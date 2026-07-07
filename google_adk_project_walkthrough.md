# Walkthrough: Smart Chef & Grocery Assistant (Google ADK)

This document serves as the unified project walkthrough and documentation for the **Smart Chef & Grocery Assistant**, built using the **Google Agent Development Kit (ADK)** in Python.

---

## 🌟 1. Project Concept
The application takes a user's food craving, ingredients on hand, or diet preferences, and performs two sequential tasks:
1. **Recipe Creation**: Designs a customized, detailed recipe using Gemini.
2. **Grocery Planning**: Analyzes the recipe to output a clean, categorized shopping list (excluding ingredients the user already has) and an estimated nutritional breakdown.

---

## 🛠️ 2. Project Setup & Directory
All files are organized in the following local directory:
`/usr/local/google/home/maorhz/Documents/Code/chef-multi-agent`

### Setup Steps:
1. **Virtual Environment**:
   ```bash
   python3.11 -m venv venv --without-pip
   source venv/bin/activate
   ```
2. **Pip Installation** (due to system-level staging repository overrides):
   ```bash
   curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
   python get-pip.py --index-url https://pypi.org/simple
   rm get-pip.py
   ```
3. **Google ADK Library**:
   ```bash
   pip install google-adk --index-url https://pypi.org/simple
   ```

---

## ⚙️ 3. Application Optimization Journey

### Phase 1: Multi-Agent Workflow (Initial Design)
We initially designed the system with two separate agents (`chef_agent` and `grocery_agent`) executing in sequence within a `Workflow` graph.

While functional, this triggered a **System Instruction Performance Alert** in the ADK Developer UI. Swapping the system instructions (`You are an expert chef...` to `You are a shopping coordinator...`) between consecutive turns in the same session invalidated Gemini's **context caching**, resulting in cache misses and increased response latency.

### Phase 2: Single-Agent Consolidation (Optimized Caching)
To maximize caching efficiency, we consolidated both personas into a single, unified agent (`chef_and_grocery_agent`) that executed the tasks sequentially in a single turn. This resolved context cache invalidation warnings.

### Phase 3: Multi-Agent Restoration (Security Guardrails & Vertex AI platform)
To support robust **Model Armor Input Shielding**, we restored the multi-agent layout containing the separate agents `chef_agent` and `grocery_agent` wrapped in a custom `@node` wrapper (`run_chef`).
* By using a custom node wrapper with conditional routing (`ctx.route = "continue"`), we cleanly halt the workflow output downstream without duplicate messages if a security filter is triggered.
* To optimize caching in the multi-agent setup, we run reasoning on a managed **Vertex AI Agent Engine** execution graph, maintaining caching and session persistence natively.

#### Final Agent Code (`chef_grocery_app/agent.py`):
```python
from google.adk import Agent
from google.adk.workflow import Workflow, START, node
# ... imports ...

chef_agent = Agent(
    name="chef_agent",
    model="gemini-2.5-flash",
    instruction="You are an expert culinary assistant..."
)

grocery_agent = Agent(
    name="grocery_agent",
    model="gemini-2.5-flash",
    instruction="You are a grocery shopping coordinator..."
)

# Wrapper node for safety checks and routing
@node(rerun_on_resume=True)
async def run_chef(ctx, inp):
    res = await ctx.run_node(chef_agent, inp, use_as_output=True)
    if res is None:  # Blocked by Model Armor
        return None
    ctx.route = "continue"
    return res

chef_grocery_workflow = Workflow(
    name="chef_grocery_workflow",
    edges=[
        (START, run_chef),
        (run_chef, {
            "continue": grocery_agent
        })
    ]
)

root_agent = chef_grocery_workflow
```

---

## 🖥️ 4. Local CLI Execution (RTL/Hebrew Formatting)
To interact with the agent locally in your terminal, we created a custom runner script `run.py`. 

Because modern terminal emulators already support Right-to-Left (RTL) rendering, we output the raw logical text stream directly without visual formatting libraries (which would otherwise invert the characters).

#### CLI Runner (`run.py`):
```python
import asyncio
import os
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from chef_grocery_app.agent import root_agent

# Load environment configuration
dotenv_path = os.path.join(os.path.dirname(__file__), 'chef_grocery_app', '.env')
load_dotenv(dotenv_path)

def print_friendly_event(event) -> None:
    if not event.content or not event.content.parts:
        return
    text_buffer = [part.text for part in event.content.parts if part.text]
    if text_buffer:
        print(f"{event.author} > {''.join(text_buffer)}")

async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="chef_grocery_app")
    
    # Query Mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Running single query: {query}\n")
        events = await runner.run_debug(query, quiet=True)
        for event in events:
            print_friendly_event(event)
        return

    # Interactive CLI Mode
    print("=== Chef & Grocery Agent (CLI Mode) ===")
    print("Type 'exit' or 'quit' to end the session.\n")
    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue
            events = await runner.run_debug(user_input, quiet=True)
            print("\nAgent:")
            for event in events:
                print_friendly_event(event)
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ☁️ 5. Platform Hosting: Cloud Run UI Gateway & Vertex AI Agent Engine

We deployed a hybrid hosting model to keep custom DNS routing (`chef.gmandiant.com`) active while running the agents on Vertex AI Agent Engine:

### 1. Cloud Run UI Gateway
Acts as the public frontend and routing gateway. It serves the custom gourmet UI, handles rate limits, runs `/evaluate` security filters, and forwards agent execution queries to Vertex AI.

* **Deployment Command**:
  ```bash
  adk deploy cloud_run --project=my-project-76851-371010 --region=us-central1 --with_ui chef_grocery_app
  ```

### 2. Vertex AI Agent Engine (Agent Platform)
Executes the ADK multi-agent graph as a managed Reasoning Engine.

* **Engine ID**: `3906571960313708544`
* **Agent Engine Deployment Script**:
  ```python
  from google.cloud import aiplatform
  from google.adk.deploy import deploy_to_agent_engine
  from chef_grocery_app.agent import root_agent

  aiplatform.init(project="my-project-76851-371010", location="us-central1")

  remote_agent = deploy_to_agent_engine(
      agent=root_agent,
      display_name="Chef & Grocery Multi-Agent System",
      requirements=["google-adk", "google-cloud-modelarmor", "google-cloud-dlp"]
  )
  ```

### IAM Vertex AI User Permission Binding
To allow the Cloud Run backend to invoke the Reasoning Engine on the Agent Platform, we granted the **Vertex AI User** (`roles/aiplatform.user`) role to the Cloud Run Service Account:
```bash
gcloud projects add-iam-policy-binding my-project-76851-371010 \
  --member="serviceAccount:855384940829-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Restricting Access & Authenticating Users (IAM Invoker)
To prevent unauthorized public access, we removed `allUsers` permissions and restricted access to authorized team accounts:

1. **Remove public access**:
   ```bash
   gcloud run services remove-iam-policy-binding adk-default-service-name \
     --member="allUsers" \
     --role="roles/run.invoker" \
     --project=my-project-76851-371010 \
     --region=us-central1
   ```

2. **Grant access to authorized users**:
   ```bash
   gcloud run services add-iam-policy-binding adk-default-service-name \
     --member="user:maorhz@google.com" \
     --role="roles/run.invoker" \
     --project=my-project-76851-371010 \
     --region=us-central1
   ```

---

## 🛡️ 6. Model Armor Prompt Shielding & Multi-Agent Routing

We configured **Google Cloud Model Armor** to secure the LLM application against prompt injection, jailbreaks, PII leakage, and malicious URLs. The application was split into a multi-agent workflow containing a security callback block that cleanly stops downstream execution without duplicating UI replies.

### IAM Permissions
We granted the **Model Armor User** (`roles/modelarmor.user`) role to the Cloud Run service account:
```bash
gcloud projects add-iam-policy-binding my-project-76851-371010 \
  --member="serviceAccount:855384940829-compute@developer.gserviceaccount.com" \
  --role="roles/modelarmor.user"
```

### Multi-Agent Workflow Implementation
The application is structured as a `Workflow` containing two agents: `chef_agent` and `grocery_agent`.

1. **Model Armor Callback**:
   We added a `before_agent_callback` named `model_armor_input_shield` to `chef_agent`. This callback calls Model Armor's `sanitize_user_prompt` API using the template `projects/my-project-76851-371010/locations/us-central1/templates/agent-shield`.
   *   If blocked, it emits a single event containing the warning `[Security Alert] Your request was blocked by security filters.` and halts the agent run.

2. **Clean Conditional Routing**:
   We wrapped `chef_agent` inside a custom `@node(rerun_on_resume=True)` wrapper function named `run_chef`.
   *   `run_chef` executes the `chef_agent` node using `ctx.run_node(chef_agent, ..., use_as_output=True)`. This suppresses duplicate recipe output events by delegating `chef_agent`'s output directly to the wrapper.
   *   If `chef_agent` returned `None` (was blocked), `run_chef` returns `None` immediately without setting a route value. Because no route is set and no default route is configured in the routing map, the workflow terminates cleanly with only the original security alert event printed.
   *   If safe, `run_chef` sets `ctx.route = "continue"`, which matches the routing map key to run `grocery_agent`.


```python
# 3. Create the multi-agent workflow with conditional routing
chef_grocery_workflow = Workflow(
    name="chef_grocery_workflow",
    edges=[
        (START, run_chef),
        (run_chef, {
            "continue": grocery_agent
        })
    ]
)
```

---

## 🛡️ 7. Real-Time Client-Side Prompt Shielding & Masking

To protect PII before it is displayed or stored in local UI histories, we implemented a real-time client-side shielding layer that integrates with the backend Google Cloud Model Armor SDP template.

### Core Capabilities:
1. **Zero-Latency Dynamic Optimistic Masking**: Eliminates the "visual flash of unmasked text" by pre-masking PII (emails, credit cards, street addresses, etc.) locally in the DOM as soon as the user hits Enter.
2. **Automated SDP Template Parsing**: The backend queries the live Google Cloud Sensitive Data Protection (DLP) inspectTemplate API (`projects/my-project-76851-371010/locations/us-central1/inspectTemplates/2828347596800781685`) to dynamically load active infoTypes and custom regex rules, compiling them into a combined regex alternation on the client.
3. **5-Minute Template Caching**: Updates made in the Google Cloud Console propagate to browser sessions within 5 minutes without restarting any backend service.
4. **Accurate SDP Exclusions**: Queries the Model Armor backend to validate whether a match is excluded (e.g., `maor@google.com` matching the exclusion regex).
6. **Dual XHR & Fetch Hooks**: Intercepts both standard browser `fetch` requests and Angular HttpClient's `XMLHttpRequest` (XHR) calls.

### Architecture Overview:

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant DOM as Browser UI
    participant FastAPI as Backend API Gateway
    participant DLP as DLP API (GCP)
    participant MA as Model Armor (SDP Template)
    participant RE as Vertex AI Agent Engine
    participant Chef as run_chef Node (RE)
    participant Grocery as Grocery Agent (RE)
    
    %% Boot & Page Load
    Note over User, Grocery: Phase 1: Startup & Dynamic Template Fetching
    FastAPI->>DLP: GetInspectTemplate(template_name)
    DLP-->>FastAPI: Return inspectTemplate config (InfoTypes, Custom Regexes)
    Note over User, Grocery: Map SDP infoTypes to local patterns & compile MASK_REGEX
    Note over User, Grocery: Overwrite index.html static assets on disk with compiled MASK_REGEX
    DOM->>FastAPI: Load page index.html (at / or /dev-ui/)
    FastAPI-->>DOM: Return index.html (CustomUIMiddleware intercepts and serves Custom UI HTML)

    %% Interception & Evaluation
    Note over User, Grocery: Phase 2: Client-side Interception & SDP Evaluation
    User->>DOM: Type prompt "My email is test@example.com" and hit Enter
    Note over User, Grocery: Optimistic Masking: Local regex pattern matching (PII masked immediately in DOM user bubble)
    DOM->>FastAPI: Sync POST /evaluate {text: prompt}
    FastAPI->>MA: SanitizeUserPromptRequest(prompt) using Template
    Note over User, Grocery: Model Armor SDP checks: inspect and deidentify PII based on active SDP template config
    MA-->>FastAPI: Return SanitizationResult (block state, deidentified_text)
    FastAPI-->>DOM: Return evaluate response {"block": false, "deidentified_text": "My email is ################"}
    Note over User, Grocery: Stateful DOM update: Keep masked PII or restore to clear text (if exclusion matched)
    DOM->>FastAPI: Send finalized prompt via POST /run (or /run_sse)
    
    %% Agent Platform
    Note over User, Grocery: Phase 3: Multi-Agent Workflow Execution (Agent Platform)
    FastAPI->>RE: Invoke Reasoning Engine (streamQuery)
    RE->>Chef: run_chef(node_input)
    Note over User, Grocery: Executes chef_agent & checks callback route status
    alt Callback route = blocked
        Chef-->>FastAPI: Return None (Workflow Halts with [Security Alert])
    else Callback route = continue
        Chef->>Grocery: Execute grocery_agent(recipe)
        Grocery-->>RE: Return final shopping list and nutrition breakout
    end
    RE-->>FastAPI: Stream tokens back
    FastAPI-->>DOM: Stream SSE response back
```

### Complete Implementation Details:
*   **ASGI Middleware**: [CustomUIMiddleware](file:///usr/local/google/home/maorhz/Documents/Code/chef-multi-agent/chef_grocery_app/services.py#L294) intercepts incoming HTTP requests to `/` and `/dev-ui/` to serve the custom Gourmet UI HTML with compiled PII regexes injected.
*   **DLP API Integration**: Uses credentials with custom quota-project overrides to dynamically fetch templates from the REST endpoint (`https://dlp.googleapis.com/v2/...`), extracting both standard built-in rulesets and custom regex patterns.
*   **XHR Hook**: Overrides `XMLHttpRequest.prototype.open` and `XMLHttpRequest.prototype.send` to perform a synchronous blocking call to `/evaluate` before the `/run` stream is dispatched.
*   **DOM Observer**: Uses a standard browser `MutationObserver` combined with `element._originalValue` state properties to ensure clean text replacements without permanently losing node values.

---

## 🎨 8. Premium Gourmet Custom UI (Production)

To elevate the application from a default ADK developer panel to a premium consumer product, we implemented a custom **Gourmet Split-Screen UI** at the root domain (`chef.gmandiant.com`).

### UX Concept & Layout
*   **Left Column (Culinary Chat)**: A sleek chat interface featuring preset suggestion pills (e.g., *High-Protein Keto Dinner*, *15-Min Vegan Pasta*), conversational history, and secure, interactive prompt shielding badges.
*   **Right Column (The Gourmet Board)**: A multi-tab dashboard that parses and presents the agent's output in real time:
    1.  **Recipe Tab**: A beautifully formatted culinary article with a prep/cook metadata grid and step-by-step cooking cards.
    2.  **Shopping List Tab**: A smart grocery checklist grouped by department/aisle (e.g., *Produce*, *Bakery*, *Meat*). Users can check off items as they shop.
    3.  **Nutrition HUD**: A visual macronutrient dashboard featuring real-time progress bars for Calories, Protein, Carbs, and Fat scaled against daily benchmarks.

---

### Container-Native Memory Asset Delivery

To bypass container-copying restrictions during Cloud Run deployments (where custom folders like `static/` are often excluded from python package uploads), we designed a **zero-filesystem, container-native asset delivery system**:

1.  **Memory-Backed Assets (`static_assets.py`)**: Embedded the entire frontend codebase (HTML, CSS, Javascript) as raw UTF-8 Python strings within [static_assets.py](file:///usr/local/google/home/maorhz/Documents/Code/chef-multi-agent/chef_grocery_app/static_assets.py).
2.  **FastAPI Memory Routes**: Registered custom memory routes in [services.py](file:///usr/local/google/home/maorhz/Documents/Code/chef-multi-agent/chef_grocery_app/services.py) that serve these assets directly as responses, bypassing disk I/O entirely:
    ```python
    @app.get("/static/styles.css")
    async def serve_css():
        return Response(content=static_assets.get_css(), media_type="text/css")

    @app.get("/static/app.js")
    async def serve_js():
        return Response(content=static_assets.get_js(), media_type="application/javascript")
    ```
3.  **ASGI Root Interception**: Inside `CustomUIMiddleware`, requests to the root path (`/` or `/index.html`) or `/dev-ui/` are intercepted at the ASGI layer to serve the gourmet HTML string from memory, replacing `MASK_REGEX_PLACEHOLDER` with the active compiled PII regex.
4.  **Dev/Prod Coexistence**: The custom gourmet UI is served at `/` for consumer use, while the default ADK developer console remains fully active and accessible at `/dev-ui` for debugging!

---

### Real-Time LLM Response Parsing

The frontend Javascript [app.js](file:///usr/local/google/home/maorhz/Documents/Code/chef-multi-agent/chef_grocery_app/static/app.js) parses the raw markdown streamed from the backend:
*   **Recipe**: Scans for headers containing `Recipe`, `Ingredients`, or `Instructions` and converts markdown syntax into rich HTML cards.
*   **Checklist**: Extracts bulleted items and groups them into department categories using a custom parser.
*   **HUD Dashboard**: Uses regex patterns (e.g., `/(?:protein|pro):\s*(\d+)/i`) to extract macro values, updating values and animating progress bars dynamically as the stream completes.




