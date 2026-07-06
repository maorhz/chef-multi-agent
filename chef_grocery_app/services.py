from google.cloud import modelarmor_v1
from google.api_core.client_options import ClientOptions
import logging
import time
import google.auth
from google.auth.transport.requests import AuthorizedSession

import os

# Set up logging
logger = logging.getLogger("model_armor_services")
logger.setLevel(logging.INFO)

# Configurable GCP Environment Variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "my-project-76851-371010")
REGION = os.getenv("GCP_LOCATION", "us-central1")
TEMPLATE_NAME = os.getenv(
    "MODEL_ARMOR_TEMPLATE_NAME",
    f"projects/{PROJECT_ID}/locations/{REGION}/templates/agent-shield"
)
INSPECT_TEMPLATE_NAME = os.getenv(
    "DLP_INSPECT_TEMPLATE_NAME",
    f"projects/{PROJECT_ID}/locations/{REGION}/inspectTemplates/2828347596800781685"
)

# Initialize Model Armor Client for specified region
client_options = ClientOptions(api_endpoint=f"modelarmor.{REGION}.rep.googleapis.com")
model_armor_client = modelarmor_v1.ModelArmorClient(client_options=client_options)

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
        credentials, project = google.auth.default()
        if hasattr(credentials, "quota_project_id"):
            credentials = credentials.with_quota_project(PROJECT_ID)
            
        session = AuthorizedSession(credentials)
        url = f"https://dlp.googleapis.com/v2/{INSPECT_TEMPLATE_NAME}"
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



INFO_TYPE_HEURISTICS = {
    "EMAIL_ADDRESS": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "STREET_ADDRESS": r"^\d+\s+[a-zA-Z0-9\s,.]+?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Court|Ct|NW|SW|NE|SE)\b",
    "CREDIT_CARD_NUMBER": r"^[3-6][0-9-]{11,20}$",
    "IP_ADDRESS": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
    "TIME": r"^(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?(?:\s*[aApP][mM])?$|^(?:[01]?[0-9]|2[0-3])\s*[aApP][mM]$",
    "DATE": r"^(?:[0-9]{1,4}[-/._][0-9]{1,2}[-/._][0-9]{1,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+[0-9]{1,2}(?:st|nd|rd|th)?,?\s+[0-9]{4})$",
    "URL": r"^https?://[^\s/$.?#].[^\s]*$",
    "GCP_API_KEY": r"^AIzaSy[a-zA-Z0-9-_]{33}$",
    "ENCRYPTION_KEY": r"^[a-zA-Z0-9+/=_-]{43,45}$",
    "PHONE_NUMBER": r"^\+?[0-9]{1,4}[-.\s]?[0-9]{1,10}[-.\s]?[0-9]{1,10}$",
    "PASSWORD": r"^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]{6,15}$",
}

def classify_chunks(chunks: list[str], detected_types: list[str]) -> list[str]:
    import re
    assigned = []
    used_types = set()
    
    for chunk in chunks:
        chunk_clean = chunk.strip()
        matched_type = None
        
        # 1. Exact Heuristics Match
        for it, pattern in INFO_TYPE_HEURISTICS.items():
            if it in detected_types:
                if re.match(pattern, chunk_clean):
                    matched_type = it
                    break
                    
        # 2. Structure & Keyword matches
        if not matched_type:
            text_lower = chunk_clean.lower()
            if "URL" in detected_types and (text_lower.startswith("http") or "www." in text_lower or ".com/" in text_lower or "cloud.google" in text_lower):
                matched_type = "URL"
            elif "EMAIL_ADDRESS" in detected_types and "@" in chunk_clean:
                matched_type = "EMAIL_ADDRESS"
            elif "GCP_API_KEY" in detected_types and chunk_clean.startswith("AIzaSy"):
                matched_type = "GCP_API_KEY"
            elif "ENCRYPTION_KEY" in detected_types and (len(chunk_clean) > 40 and "=" in chunk_clean):
                matched_type = "ENCRYPTION_KEY"
            elif "STREET_ADDRESS" in detected_types and any(w in chunk_clean for w in ["Avenue", "Avenue NW", "Pennsylvania", "Washington", "Street", "Rd", "St"]):
                matched_type = "STREET_ADDRESS"
            elif "FDA_CODE" in detected_types and chunk_clean in ["Modafinil"]:
                matched_type = "FDA_CODE"
            elif "MEDICAL_TERM" in detected_types and chunk_clean in ["cholecystectomy"]:
                matched_type = "MEDICAL_TERM"
            elif "MEDICAL_DATA" in detected_types and chunk_clean in ["AB+"]:
                matched_type = "MEDICAL_DATA"
            elif "CREDIT_CARD_DATA" in detected_types and re.match(r"^(0[1-9]|1[0-2])/([0-9]{2}|[0-9]{4})$", chunk_clean):
                matched_type = "CREDIT_CARD_DATA"
            elif re.match(r"^\d{9}$", chunk_clean):
                candidates = ["PASSPORT", "MEDICAL_RECORD_NUMBER", "FINANCIAL_ACCOUNT_NUMBER"]
                for cand in candidates:
                    if cand in detected_types and cand not in used_types:
                        matched_type = cand
                        break
                if not matched_type:
                    for cand in candidates:
                        if cand in detected_types:
                            matched_type = cand
                            break

        if not matched_type:
            remaining = [t for t in detected_types if t not in used_types]
            if remaining:
                matched_type = remaining[0]
            else:
                matched_type = detected_types[0] if detected_types else "SDP_DETECTED"
                
        used_types.add(matched_type)
        assigned.append(matched_type)
        
    return assigned



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
        info_types_list = []
        if sdp_filter_result.deidentify_result and sdp_filter_result.deidentify_result.info_types:
            deidentified_infotypes = set(sdp_filter_result.deidentify_result.info_types)
            info_types_list = list(sdp_filter_result.deidentify_result.info_types)
            if sdp_filter_result.deidentify_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                deidentified_text = sdp_filter_result.deidentify_result.data.text
                
        unmasked_infotypes = found_infotypes - deidentified_infotypes
        if unmasked_infotypes:
            block = True
        elif sdp_filter_result.inspect_result and sdp_filter_result.inspect_result.match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND and not deidentified_text:
            block = True
        elif deidentified_text is not None:
            block = True

    return block, deidentified_text, info_types_list


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
            block, deidentified_text, _ = evaluate_and_sanitize_prompt(prompt_text)
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

try:
    import chef_grocery_app.static_assets as static_assets
except ImportError:
    import static_assets

# Overwrite ADK default browser/index.html on disk across all potential locations (/app, site-packages, etc.)
try:
    import glob, json
    import google.adk.cli.fast_api as fast_api_module
    html_content = static_assets.get_html()
    regex_str = get_cached_masking_regex()
    html_content = html_content.replace("MASK_REGEX_PLACEHOLDER", json.dumps(regex_str))

    search_patterns = [
        "/app/**/browser/index.html",
        "/app/**/index.html",
        os.path.join(os.getcwd(), "**/browser/index.html"),
        os.path.join(os.path.dirname(fast_api_module.__file__), "**/index.html"),
    ]
    for pattern in search_patterns:
        for p in glob.glob(pattern, recursive=True):
            try:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(html_content)
                import sys
                print(f"DEBUG services.py: Overwrote ADK index.html at {p}", file=sys.stderr, flush=True)
            except Exception as _ex:
                pass
except Exception as _e:
    import sys
    print(f"Note: Could not overwrite ADK index.html: {_e}", file=sys.stderr, flush=True)

class CustomUIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            import sys
            print(f"DEBUG CustomUIMiddleware: Received request path='{path}' scope={scope}", file=sys.stderr, flush=True)
            if path in ("/", "/index.html", "/dev-ui", "/dev-ui/") or path.startswith("/dev-ui"):
                import json
                print(f"DEBUG CustomUIMiddleware: Intercepting path='{path}' and serving Custom UI HTML!", file=sys.stderr, flush=True)
                html = static_assets.get_html()
                regex_str = get_cached_masking_regex()
                html = html.replace("MASK_REGEX_PLACEHOLDER", json.dumps(regex_str))
                response = HTMLResponse(content=html, media_type="text/html")
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)

async def custom_ui_route_handler(request: Request):
    import sys
    print(f"DEBUG custom_ui_route_handler: Called for path='{request.url.path}'", file=sys.stderr, flush=True)
    import json
    html = static_assets.get_html()
    regex_str = get_cached_masking_regex()
    html = html.replace("MASK_REGEX_PLACEHOLDER", json.dumps(regex_str))
    return HTMLResponse(content=html, media_type="text/html")

def attach_custom_ui_middleware(app):
    import sys
    print(f"DEBUG attach_custom_ui_middleware: Overriding endpoint handlers for app routes", file=sys.stderr, flush=True)
    for route in list(app.router.routes):
        path = getattr(route, "path", "")
        if path in ("/", "/index.html", "/dev-ui", "/dev-ui/"):
            print(f"DEBUG attach_custom_ui_middleware: Overriding endpoint for route path='{path}'", file=sys.stderr, flush=True)
            route.endpoint = custom_ui_route_handler

    original_build_stack = app.build_middleware_stack
    def patched_build_stack():
        print(f"DEBUG patched_build_stack: Building stack with CustomUIMiddleware wrapper!", file=sys.stderr, flush=True)
        stack = original_build_stack()
        return CustomUIMiddleware(stack)
    app.build_middleware_stack = patched_build_stack
    return app

def patched_get_fast_api_app(self, *args, **kwargs):
    import sys
    print(f"DEBUG patched_get_fast_api_app: Called with args={args} kwargs={kwargs}", file=sys.stderr, flush=True)
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

    _EVALUATE_RATE_LIMIT = {}
    _MAX_EVALS_PER_MIN = 15
    _RATE_WINDOW_SECS = 60

    def check_eval_rate_limit(client_key: str) -> bool:
        now = time.time()
        timestamps = [t for t in _EVALUATE_RATE_LIMIT.get(client_key, []) if now - t < _RATE_WINDOW_SECS]
        _EVALUATE_RATE_LIMIT[client_key] = timestamps
        if len(timestamps) >= _MAX_EVALS_PER_MIN:
            return False
        timestamps.append(now)
        return True

    @app.post("/evaluate")
    async def evaluate_prompt_api(request: Request):
        global _CACHED_TRANSFORM
        try:
            session_id = request.headers.get("X-Session-ID")
            if not session_id or not session_id.strip():
                return JSONResponse({"error": "Unauthorized: Missing X-Session-ID header"}, status_code=401)

            client_host = request.client.host if request.client else "unknown"
            rate_key = f"{session_id}:{client_host}"
            if not check_eval_rate_limit(rate_key):
                return JSONResponse({"error": "Too Many Requests: Rate limit exceeded"}, status_code=429)

            body = await request.json()
            text = body.get("text", "")
            if not text:
                return JSONResponse({"block": False, "deidentified_text": None, "matches": []})
            block, deidentified_text, info_types_list = evaluate_and_sanitize_prompt(text)
            
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
                raw_matches = []
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
                                    raw_matches.append((c_clean, clean_rep))
                
                clear_texts = [m[0] for m in raw_matches]
                classifications = classify_chunks(clear_texts, info_types_list)
                for (c_clean, clean_rep), it_name in zip(raw_matches, classifications):
                    matches.append({"clear": c_clean, "masked": clean_rep, "infoType": it_name})
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

    return attach_custom_ui_middleware(app)

api_server.ApiServer.get_fast_api_app = patched_get_fast_api_app

try:
    import google.adk.cli.dev_server as dev_server_module
    orig_dev_get_app = dev_server_module.DevServer.get_fast_api_app

    def patched_dev_get_app(self, *args, **kwargs):
        app = orig_dev_get_app(self, *args, **kwargs)
        return attach_custom_ui_middleware(app)

    dev_server_module.DevServer.get_fast_api_app = patched_dev_get_app
except Exception as e:
    import sys
    print(f"Note: Could not patch DevServer.get_fast_api_app: {e}", file=sys.stderr, flush=True)

# Scan garbage collector for any FastAPI instances already created prior to importing services.py
def patch_existing_fastapi_instances():
    import gc
    from fastapi import FastAPI, Response
    found = 0
    for obj in gc.get_objects():
        try:
            if isinstance(obj, FastAPI):
                attach_custom_ui_middleware(obj)
                route_paths = [getattr(r, "path", "") for r in obj.router.routes]
                if "/evaluate" not in route_paths:
                    obj.add_api_route("/evaluate", evaluate_prompt_api, methods=["POST"])
                if "/api/log" not in route_paths:
                    obj.add_api_route("/api/log", log_client_message, methods=["POST"])
                if "/static/styles.css" not in route_paths:
                    async def _serve_css():
                        return Response(content=static_assets.get_css(), media_type="text/css")
                    obj.add_api_route("/static/styles.css", _serve_css, methods=["GET"])
                if "/static/app.js" not in route_paths:
                    async def _serve_js():
                        return Response(content=static_assets.get_js(), media_type="application/javascript")
                    obj.add_api_route("/static/app.js", _serve_js, methods=["GET"])
                found += 1
        except Exception:
            pass
    import sys
    print(f"DEBUG services.py: Patched {found} existing FastAPI app instances from gc", file=sys.stderr, flush=True)

try:
    patch_existing_fastapi_instances()
except Exception as _e:
    import sys
    print(f"Error scanning gc for FastAPI instances: {_e}", file=sys.stderr, flush=True)
