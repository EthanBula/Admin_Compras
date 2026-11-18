# Supply Chain Procurement & Production Planning Optimization

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-3.0.4-008DE4?logo=plotly&logoColor=white)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-6.1.2-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![PuLP](https://img.shields.io/badge/Solver-PuLP%20CBC%20MILP-orange)](https://coin-or.github.io/pulp/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-black?logo=langchain)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/AI%20Engine-Gemini%203.5%20Flash--Lite-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-7%20Passed%20(100%25)-brightgreen?logo=pytest&logoColor=white)](https://docs.pytest.org/)

An end-to-end Operations Research (OR) and supply chain planning platform. Combines **Linear Programming (LP/MILP)** mathematical optimization with an executive-grade **Plotly Dash** dashboard, native **CSS Scroll-Driven Animations**, and an **Autonomous Strategy Explainer Agent** orchestrated via **LangGraph** powered by Google Gemini.

Developed by **Ethan Bula** & **Cesia Burgos**.

---

## 📌 Executive Summary & Key Results

The optimization model resolves multi-period procurement, manufacturing, and warehouse inventory allocation across a **strict 11-week operational planning horizon** characterized by:
- **Seasonal Demand Peaks:** High demand concentration in late weeks (surging to **7,000 units** in Weeks 10 and 11).
- **Cumulative Weekly Inflation:** Base purchase prices, manufacturing labor, and storage fees increase by **7% weekly** through Week 8, remaining flat through Week 11.
- **Physical Capacity Limits:** Warehouse storage restricted to **108.0 m³** (Weeks 1–3) and expanded by 15% to **124.2 m³** (Weeks 4–11).
- **Supply Lead Times:** 2-week international procurement lead time for sheet metal.

### Key Financial Findings
| Metric | Baseline Scenario (30 Sealers) | Optimal Scenario (31 Sealers) | Variance / Savings |
| :--- | :---: | :---: | :---: |
| **Total Horizon Cost** | **$378,555.62** | **$377,617.09** | **-$938.54** |
| **Purchasing Spend** | $178,552.34 | $178,552.34 | 47.28% of budget |
| **Manufacturing Spend** | $180,875.62 | $179,937.08 | 47.65% of budget |
| **Warehouse Storage Spend** | $19,127.66 | $19,127.67 | 5.07% of budget |
| **Week 1 Front-Loading** | $100,953.56 | $100,953.56 | **26.73%** of total budget |

> **Strategic Takeaway:** Adding a 31st assembly sealer machine yields an exact savings of **$938.54**. This defines the exact economic breakeven threshold management should pay to lease or acquire the additional machine. Sensitivity analysis confirms that expanding CNC, Wire, or Plasma cutting capacities delivers **$0.00** in savings because they operate with permanent slack.

---

## 🏗️ Architecture & Core Components

```
Administracion_Compras/
├── app.py                          # Main Dash dashboard application (layout & callbacks)
├── agents/
│   └── explainer_graph.py          # LangGraph Explainer Agent (StateGraph + Gemini dual-tier)
├── assets/
│   ├── style.css                   # Custom CSS (Scroll-driven animations, pure white theme)
│   └── nav.js                      # ScrollSpy, dynamic navbar glow & fallback interactions
├── tests/
│   └── test_dashboard.py           # Automated test suite (Pytest, 7 unit & integration tests)
├── resultados_plan_abastecimiento.csv # Optimal procurement, production & inventory schedule
├── costos_semanales.csv            # Weekly cost breakdown (Purchasing, Manufacturing, Storage)
├── restriccion_*.csv               # Machine usage vs. capacity CSV datasets (CNC, Wire, Plasma, Assembly, Space)
├── Evaluacion.ipynb                # Mathematical model source notebook & PuLP formulation
├── Context.pdf                     # Original industrial case specification document
├── .env.example                    # Template for environment variables (Gemini API key)
├── requirements.txt                # Python project dependencies
└── .gitignore                      # Git ignore rules (protecting .env and caches)
```

---

## 📊 Dashboard Sections

The dashboard is built on a responsive single-page architecture with a pure white (`#FFFFFF`) aesthetic, custom Inter typography, and disciplined information design:

### 1. Procurement Plan
- Multi-trace visualization of weekly raw material purchasing schedules (**Fabric**, **Thread**, and **Sheet Metal**) in rolls and sheets.
- Illustrates the front-loading strategy: 3,300 thread rolls and 2,333 sheet metal units ordered in Week 1 to hedge against cumulative inflation.

### 2. Production Plan & Machine Constraints (Sticky Horizontal Scroll)
- Displays finished goods assembly output smoothed against forecast demand.
- **Sticky Horizontal Reel:** Utilizes native **CSS Scroll-Driven Animations** (`view-timeline` and `animation-timeline`) to smoothly translate four machine stages along the horizontal axis as the user scrolls vertically:
  - *CNC Cutting (4 machines / 17,280 min):* Permanent operational slack.
  - *Wire Cutting (4 machines / 17,280 min):* Permanent operational slack.
  - *Plasma Cutting (10 machines / 43,200 min):* Ample capacity surplus.
  - *Assembly & Sealing (30/31 machines):* **Binding bottleneck** flagged with a dedicated status badge.

### 3. Inventory & Space Utilization
- Multi-category ending inventory levels comparing finished goods accumulation against raw material stock.
- Physical warehouse volume utilization tracking occupied cubic meters against the **108.0 m³** and **124.2 m³** capacity thresholds.

### 4. Cost Analysis & Budget Breakdown
- Stacked weekly expenditure bar chart segmenting Purchasing, Manufacturing, and Storage expenses.
- Highlights that **26.73% ($100,953.56)** of total expenditure occurs in Week 1 to lock in low base prices.

### 5. Strategy Explainer (LangGraph AI Agent)
- Integrated autonomous conversational agent built on **LangGraph (`StateGraph`)**.
- **Dual-Tier Model Routing with Deterministic Failover:**
  1. *Primary LLM:* `gemini-3.5-flash-lite` (sub-second latency, high analytical reasoning).
  2. *Secondary LLM:* `gemini-3.1-flash-lite` (automatic fallback if primary rate/quota limits are reached).
  3. *Local Engine:* Pre-compiled deterministic analytical engine returning exact quantitative proofs if offline.
- Features 5 one-click strategic pillar shortcuts (*Context & Demand*, *Constraints & Bottlenecks*, *Mathematical Formulation*, *Procurement Decisions*, *Financial Impact & ROI*) and a live user chat query interface.

---

## 📐 Mathematical Formulation

The linear program is formulated as follows:

### Objective Function
$$\min Z = \sum_{t=1}^{11} \left( \sum_{i \in \text{Materials}} c_{i,t} \cdot X_{i,t} + c_{\text{mfg},t} \cdot PT_t + c_{\text{storage},t} \sum_{i \in \text{Materials}} \text{Vol}_i \cdot \bar{I}_{i,t} + c_{\text{storage},t} \cdot \text{Vol}_{PT} \cdot \bar{I}_{PT,t} \right)$$

### Constraints
1. **Inventory Balance (Physical vs. In-Transit):**
   - For materials with zero lead time (Fabric, Thread):
     $$I_{i,t} = I_{i,t-1} + X_{i,t} - \alpha_i \cdot PT_t \quad \forall t$$
   - For Sheet Metal ($L=2$ weeks lead time):
     $$I_{\text{metal},t} = I_{\text{metal},t-1} + X_{\text{metal},t-2} - \alpha_{\text{metal}} \cdot PT_t \quad \forall t \ge 2$$
   - Storage tariffs are charged exclusively on **physical on-hand warehouse inventory**, exempting international orders in transit.
2. **Machine Capacity:**
   $$t_{m} \cdot PT_t \le M_m \cdot 4,320 \quad \forall m, t$$
3. **Warehouse Volume Limit:**
   $$\sum_{i} \text{Vol}_i \cdot I_{i,t} + \text{Vol}_{PT} \cdot I_{PT,t} \le \text{Cap}_t \quad (\text{Cap}_t = 108.0 \text{ for } t \le 3;\ 124.2 \text{ for } t > 3)$$

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EthanBula/Administracion_Compras.git
   cd Administracion_Compras
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and set your Google Gemini API Key:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # Linux / macOS
   cp .env.example .env
   ```
   Open `.env` and provide your key:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *(Note: If no API key is provided, the Strategy Explainer automatically operates via the local deterministic analytical engine).*

5. **Launch the Dashboard:**
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:8050/`.

---

## 🧪 Testing & Verification

The project includes an automated test suite implemented with `pytest`:

```bash
# Run all tests with verbose output
pytest tests/ -v
```

### Verified Test Cases
- `test_data_loading_structure`: Validates column schemas, types, and strict 11-week horizons across all CSV datasets.
- `test_procurement_chart_generation`: Verifies material traces, explicit roll units, and Plotly layout configurations.
- `test_production_and_constraints_charts`: Checks finished goods production figures and machine minute capacities.
- `test_inventory_and_space_charts`: Validates stock metrics and warehouse cubic volume limits.
- `test_cost_breakdown_chart`: Verifies stacked bar mode, USD formatting, and three-component expenditure breakdown.
- `test_dash_app_layout`: Traverses layout tree ensuring all 5 section anchors, horizontal scroll track, and chat cards exist.
- `test_explainer_agent_pillars`: Invokes the LangGraph agent across all 5 strategic pillars and custom queries, confirming numerical accuracy and LLM failover.

---

## 👥 Authors

- **Ethan Bula** — Operations Research, Linear Programming Formulation & Dashboard Architecture.
- **Cesia Burgos** — Production Modeling, Constraints Engineering & Economic Analysis.

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

