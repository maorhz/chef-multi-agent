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
    "TIME": r"\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?(?:\s*[aApP][mM])?\b|\b(?:[01]?[0-9]|2[0-3])\s*[aApP][mM]\b",
    "DATE": r"\b(?:[0-9]{1,4}[-/._][0-9]{1,2}[-/._][0-9]{1,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{1,2}(?:st|nd|rd|th)?,?\s+[0-9]{4})\b",
    "DATE_TIME": r"\b(?:[0-9]{1,4}[-/._][0-9]{1,2}[-/._][0-9]{1,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{1,2}(?:st|nd|rd|th)?,?\s+[0-9]{4})\s+(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?(?:\s*[aApP][mM])?\b",
}

_DYNAMIC_REGEX_CACHE = None
_LAST_FETCH_TIME = 0
_CACHE_TIMEOUT_SECONDS = 300
_CACHED_TRANSFORM = "[redacted]"  # Cache for 5 minutes

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
        return Response(content=static_assets.get_css(), media_type="text/css")

    @app.get("/static/app.js")
    async def serve_js():
        return Response(content=static_assets.get_js(), media_type="application/javascript")

    @app.post("/evaluate")
    async def evaluate_prompt_api(request: Request):
        global _CACHED_TRANSFORM
        try:
            body = await request.json()
            text = body.get("text", "")
            if not text:
                return JSONResponse({"block": False, "deidentified_text": None, "matches": []})
            block, deidentified_text = evaluate_and_sanitize_prompt(text)
            
            matches = []
            if deidentified_text and deidentified_text != text:
                import re, difflib
                tags = re.findall(r"\[[^\]]+\]|<[^>]+>|\*+|#+", deidentified_text)
                if tags:
                    _CACHED_TRANSFORM = tags[0]
                    
                token_pattern = r"\[[^\]]+\]|<[^>]+>|\*+|#+|\w+|\s+|[^\w\s]"
                tokens_clear = re.findall(token_pattern, text)
                tokens_deid = re.findall(token_pattern, deidentified_text)
                
                matcher = difflib.SequenceMatcher(None, tokens_clear, tokens_deid, autojunk=False)
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag != 'equal':
                        clear_sub = "".join(tokens_clear[i1:i2])
                        raw_rep = "".join(tokens_deid[j1:j2])
                        if clear_sub.strip():
                            sub_tags = re.findall(r"\[[^\]]+\]|<[^>]+>|\*+|#+", raw_rep)
                            clean_rep = sub_tags[0] if sub_tags else (raw_rep.strip() if raw_rep.strip() else (_CACHED_TRANSFORM if _CACHED_TRANSFORM else "[redacted]"))
                            if not clean_rep: clean_rep = "[redacted]"
                            for chunk in clear_sub.split("\n"):
                                c_clean = chunk.strip()
                                if c_clean:
                                    matches.append({"clear": c_clean, "masked": clean_rep})
            else:
                import re
                for it_name, pattern in INFO_TYPE_REGEX_MAP.items():
                    for m in re.finditer(pattern, text):
                        clear_m = m.group(0)
                        if not any(clear_m in m_item["clear"] or m_item["clear"] in clear_m for m_item in matches):
                            matches.append({"clear": clear_m, "masked": _CACHED_TRANSFORM})
                            block = True
                            if deidentified_text is None:
                                deidentified_text = re.sub(pattern, _CACHED_TRANSFORM, text)
                        
            return JSONResponse({"block": block, "deidentified_text": deidentified_text, "matches": matches})
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
                    html = static_assets.get_html()
                    import json
                    regex_str = get_cached_masking_regex()
                    html = html.replace("MASK_REGEX_PLACEHOLDER", json.dumps(regex_str))
                    
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

            

            await self.app(scope, receive, send)

    app.add_middleware(PatchedIndexMiddleware)
    import sys
    print(f"DEBUG patched_get_fast_api_app registered routes: {[r.path for r in app.routes]}", file=sys.stderr, flush=True)
    return app

api_server.ApiServer.get_fast_api_app = patched_get_fast_api_app
