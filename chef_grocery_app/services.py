from google.cloud import modelarmor_v1
from google.api_core.client_options import ClientOptions
import logging
import time
import google.auth
from google.auth.transport.requests import AuthorizedSession

# Set up logging
logger = logging.getLogger("model_armor_services")
logger.setLevel(logging.INFO)

# Initialize Model Armor Client for us-central1 region
client_options = ClientOptions(api_endpoint="modelarmor.us-central1.rep.googleapis.com")
model_armor_client = modelarmor_v1.ModelArmorClient(client_options=client_options)
TEMPLATE_NAME = "projects/my-project-76851-371010/locations/us-central1/templates/agent-shield"

INFO_TYPE_REGEX_MAP = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "CREDIT_CARD_NUMBER": r"\b[3-6][0-9]{11,18}\b",
    "CREDIT_CARD_DATA": r"\b[3-6][0-9]{11,18}\b",
    "PHONE_NUMBER": r"\+?[0-9]{1,4}[-.\s]?[0-9]{1,10}[-.\s]?[0-9]{1,10}",
    "IP_ADDRESS": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "STREET_ADDRESS": r"\b[0-9]+\s+[a-zA-Z0-9\s,.]+?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Court|Ct)\b",
}

_DYNAMIC_REGEX_CACHE = None
_LAST_FETCH_TIME = 0
_CACHE_TIMEOUT_SECONDS = 300  # Cache for 5 minutes

def get_dynamic_masking_regex() -> str:
    """Fetches the active SDP template and returns a compiled JS-compatible regex string."""
    try:
        # Template ID for inspectTemplate configured in Model Armor Template
        inspect_template_name = "projects/my-project-76851-371010/locations/us-central1/inspectTemplates/2828347596800781685"
        
        credentials, project = google.auth.default()
        if hasattr(credentials, "quota_project_id"):
            credentials = credentials.with_quota_project("my-project-76851-371010")
            
        session = AuthorizedSession(credentials)
        url = f"https://dlp.googleapis.com/v2/{inspect_template_name}"
        res = session.get(url)
        if res.status_code == 200:
            config = res.json().get("inspectConfig", {})
            info_types = config.get("infoTypes", [])
            
            patterns = []
            for it in info_types:
                it_name = it.get("name")
                if it_name in INFO_TYPE_REGEX_MAP:
                    patterns.append(INFO_TYPE_REGEX_MAP[it_name])
                    
            custom_info_types = config.get("customInfoTypes", [])
            for cit in custom_info_types:
                regex_pattern = cit.get("regex", {}).get("pattern")
                if regex_pattern:
                    patterns.append(regex_pattern)
                    
            if patterns:
                combined = "|".join(patterns)
                return combined
    except Exception as e:
        import sys
        print(f"Error fetching dynamic masking regex: {e}", file=sys.stderr, flush=True)
    
    # Fallback to email regex if retrieval fails
    return r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def get_cached_masking_regex() -> str:
    global _DYNAMIC_REGEX_CACHE, _LAST_FETCH_TIME
    now = time.time()
    if _DYNAMIC_REGEX_CACHE is None or (now - _LAST_FETCH_TIME) > _CACHE_TIMEOUT_SECONDS:
        _DYNAMIC_REGEX_CACHE = get_dynamic_masking_regex()
        _LAST_FETCH_TIME = now
    return _DYNAMIC_REGEX_CACHE



def evaluate_and_sanitize_prompt(prompt_text: str) -> tuple[bool, str | None]:
    """Evaluates the prompt text with Model Armor.
    
    Returns:
        (block_flag, deidentified_text)
    """
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name=TEMPLATE_NAME,
        user_prompt_data=modelarmor_v1.DataItem(text=prompt_text)
    )
    response = model_armor_client.sanitize_user_prompt(request=request)
    result = response.sanitization_result

    block = False
    for filter_name in ["rai", "pi_and_jailbreak", "malicious_uris", "csam"]:
        filter_res = result.filter_results.get(filter_name)
        if filter_res:
            res_val = getattr(filter_res, f"{filter_name}_filter_result", None)
            if not res_val and filter_name == "csam":
                res_val = getattr(filter_res, "csam_filter_filter_result", None)
            if res_val and getattr(res_val, "match_state", None) == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                block = True
                break

    deidentified_text = None
    sdp_res = result.filter_results.get("sdp")
    if sdp_res and sdp_res.sdp_filter_result:
        sdp_filter_result = sdp_res.sdp_filter_result
        
        found_infotypes = set()
        if sdp_filter_result.inspect_result and sdp_filter_result.inspect_result.findings:
            found_infotypes = {finding.info_type for finding in sdp_filter_result.inspect_result.findings}
            
        deidentified_infotypes = set()
        if sdp_filter_result.deidentify_result and sdp_filter_result.deidentify_result.info_types:
            deidentified_infotypes = set(sdp_filter_result.deidentify_result.info_types)
            if sdp_filter_result.deidentify_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                deidentified_text = sdp_filter_result.deidentify_result.data.text
                
        unmasked_infotypes = found_infotypes - deidentified_infotypes
        if unmasked_infotypes:
            block = True
        elif sdp_filter_result.inspect_result and sdp_filter_result.inspect_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND and not deidentified_text:
            block = True
        elif deidentified_text is not None:
            block = True

    return block, deidentified_text


# Monkeypatch prepare_llm_agent_input in adk to sanitize workflow/node input
import google.adk.workflow._llm_agent_wrapper as wrapper
from google.genai import types

original_prepare_input = wrapper.prepare_llm_agent_input

def patched_prepare_llm_agent_input(agent, ctx, node_input):
    import sys
    print(f"DEBUG patched_prepare_llm_agent_input: agent.name={agent.name} agent.mode={agent.mode} node_input={node_input}", file=sys.stderr, flush=True)
    if node_input is not None:
        content_input = wrapper._node_input_to_content(node_input)
        prompt_text = "".join(part.text for part in content_input.parts if part.text)
        print(f"DEBUG patched_prepare_llm_agent_input resolved prompt_text: {prompt_text}", file=sys.stderr, flush=True)
        if prompt_text:
            block, deidentified_text = evaluate_and_sanitize_prompt(prompt_text)
            print(f"DEBUG patched_prepare_llm_agent_input evaluate_and_sanitize_prompt: block={block} deidentified_text={deidentified_text}", file=sys.stderr, flush=True)
            if block:
                node_input = types.Content(
                    parts=[types.Part.from_text(
                        text="[Security Alert] Your request was blocked by security filters."
                    )]
                )
            elif deidentified_text is not None:
                node_input = types.Content(
                    parts=[types.Part.from_text(text=deidentified_text)]
                )
                print(f"DEBUG patched_prepare_llm_agent_input modified node_input to: {node_input}", file=sys.stderr, flush=True)
    return original_prepare_input(agent, ctx, node_input)

wrapper.prepare_llm_agent_input = patched_prepare_llm_agent_input


# Monkeypatch FastAPI app generation to inject the local buffer JS client layer
import google.adk.cli.api_server as api_server
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
import os

original_get_app = api_server.ApiServer.get_fast_api_app

def patched_get_fast_api_app(self, *args, **kwargs):
    # Try to resolve web_assets_dir
    web_assets_dir = kwargs.get("web_assets_dir")
    if not web_assets_dir and len(args) >= 3:
        web_assets_dir = args[2]
    if not web_assets_dir:
        import google.adk.cli.fast_api as fast_api_module
        BASE_DIR = os.path.dirname(fast_api_module.__file__)
        web_assets_dir = os.path.join(BASE_DIR, "browser")

    app = original_get_app(self, *args, **kwargs)

    # Import embedded static assets and FastAPI Response
    from fastapi.responses import Response
    try:
        import chef_grocery_app.static_assets as static_assets
    except ImportError:
        import static_assets

    @app.get("/static/styles.css")
    async def serve_css():
        return Response(content=static_assets.CSS_CONTENT, media_type="text/css")

    @app.get("/static/app.js")
    async def serve_js():
        return Response(content=static_assets.JS_CONTENT, media_type="application/javascript")

    @app.post("/evaluate")
    async def evaluate_prompt_api(request: Request):
        try:
            body = await request.json()
            text = body.get("text", "")
            if not text:
                return JSONResponse({"block": False, "deidentified_text": None})
            block, deidentified_text = evaluate_and_sanitize_prompt(text)
            return JSONResponse({"block": block, "deidentified_text": deidentified_text})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/log")
    async def log_client_message(request: Request):
        try:
            body = await request.json()
            message = body.get("message", "")
            print(f"[BROWSER LOG] {message}", flush=True)
            return JSONResponse({"status": "ok"})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # Serve patched index.html via raw ASGI middleware
    class PatchedIndexMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return

            path = scope.get("path", "")
            
            # 1. Direct Interception for Custom UI Root Page
            if path == "/" or path == "/index.html":
                import sys
                print(f"DEBUG middleware: Intercepting root path to serve custom gourmet UI from static_assets!", file=sys.stderr, flush=True)
                try:
                    html = static_assets.HTML_CONTENT
                    regex_str = get_cached_masking_regex()
                    html = html.replace("MASK_REGEX_PLACEHOLDER", "/" + regex_str + "/g")
                    
                    html_bytes = html.encode("utf-8")
                    headers = [
                        (b"content-type", b"text/html; charset=utf-8"),
                        (b"content-length", str(len(html_bytes)).encode("utf-8"))
                    ]
                    
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": headers
                    })
                    await send({
                        "type": "http.response.body",
                        "body": html_bytes,
                        "more_body": False
                    })
                    return
                except Exception as e:
                    print(f"Error serving custom UI: {e}", file=sys.stderr, flush=True)
                    await self.app(scope, receive, send)
                    return

            # 2. Intercept Dev UI to inject prompt shielding
            if "dev-ui" in path or path.endswith("index.html"):
                import sys
                is_html = None
                response_status = None
                response_headers = []
                response_body = b""

                async def mock_send(message):
                    nonlocal is_html, response_status, response_headers, response_body
                    if message["type"] == "http.response.start":
                        response_status = message["status"]
                        response_headers = message["headers"]
                        
                        content_type = ""
                        for k, v in response_headers:
                            if k.lower() == b"content-type":
                                content_type = v.decode("utf-8")
                                break
                        is_html = (response_status == 200 and "text/html" in content_type)
                        print(f"DEBUG middleware: path={path} status={response_status} is_html={is_html}", file=sys.stderr, flush=True)
                        if not is_html:
                            await send(message)
                    elif message["type"] == "http.response.body":
                        if not is_html:
                            await send(message)
                            return
                        
                        response_body += message.get("body", b"")
                        if not message.get("more_body", False):
                            print(f"DEBUG middleware: Injecting script tag into HTML response!", file=sys.stderr, flush=True)
                            html = response_body.decode("utf-8")
                            js_code = """
                            <script>
                            (function() {
                              console.log("Local buffer layer active!");
                              const MASK_REGEX = MASK_REGEX_PLACEHOLDER;
                              const maskedTexts = new Map();

                              function remoteLog(msg) {
                                fetch("/api/log", {
                                  method: "POST",
                                  headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ message: msg })
                                }).catch(() => {});
                              }

                              // 1. Intercept XMLHttpRequest
                               const originalOpen = XMLHttpRequest.prototype.open;
                               const originalSend = XMLHttpRequest.prototype.send;

                               XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                                 this._url = (url && url.toString) ? url.toString() : url;
                                 this._method = (method && method.toString) ? method.toString().toUpperCase() : method;
                                 console.log("[Local Buffer DEBUG] XHR open: method=" + this._method + " url=" + this._url);
                                 return originalOpen.apply(this, arguments);
                               };

                               XMLHttpRequest.prototype.send = function(body) {
                                 console.log("[Local Buffer DEBUG] XHR send: url=" + this._url + " method=" + this._method + " body=" + (body ? body.substring(0, 100) : "null"));
                                 if (this._url && this._url.includes("/run_sse") && this._method === "POST" && body) {
                                   console.log("[Local Buffer DEBUG] XHR matched /run_sse!");
                                   try {
                                     const bodyObj = JSON.parse(body);
                                     const newMessage = bodyObj.newMessage || bodyObj.new_message;
                                     if (newMessage && newMessage.parts) {
                                       const originalPrompt = newMessage.parts.map(p => p.text || "").join("");
                                       console.log("[Local Buffer DEBUG] XHR prompt text: " + originalPrompt);
                                       if (originalPrompt) {
                                         remoteLog("[XHR client] prompt intercepted: " + originalPrompt);
                                         // 1. Optimistic client-side masking
                                         const allEmails = originalPrompt.match(MASK_REGEX) || [];
                                         allEmails.forEach(email => {
                                           const emailMasked = "#".repeat(email.length);
                                           maskedTexts.set(email, emailMasked);
                                         });
                                         remoteLog("[XHR client] Optimistic allEmails matched: " + JSON.stringify(allEmails) + " map: " + JSON.stringify(Array.from(maskedTexts.entries())));
                                         if (allEmails.length > 0) {
                                           maskElements(document.body);
                                         }

                                         // Synchronous call to /api/evaluate to intercept
                                         const xhr = new XMLHttpRequest();
                                         originalOpen.call(xhr, "POST", "/evaluate", false);
                                         xhr.setRequestHeader("Content-Type", "application/json");
                                         originalSend.call(xhr, JSON.stringify({ text: originalPrompt }));
                                         console.log("[Local Buffer DEBUG] /api/evaluate synchronous response status: " + xhr.status);

                                         if (xhr.status === 200) {
                                           const evalResult = JSON.parse(xhr.responseText);
                                           console.log("[Local Buffer DEBUG] /api/evaluate result: " + JSON.stringify(evalResult));
                                           remoteLog("[XHR client] evaluate result: " + JSON.stringify(evalResult));
                                           
                                           // 2. Adjust mappings based on backend evaluation
                                           if (evalResult.deidentified_text) {
                                             const masked = evalResult.deidentified_text;
                                             maskedTexts.set(originalPrompt, masked);
                                             
                                             allEmails.forEach(email => {
                                               if (masked.includes(email)) {
                                                 maskedTexts.delete(email);
                                               } else {
                                                 const emailMasked = "#".repeat(email.length);
                                                 maskedTexts.set(email, emailMasked);
                                               }
                                             });
                                             remoteLog("[XHR client] adjusted map: " + JSON.stringify(Array.from(maskedTexts.entries())));
                                           } else {
                                             allEmails.forEach(email => {
                                               maskedTexts.delete(email);
                                             });
                                           }

                                           // Re-evaluate DOM elements to restore excluded ones
                                           maskElements(document.body);

                                           // Re-construct the body parts using finalized mappings
                                           if (evalResult.deidentified_text && !evalResult.block) {
                                          newMessage.parts.forEach(part => {
                                             if (part.text) {
                                               let updatedText = part.text;
                                               const sortedEntries = Array.from(maskedTexts.entries()).sort((a, b) => b[0].length - a[0].length);
                                               for (const [raw, msk] of sortedEntries) {
                                                 if (raw && updatedText.includes(raw)) {
                                                   updatedText = updatedText.replaceAll(raw, msk);
                                                 }
                                               }
                                               part.text = updatedText;
                                             }
                                           });
                                           body = JSON.stringify(bodyObj);
                                           console.log("[Local Buffer DEBUG] XHR request body patched successfully!");
                                           }
                                         }
                                       }
                                     }
                                   } catch (e) {
                                     console.error("[Local Buffer DEBUG] XHR evaluation error:", e);
                                   }
                                 }
                                 return originalSend.call(this, body);
                               };

                               // 2. Intercept fetch
                               const originalFetch = window.fetch;
                               window.fetch = async function(resource, options) {
                                 let url = "";
                                 let method = "GET";
                                 let bodyText = "";

                                 if (resource instanceof Request) {
                                   url = resource.url;
                                   method = resource.method;
                                   try {
                                     const cloned = resource.clone();
                                     bodyText = await cloned.text();
                                   } catch (e) {
                                     console.error("[Local Buffer DEBUG] Error reading request body:", e);
                                   }
                                 } else if (resource instanceof URL) {
                                   url = resource.href;
                                   if (options) {
                                     method = options.method || "GET";
                                     bodyText = options.body || "";
                                   }
                                 } else if (typeof resource === 'string') {
                                   url = resource;
                                   if (options) {
                                     method = options.method || "GET";
                                     bodyText = options.body || "";
                                   }
                                 }

                                 method = method.toUpperCase();
                                 console.log("[Local Buffer DEBUG] fetch call: url=" + url + " method=" + method + " body=" + (bodyText ? bodyText.substring(0, 100) : "null"));

                                 if (url && url.includes("/run_sse") && method === "POST" && bodyText) {
                                   console.log("[Local Buffer DEBUG] fetch matched /run_sse!");
                                   try {
                                     const bodyObj = JSON.parse(bodyText);
                                     const newMessage = bodyObj.newMessage || bodyObj.new_message;
                                     if (newMessage && newMessage.parts) {
                                       const originalPrompt = newMessage.parts.map(p => p.text || "").join("");
                                       console.log("[Local Buffer DEBUG] fetch prompt text: " + originalPrompt);
                                       if (originalPrompt) {
                                         remoteLog("[Fetch client] prompt intercepted: " + originalPrompt);
                                         // 1. Optimistic client-side masking
                                         const allEmails = originalPrompt.match(MASK_REGEX) || [];
                                         allEmails.forEach(email => {
                                           const emailMasked = "#".repeat(email.length);
                                           maskedTexts.set(email, emailMasked);
                                         });
                                         remoteLog("[Fetch client] Optimistic allEmails matched: " + JSON.stringify(allEmails) + " map: " + JSON.stringify(Array.from(maskedTexts.entries())));
                                         if (allEmails.length > 0) {
                                           maskElements(document.body);
                                         }

                                         const evalResponse = await originalFetch("/evaluate", {
                                           method: "POST",
                                           headers: { "Content-Type": "application/json" },
                                           body: JSON.stringify({ text: originalPrompt })
                                         });
                                         const evalResult = await evalResponse.json();
                                         console.log("[Local Buffer DEBUG] fetch /api/evaluate result: " + JSON.stringify(evalResult));
                                         remoteLog("[Fetch client] evaluate result: " + JSON.stringify(evalResult));
                                         
                                         // 2. Adjust mappings based on backend evaluation
                                         if (evalResult.deidentified_text) {
                                           const masked = evalResult.deidentified_text;
                                           maskedTexts.set(originalPrompt, masked);
                                           
                                           allEmails.forEach(email => {
                                             if (masked.includes(email)) {
                                               maskedTexts.delete(email);
                                             } else {
                                               const emailMasked = "#".repeat(email.length);
                                               maskedTexts.set(email, emailMasked);
                                             }
                                           });
                                           remoteLog("[Fetch client] adjusted map: " + JSON.stringify(Array.from(maskedTexts.entries())));
                                         } else {
                                           allEmails.forEach(email => {
                                             maskedTexts.delete(email);
                                           });
                                         }

                                         // Re-evaluate DOM elements to restore excluded ones
                                         maskElements(document.body);

                                         if (evalResult.deidentified_text && !evalResult.block) {
                                         newMessage.parts.forEach(part => {
                                           if (part.text) {
                                             let updatedText = part.text;
                                             const sortedEntries = Array.from(maskedTexts.entries()).sort((a, b) => b[0].length - a[0].length);
                                             for (const [raw, msk] of sortedEntries) {
                                               if (raw && updatedText.includes(raw)) {
                                                 updatedText = updatedText.replaceAll(raw, msk);
                                               }
                                             }
                                             part.text = updatedText;
                                           }
                                         });
                                         
                                         if (resource instanceof Request) {
                                           const newHeaders = new Headers(resource.headers);
                                           resource = new Request(resource.url, {
                                             method: resource.method,
                                             headers: newHeaders,
                                             body: JSON.stringify(bodyObj),
                                             mode: resource.mode,
                                             credentials: resource.credentials,
                                             cache: resource.cache,
                                             redirect: resource.redirect,
                                             referrer: resource.referrer,
                                             integrity: resource.integrity,
                                             keepalive: resource.keepalive,
                                             signal: resource.signal
                                           });
                                         } else if (options) {
                                           options.body = JSON.stringify(bodyObj);
                                         }
                                         console.log("[Local Buffer DEBUG] fetch request body patched successfully!");
                                            }
                                        }
                                      }
                                   } catch (e) {
                                     console.error("[Local Buffer DEBUG] fetch evaluation error:", e);
                                     remoteLog("[Fetch client] fetch evaluation error: " + (e.stack || e.message));
                                   }
                                 }
                                 return originalFetch.call(this, resource, options);
                               };

                               // 3. MutationObserver
                               const observer = new MutationObserver((mutations) => {
                                 for (const mutation of mutations) {
                                   if (mutation.type === "childList") {
                                     for (const node of mutation.addedNodes) {
                                       if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) {
                                         maskElements(node);
                                       }
                                     }
                                   } else if (mutation.type === "characterData") {
                                     maskElements(mutation.target);
                                   }
                                 }
                               });

                               function maskElements(element) {
                                 if (element.nodeType === Node.TEXT_NODE) {
                                   if (element._originalValue === undefined) {
                                     element._originalValue = element.nodeValue;
                                   }
                                   let val = element._originalValue;
                                   remoteLog("[DOM client] maskElements TEXT_NODE: '" + val + "'");
                                   let changed = false;
                                   
                                   // 1. Try substring mapping against any full prompt deidentified_text in map
                                   for (const [raw, masked] of maskedTexts.entries()) {
                                     if (raw && raw.length > 50 && masked && masked.length === raw.length) {
                                       // Normalize non-breaking spaces in both lookup value and full prompt
                                       const normalizedVal = val.replace(/\u00a0/g, " ");
                                       const normalizedPrompt = raw.replace(/\u00a0/g, " ");
                                       const startIdx = normalizedPrompt.indexOf(normalizedVal);
                                       if (startIdx !== -1) {
                                         const maskedVal = masked.substring(startIdx, startIdx + val.length);
                                         // Preserve non-breaking spaces from original DOM value
                                         let finalVal = "";
                                         for (let i = 0; i < val.length; i++) {
                                           if (val[i] === "\u00a0" && maskedVal[i] === " ") {
                                             finalVal += "\u00a0";
                                           } else {
                                             finalVal += maskedVal[i];
                                           }
                                         }
                                         if (finalVal !== val) {
                                           remoteLog("[DOM client] found substring match in full prompt offset: " + startIdx + ", replacing: '" + val + "' with: '" + finalVal + "'");
                                           val = finalVal;
                                           changed = true;
                                           break;
                                         }
                                       }
                                     }
                                   }
                                   
                                   // 2. Fall back to individual replacements in Map
                                   if (!changed) {
                                     const sortedEntries = Array.from(maskedTexts.entries()).sort((a, b) => b[0].length - a[0].length);
                                     for (const [raw, masked] of sortedEntries) {
                                       if (raw && val.includes(raw)) {
                                         remoteLog("[DOM client] found individual match for raw: '" + raw + "', replacing with: '" + masked + "'");
                                         val = val.replaceAll(raw, masked);
                                         changed = true;
                                       }
                                     }
                                   }
                                   if (element.nodeValue !== val) {
                                     remoteLog("[DOM client] nodeValue updated to: '" + val + "'");
                                     observer.disconnect();
                                     element.nodeValue = val;
                                     observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                                   }
                                 } else if (element.nodeType === Node.ELEMENT_NODE) {
                                   if (element.tagName === "SCRIPT" || element.tagName === "STYLE") return;
                                   for (const child of element.childNodes) {
                                     maskElements(child);
                                   }
                                 }
                               }

                              function startObserver() {
                                if (!document.body) {
                                  console.warn("[Local Buffer DEBUG] document.body not ready yet, retrying...");
                                  setTimeout(startObserver, 50);
                                  return;
                                }
                                observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                                maskElements(document.body);
                                console.log("[Local Buffer DEBUG] MutationObserver started successfully!");
                              }

                              if (document.readyState === "loading") {
                                document.addEventListener("DOMContentLoaded", startObserver);
                              } else {
                                startObserver();
                              }
                            })();
                            </script>
                            """
                            regex_str = get_cached_masking_regex()
                            patched_js = js_code.replace("MASK_REGEX_PLACEHOLDER", "/" + regex_str + "/g")
                            patched_html = html.replace("</head>", patched_js + "</head>")
                            patched_bytes = patched_html.encode("utf-8")
                            
                            new_headers = []
                            for k, v in response_headers:
                                if k.lower() == b"content-length":
                                    new_headers.append((k, str(len(patched_bytes)).encode()))
                                else:
                                    new_headers.append((k, v))
                            
                            await send({
                                "type": "http.response.start",
                                "status": response_status,
                                "headers": new_headers
                            })
                            await send({
                                "type": "http.response.body",
                                "body": patched_bytes,
                                "more_body": False
                            })

                await self.app(scope, receive, mock_send)
                return

            await self.app(scope, receive, send)

    app.add_middleware(PatchedIndexMiddleware)
    import sys
    print(f"DEBUG patched_get_fast_api_app registered routes: {[r.path for r in app.routes]}", file=sys.stderr, flush=True)
    return app

api_server.ApiServer.get_fast_api_app = patched_get_fast_api_app
