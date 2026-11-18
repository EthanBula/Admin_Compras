"""
LangGraph Multi-Agent Explainer for Supply Chain & Operations Management
Specialized in explaining:
1. Context (11-week horizon, demand variability, 7% weekly inflation)
2. Operational Constraints (machine limits, lead times, warehouse capacity)
3. Mathematical Model (LP objective function, physical inventory balances)
4. Derived Optimal Decisions (early bulk purchasing vs. periodic fabric purchases)
5. Financial Impact & ROI (exact $938.54 savings from adding 1 sealer machine)

Primary LLM: gemini-3.5-flash-lite
Fallback LLM: gemini-3.1-flash-lite
Offline / Local Fallback: Deterministic Operations Research Engine
"""
from typing import TypedDict, Annotated, Literal, Optional, Tuple
import os
import json
import urllib.request
import urllib.error

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None

from langgraph.graph import StateGraph, START, END

# --- API Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, '.env')

def get_gemini_api_key() -> Optional[str]:
    """
    Retrieves the Gemini API key from:
    1. OS environment variables (standard for cloud platforms like Render / Heroku)
    2. Local .env file (for local development)
    """
    # 1. Cloud environment variables
    env_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEI')
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. Local .env file fallback
    if os.path.exists(ENV_FILE):
        if dotenv_values is not None:
            try:
                env_vars = dotenv_values(ENV_FILE)
                key = env_vars.get('GEMINI_API_KEY') or env_vars.get('GEMINI_API_KEI')
                if key and key.strip():
                    return key.strip()
            except Exception:
                pass

        # Zero-dependency manual parser for .env
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() in ('GEMINI_API_KEY', 'GEMINI_API_KEI'):
                            clean_val = v.strip().strip("'\"")
                            if clean_val:
                                return clean_val
        except Exception:
            pass

    return None

SYSTEM_PROMPT = """You are an authoritative, pedagogical Senior Operations Research & Supply Chain Executive explaining the procurement and production planning optimization model developed by Ethan Bula and Cesia Burgos.

PROJECT FACTS & NUMERICAL TRUTHS (Strictly adhere to these exact numbers):
- Horizon: Strictly 11 weeks (Week 1 through Week 11). Never mention 12 weeks.
- Demand Forecast (100 units batches): [1000, 2000, 1000, 4000, 3000, 2000, 2000, 1000, 3000, 7000, 7000]. Peaks occur in weeks 10 and 11.
- Raw Materials:
  * Fabric: Base cost $20/roll, volume 0.2 m³/roll, cutting time 4 min/100u. Purchased periodically as-needed due to high volume penalty.
  * Thread: Base cost $10/roll, volume 0.016 m³/roll, cutting time 5 min/100u. Purchased early (3,300 rolls in week 1).
  * Sheet Metal: Base cost $20/roll, volume 0.025 m³/roll, cutting time 12 min/100u. Supplier lead time is 2 weeks. Initial inventory: 550 rolls. Orders placed in week 1 (2,333 rolls) arrive physically in week 3.
- Manufacturing: Base cost $4 per 100 units, assembly/sealing time 40 min per 100 units.
- Inflation: +7% cumulative weekly increase on purchasing, manufacturing, and storage from Week 1 through Week 8 (prices remain fixed from Week 8 to Week 11).
- Work Centers / Machines (4,320 operating minutes/week each):
  * CNC Cutting: 4 machines (17,280 min/wk available).
  * Wire Cutting: 4 machines (17,280 min/wk available).
  * Plasma Cutting: 10 machines (43,200 min/wk available).
  * Assembly & Sealing: 30 machines baseline (129,600 min/wk) vs. 31 machines optimal (133,920 min/wk). This is the BINDING BOTTLENECK operating at 100% capacity across most weeks.
- Warehouse Storage:
  * Weeks 1-3: 108 m³ capacity.
  * Weeks 4-11: 124.2 m³ capacity (+15% expansion).
  * Base storage cost: $12/m³/week.
  * Physical inventory storage rule: Only physical inventory in the warehouse incurs holding costs. In-transit orders (sheet metal lead time) do not occupy space or incur warehouse holding costs until physical delivery.
- Financial Optimization Results:
  * Baseline Cost (30 sealers): $378,555.62
  * Optimal Cost (31 sealers): $377,617.09
  * Exact Net Savings: $938.54. This represents the maximum economic breakeven price the company should pay to acquire the 31st sealer.
  * Cost Breakdown: Purchasing $178,552.34 (47.28%), Manufacturing $179,937.08 (47.65%), Storage $19,127.67 (5.07%).
  * Week 1 Expenditure: $86,340.00 in purchases ($100,953.56 total weekly cost, 26.7% of entire 11-week budget) to lock in low base prices before 7% weekly inflation.

Tone: Professional, pedagogical, mathematically precise, well-structured with clear markdown headings, bullet points, and bold key metrics. Respond in Spanish if the user asks in Spanish, or English if asked in English."""

# --- Fallback Knowledge Base (Deterministic) ---
DETERMINISTIC_RESPONSES = {
    "context": r"""### 1. Industrial Context & Demand Dynamics

The planning problem addresses a manufacturing enterprise optimizing raw material procurement, inventory storage, and finished goods assembly across a **strict 11-week planning horizon**.

* **Demand Profile:**
  Customer demand exhibits strong seasonality with steep peaks towards the end of the horizon:
  - *Weeks 1 to 3:* Moderate demand (1,000 to 2,000 units/week).
  - *Weeks 4 to 9:* Medium demand (between 1,000 and 4,000 units/week).
  - *Weeks 10 and 11:* **Extreme demand spikes of 7,000 units each**.
* **Inflationary Pressure:**
  Raw material acquisition prices, baseline manufacturing costs ($4 per 100 units), and warehouse holding tariffs ($12 per m³) suffer a **cumulative 7% weekly inflation rate** from Week 1 through Week 8, stabilizing thereafter through Week 11.
* **Bill of Materials (BOM):**
  Each 100 finished goods units require 10 rolls of fabric, 10 rolls of thread, and 10 sheet metal units.""",

    "constraints": r"""### 2. Operational Constraints, Bottlenecks & Lead Times

The optimization model adheres to four critical families of operational and physical limits:

1. **Machine Capacities (6 days × 12 hours = 4,320 minutes/week per machine):**
   - **CNC Cutting (4 machines):** 17,280 min available per week. Operates with permanent slack.
   - **Wire Cutting (4 machines):** 17,280 min available per week. Operates with permanent slack.
   - **Plasma Cutting (10 machines):** 43,200 min available per week. Substantial surplus capacity.
   - **Assembly & Sealing (30 / 31 machines):** **The binding bottleneck**. Requires 40 minutes per 100 units, operating at near 100% saturation throughout the horizon.
2. **Supplier Lead Time:**
   - Sheet metal has a **2-week lead time**. Orders placed in Week 1 do not physically arrive at the warehouse until Week 3.
   - The company holds an initial safety stock of **550 sheet metal units**.
3. **Warehouse Cubic Capacity:**
   - Weeks 1 to 3: Maximum limit of **108.0 m³**.
   - Weeks 4 to 11: 15% expansion up to **124.2 m³**.
   - Material volumes differ significantly: fabric occupies **0.2 m³/roll** (very bulky), whereas thread occupies only **0.016 m³** and sheet metal **0.025 m³**.""",

    "model": r"""### 3. Mathematical Formulation (Linear Programming)

The planning model is formulated in Python using `PuLP` and solved with the CBC MILP solver:

#### Objective Function
$$\min \ Z = \sum_{t=1}^{11} \left( \text{Purchasing Cost}_t + \text{Manufacturing Cost}_t + \text{Storage Cost}_t \right)$$

Where each cost term accounts for cumulative weekly inflation:
- **Purchasing Cost:** $\sum_i c_{i,t} \cdot X_{i,t}$ (Fabric, Thread, Sheet Metal).
- **Manufacturing Cost:** $c_{\text{mfg},t} \cdot PT_t$.
- **Storage Cost:** $c_{\text{storage},t} \cdot \sum_i \text{Vol}_i \cdot \bar{I}_{i,t}$.

#### Critical In-Transit Holding Cost Rule:
For sheet metal ($i=2$, lead time = 2 weeks):
- At $t=0$ (Week 1): Holding cost applies only to physical on-hand inventory: $\frac{I_{\text{initial}} + I_{2,0}}{2}$ (550 initial rolls minus production draw).
- At $t=1$ (Week 2): $\frac{I_{2,0} + I_{2,1}}{2}$.
- At $t \ge 2$ (Weeks 3 to 11): Physical arrivals are incorporated once received: $\frac{I_{2,t-1} + \text{SheetMetal}_{t-2} + I_{2,t}}{2}$.
**No inventory holding fees are levied on orders in international transit.**""",

    "decisions": r"""### 4. Optimal Sourcing & Production Decisions

The linear programming solver derives non-intuitive yet cost-optimal operational policies:

1. **Strategic Purchasing Front-Loading:**
   - The model concentrates **$86,340.00 in raw material purchases during Week 1** ($100,953.56 total weekly spend, 26.7% of the entire 11-week budget), pre-purchasing 3,300 thread rolls and 2,333 sheet metal units to hedge against cumulative 7% inflation.
2. **Just-In-Time (JIT) Fabric Purchasing:**
   - In contrast to thread and metal, fabric is purchased periodically week-by-week (334 rolls). Due to its high volume ($0.2\text{ m}^3/\text{roll}$), pre-purchasing fabric would immediately breach the $108\text{ m}^3$ warehouse cap and cause severe storage penalties.
3. **Smooth Production Smoothing:**
   - Because sealers cannot physically produce 7,000 units in Weeks 10 and 11, the plant runs at maximum capacity (3,340 units/week) starting in Week 1, buffering finished goods inventory to meet late-horizon demand surges.""",

    "impact": r"""### 5. Financial Impact, Sensitivity Analysis & Exact Savings

Scenario analysis quantifies the financial value of capacity expansion:

* **Baseline Cost (30 Sealing Machines):** **$378,555.62**
* **Optimal Cost (31 Sealing Machines):** **$377,617.09**
* **Exact Net Savings:** **$938.54**

#### Strategic Takeaways:
- **$938.54** represents the **exact economic breakeven ceiling** management should pay to lease or add the 31st sealer. Any cost below $938.54 yields positive net ROI.
- **Machine Sensitivity:** Adding capacity to CNC cutting, wire cutting, or plasma cutting produces **$0.00 in savings**, as they operate with ample slack and do not restrict throughput.
- **Optimal Budget Allocation ($377,617.09):**
  - Purchasing: **$178,552.34 (47.28%)**
  - Manufacturing: **$179,937.08 (47.65%)**
  - Storage: **$19,127.67 (5.07%)**"""
}

# Alias for external dashboard imports
FALLBACK_EXPLANATIONS = DETERMINISTIC_RESPONSES

# --- Gemini REST Invocation with Fallback Chain ---
def query_gemini_api(prompt: str, model_name: str, api_key: str) -> str:
    """Executes a direct POST request to Google Gemini REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1500
        }
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['candidates'][0]['content']['parts'][0]['text']

def generate_ai_explanation(prompt: str) -> Tuple[str, str]:
    """
    Primary: gemini-3.5-flash-lite
    Fallback: gemini-3.1-flash-lite
    Offline Fallback: Deterministic Knowledge Base
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return "No API key found in .env. Using deterministic engine.", "Deterministic Engine (No Key)"

    # 1. Try Primary Model: gemini-3.5-flash-lite
    try:
        ans = query_gemini_api(prompt, "gemini-3.5-flash-lite", api_key)
        return ans, "Gemini 3.5 Flash-Lite (Primary)"
    except Exception as exc_primary:
        print(f"Notice: gemini-3.5-flash-lite unavailable ({exc_primary}). Triggering fallback to gemini-3.1-flash-lite...")

    # 2. Try Fallback Model: gemini-3.1-flash-lite
    try:
        ans = query_gemini_api(prompt, "gemini-3.1-flash-lite", api_key)
        return ans, "Gemini 3.1 Flash-Lite (Quota/Rate Fallback)"
    except Exception as exc_fallback:
        print(f"Notice: gemini-3.1-flash-lite also unavailable ({exc_fallback}). Using deterministic engine...")

    # 3. Deterministic Local Fallback
    return "", "Deterministic Engine"

# --- LangGraph State Schema ---
class ExplainerState(TypedDict):
    input_text: str
    topic: Literal["context", "constraints", "model", "decisions", "impact", "custom"]
    prompt: str
    explanation: str
    model_used: str

# --- LangGraph Nodes ---
def node_router(state: ExplainerState) -> ExplainerState:
    """Routes the query to the appropriate topic node based on user selection or keywords."""
    txt = state.get("input_text", "").strip().lower()
    
    if state.get("topic") in ["context", "constraints", "model", "decisions", "impact"]:
        return state
    
    if any(k in txt for k in ["contexto", "demanda", "semanas", "horizonte", "inflacion"]):
        state["topic"] = "context"
    elif any(k in txt for k in ["restriccion", "maquina", "cuello", "capacidad", "bodega", "espacio", "lead time"]):
        state["topic"] = "constraints"
    elif any(k in txt for k in ["modelo", "matematico", "formula", "pulp", "balance", "objetivo"]):
        state["topic"] = "model"
    elif any(k in txt for k in ["decision", "compra", "adelanto", "tela", "produccion"]):
        state["topic"] = "decisions"
    elif any(k in txt for k in ["impacto", "ahorro", "selladora", "938", "377", "378", "roi", "sensibilidad"]):
        state["topic"] = "impact"
    else:
        state["topic"] = "custom"
        
    return state

def node_topic_resolver(state: ExplainerState) -> ExplainerState:
    """Constructs the prompt and pre-seeds the deterministic answer in English."""
    topic = state.get("topic", "custom")
    user_query = state.get("input_text", "")
    
    if topic in DETERMINISTIC_RESPONSES:
        fallback_text = DETERMINISTIC_RESPONSES[topic]
        prompt = (
            f"Explain with rigorous clarity and mathematical depth the following supply chain pillar: '{topic.upper()}'.\n"
            f"User query / context requested: '{user_query}'\n"
            "STRICT REQUIREMENT: Respond 100% in professional English. Use clear markdown formatting, bold metrics, and bullet points.\n"
            "Ground your answer on the exact quantitative figures: 11-week horizon, 7% weekly inflation until week 8, "
            "baseline cost $378,555.62, optimal cost $377,617.09, and exact net savings of $938.54 from adding the 31st sealing machine."
        )
    else:
        fallback_text = DETERMINISTIC_RESPONSES["impact"]
        prompt = (
            f"Answer the following user question regarding the supply chain optimization and procurement model: '{user_query}'.\n"
            "STRICT REQUIREMENT: Respond 100% in professional English. Rely on the exact quantitative facts of the model: "
            "11 planning weeks, $377,617.09 total cost, $938.54 exact savings for 1 additional sealer (the only bottleneck), "
            "26.7% front-loading in Week 1 ($100,953.56 total spend), and physical warehouse inventory distinctions."
        )
        
    state["prompt"] = prompt
    state["explanation"] = fallback_text
    return state

def node_llm_generator(state: ExplainerState) -> ExplainerState:
    """Executes the dual-tier Gemini LLM call (gemini-3.5-flash-lite -> gemini-3.1-flash-lite)."""
    prompt = state.get("prompt", "")
    topic = state.get("topic", "custom")
    
    ai_text, model_name = generate_ai_explanation(prompt)
    
    if ai_text and len(ai_text.strip()) > 30:
        state["explanation"] = ai_text
        state["model_used"] = model_name
    else:
        # Fallback to deterministic pre-computed response
        state["explanation"] = DETERMINISTIC_RESPONSES.get(topic, DETERMINISTIC_RESPONSES["impact"])
        state["model_used"] = "Local Analytical Engine (Deterministic Fallback)"
        
    return state

# --- Compile LangGraph Workflow ---
workflow = StateGraph(ExplainerState)
workflow.add_node("router", node_router)
workflow.add_node("topic_resolver", node_topic_resolver)
workflow.add_node("llm_generator", node_llm_generator)

workflow.add_edge(START, "router")
workflow.add_edge("router", "topic_resolver")
workflow.add_edge("topic_resolver", "llm_generator")
workflow.add_edge("llm_generator", END)

explainer_app = workflow.compile()

# --- Main Public API Function ---
def get_explanation(topic_or_query: str, explicit_topic: Optional[str] = None) -> dict:
    """
    Public entrypoint to invoke the LangGraph explainer.
    Returns:
    {
        'topic': str,
        'title': str,
        'explanation': str,
        'model_used': str
    }
    """
    initial_state: ExplainerState = {
        "input_text": topic_or_query,
        "topic": explicit_topic if explicit_topic in ["context", "constraints", "model", "decisions", "impact"] else "custom",
        "prompt": "",
        "explanation": "",
        "model_used": ""
    }
    
    result = explainer_app.invoke(initial_state)
    
    titles = {
        "context": "1. Industrial Context & Demand Dynamics",
        "constraints": "2. Operational Constraints, Bottlenecks & Lead Times",
        "model": "3. Mathematical Formulation (Linear Programming)",
        "decisions": "4. Optimal Sourcing & Production Decisions",
        "impact": "5. Financial Impact, Sensitivity Analysis & Net Savings ($938.54)",
        "custom": "Strategic Supply Chain Analysis"
    }
    
    return {
        "topic": result.get("topic", "custom"),
        "title": titles.get(result.get("topic", "custom"), "Model Strategy Explanation"),
        "explanation": result.get("explanation", ""),
        "model_used": result.get("model_used", "Local Analytical Engine")
    }
