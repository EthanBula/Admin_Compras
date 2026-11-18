"""
Supply Chain & Procurement Planning Dashboard
Faithful single-page vertical layout matching the user specifications:
- Title at the top (above navbar) with burgundy hover effect
- Centered navigation tabs with glowing yellow active indicator across 4 sections
- Full-width layout (no excessive lateral voids)
- Framed charts with disciplined Inter typography
- Explicit units on all chart titles and axes
- Exact financial savings: $938.54 ($378,555.62 baseline vs. $377,617.09 optimal)
- Dedicated 4th section: Cost Analysis & Budget Breakdown with stacked bar chart
- 100% in English
"""
from typing import Dict, Tuple
import os
import pandas as pd
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from agents.explainer_graph import FALLBACK_EXPLANATIONS, get_explanation

# --- Directory Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Design Tokens & Color Palette ---
COLORS = {
    'bg_app': '#FFFFFF',
    'bg_card': '#FFFFFF',
    'border': '#E2E8F0',
    'border_dark': '#CBD5E1',
    'text_main': '#0F172A',
    'text_muted': '#475569',
    'text_caption': '#64748B',
    'burgundy': '#2E1010',
    'gold': '#D4AF37',
    'gold_bright': '#FFC107',
    'bar_dark': '#1E293B',
    'bar_mid': '#64748B',
    'bar_light': '#94A3B8',
    'capacity_line': '#DC2626',
    'grid': '#F1F5F9'
}

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# --- Data Layer ---
def load_dashboard_data() -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], pd.DataFrame]:
    """Loads all CSV files and standardizes schemas to English."""
    results_path = os.path.join(BASE_DIR, 'resultados_plan_abastecimiento.csv')
    try:
        df_main = pd.read_csv(results_path)
        df_main['Week'] = 'Week ' + df_main['Semana'].astype(str)
        df_main['Week_Short'] = 'W' + df_main['Semana'].astype(str)
    except Exception as exc:
        print(f"Warning: Could not load {results_path}: {exc}. Using fallback data.")
        weeks = [f'Week {i}' for i in range(1, 12)]
        df_main = pd.DataFrame({
            'Week': weeks,
            'Week_Short': [f'W{i}' for i in range(1, 12)],
            'Compra_Tela': [334, 216] + [334]*8 + [78],
            'Compra_Hilo': [3300] + [0]*10,
            'Compra_Lamina': [2333, 417] + [0]*9,
            'Produccion_PT': [3340, 2160] + [3340]*8 + [780],
            'Inv_Tela': [0]*11,
            'Inv_Hilo': [2966, 2750, 2416, 2082, 1748, 1414, 1080, 746, 412, 78, 0],
            'Inv_Lamina': [216, 0, 1999, 2082, 1748, 1414, 1080, 746, 412, 78, 0],
            'Inv_PT': [2340, 2500, 4840, 4180, 4520, 5860, 7200, 9540, 9880, 6220, 0],
            'Pronostico': [1000, 2000, 1000, 4000, 3000, 2000, 2000, 1000, 3000, 7000, 7000]
        })

    def process_machine_file(filename: str) -> pd.DataFrame:
        filepath = os.path.join(BASE_DIR, filename)
        try:
            df = pd.read_csv(filepath)
            df = df.T
            df.columns = ['Usage', 'Capacity']
            df.index.name = 'Week'
            df = df.reset_index()
            df['Week'] = df['Week'].str.replace('Semana ', 'Week ')
            df['Week_Short'] = df['Week'].str.replace('Week ', 'W')
            df['Usage'] = pd.to_numeric(df['Usage'], errors='coerce').fillna(0)
            df['Capacity'] = pd.to_numeric(df['Capacity'], errors='coerce').fillna(0)
            return df
        except Exception as exc:
            print(f"Warning: Could not load {filename}: {exc}")
            return pd.DataFrame({'Week': df_main['Week'], 'Week_Short': df_main['Week_Short'], 'Usage': 0, 'Capacity': 0})

    def process_space_file(filename: str) -> pd.DataFrame:
        filepath = os.path.join(BASE_DIR, filename)
        try:
            df = pd.read_csv(filepath, index_col=0)
            df = df.T
            df.columns = ['Occupied', 'Available']
            df.index.name = 'Week'
            df = df.reset_index()
            df['Week'] = df['Week'].str.replace('Semana ', 'Week ')
            df['Week_Short'] = df['Week'].str.replace('Week ', 'W')
            df['Occupied'] = pd.to_numeric(df['Occupied'], errors='coerce').fillna(0)
            df['Available'] = pd.to_numeric(df['Available'], errors='coerce').fillna(0)
            return df
        except Exception as exc:
            print(f"Warning: Could not load {filename}: {exc}")
            return pd.DataFrame({'Week': df_main['Week'], 'Week_Short': df_main['Week_Short'], 'Occupied': 0, 'Available': 0})

    def process_costs_file(filename: str) -> pd.DataFrame:
        filepath = os.path.join(BASE_DIR, filename)
        try:
            df = pd.read_csv(filepath)
            df['Week'] = 'Week ' + df['Semana'].astype(str)
            df['Week_Short'] = 'W' + df['Semana'].astype(str)
            return df
        except Exception as exc:
            print(f"Warning: Could not load {filename}: {exc}")
            return pd.DataFrame({
                'Week': df_main['Week'],
                'Week_Short': df_main['Week_Short'],
                'Compras': [86340.0, 13546.2, 7647.93, 8183.29, 8756.12, 9369.05, 10024.88, 10726.62, 10726.62, 10726.62, 2505.02],
                'Fabricacion': [13360.0, 9244.8, 15295.86, 16366.57, 17512.23, 18738.09, 20049.76, 21453.24, 21453.24, 21453.24, 5010.04],
                'Almacenamiento': [1253.56, 1078.92, 2064.09, 2209.91, 2139.14, 2114.95, 2112.91, 2138.77, 1978.18, 1586.35, 450.88],
                'Total': [100953.56, 23869.92, 25007.89, 26759.78, 28407.49, 30222.09, 32187.55, 34318.63, 34158.04, 33766.21, 7965.94]
            })

    machines = {
        'CNC': process_machine_file('restriccion_maquina_uso_corte_cnc.csv'),
        'Wire': process_machine_file('restriccion_maquina_uso_corte_hilo.csv'),
        'Plasma': process_machine_file('restriccion_maquina_uso_corte_plasma.csv'),
        'Assembly': process_machine_file('restriccion_maquina_uso_ensamble.csv'),
        'Space': process_space_file('restriccion_espacio.csv')
    }

    df_costs = process_costs_file('costos_semanales.csv')

    return df_main, machines, df_costs

df_main, machines, df_costs = load_dashboard_data()

# --- Shared Plotly Styling Helper ---
def apply_clean_layout(fig: go.Figure, height: int = 440, top_margin: int = 85) -> go.Figure:
    """Standardizes font sizes, margins, titles, and legends across figures to prevent overlaps."""
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        font=dict(family=FONT_FAMILY, color=COLORS['text_muted'], size=12),
        margin=dict(l=54, r=24, t=top_margin, b=42),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#FFFFFF',
            bordercolor=COLORS['border'],
            font=dict(family=FONT_FAMILY, size=11, color=COLORS['text_main'])
        ),
        title=dict(
            font=dict(size=13, family=FONT_FAMILY, color=COLORS['text_main']),
            x=0,
            xanchor='left',
            y=0.98,
            yref='container'
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            linecolor=COLORS['border'],
            tickfont=dict(size=11, family=FONT_FAMILY, color=COLORS['text_caption']),
            title_font=dict(size=12, family=FONT_FAMILY, color=COLORS['text_main'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            linecolor=COLORS['border'],
            tickfont=dict(size=11, family=FONT_FAMILY, color=COLORS['text_caption']),
            title_font=dict(size=12, family=FONT_FAMILY, color=COLORS['text_main'])
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0,
            font=dict(size=11, family=FONT_FAMILY, color=COLORS['text_muted']),
            bgcolor='rgba(255, 255, 255, 0.85)'
        )
    )
    return fig

# --- Figure Builders ---
def build_procurement_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Compra_Tela'], name='Fabric Purchase [Rolls]',
        marker_color='#1E293B', hovertemplate='%{y:,.0f} rolls'
    ))
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Compra_Hilo'], name='Thread Purchase [Rolls]',
        marker_color='#64748B', hovertemplate='%{y:,.0f} rolls'
    ))
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Compra_Lamina'], name='Sheet Metal Purchase [Rolls]',
        marker_color='#94A3B8', hovertemplate='%{y:,.0f} rolls'
    ))
    fig.update_layout(
        title=dict(text='Raw Material Purchases by Week [Rolls]'),
        barmode='group',
        xaxis_title='Planning Week',
        yaxis_title='Purchased Quantity [Rolls]',
        legend_title_text='Raw Material'
    )
    return apply_clean_layout(fig, height=450, top_margin=85)

def build_production_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Produccion_PT'], name='Planned Production [100 u]',
        marker_color='#1E293B', opacity=0.9, hovertemplate='%{y:,.0f} (x100 u)'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Pronostico'], name='Demand Forecast [100 u]',
        mode='lines+markers', line=dict(color=COLORS['gold'], width=3),
        marker=dict(size=6, color=COLORS['gold']), hovertemplate='%{y:,.0f} (x100 u)'
    ))
    fig.update_layout(
        title=dict(text='Production Plan vs. Demand Forecast [Hundreds of Units / 100 u]'),
        xaxis_title='Planning Week',
        yaxis_title='Quantity [Hundreds of Units / 100 u]',
        legend_title_text='Variable'
    )
    return apply_clean_layout(fig, height=440, top_margin=85)

def build_machine_constraint_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Usage'], name='Actual Usage [Minutes]',
        marker_color='#64748B', hovertemplate='%{y:,.0f} min'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Capacity'], name='Available Capacity [Minutes]',
        mode='lines', line=dict(color=COLORS['capacity_line'], width=2, dash='dot'),
        hovertemplate='%{y:,.0f} min'
    ))
    fig.update_layout(
        title=dict(text=title),
        xaxis_title='Planning Week',
        yaxis_title='Time [Minutes]'
    )
    return apply_clean_layout(fig, height=430, top_margin=85)

def build_inventory_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Inv_Tela'], name='Fabric Inventory [Rolls]',
        mode='lines+markers', line=dict(color='#2563EB', width=2), marker=dict(size=5),
        hovertemplate='%{y:,.0f} rolls'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Inv_Hilo'], name='Thread Inventory [Rolls]',
        mode='lines+markers', line=dict(color='#0D9488', width=2), marker=dict(size=5),
        hovertemplate='%{y:,.0f} rolls'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Inv_Lamina'], name='Sheet Metal Inventory [Rolls]',
        mode='lines+markers', line=dict(color='#D97706', width=2), marker=dict(size=5),
        hovertemplate='%{y:,.0f} rolls'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Inv_PT'], name='Finished Goods Inventory [100 u]',
        mode='lines+markers', line=dict(color=COLORS['gold'], width=3, dash='dash'), marker=dict(size=6),
        hovertemplate='%{y:,.0f} (x100 u)'
    ))
    fig.update_layout(
        title=dict(text='Ending Inventory Levels by Category [Rolls & Hundreds of Units]'),
        xaxis_title='Planning Week',
        yaxis_title='Ending Inventory [Units / Rolls]',
        legend_title_text='Inventory Category'
    )
    return apply_clean_layout(fig, height=440, top_margin=85)

def build_space_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Occupied'], name='Occupied Space [m³]',
        marker_color='#1E293B', hovertemplate='%{y:,.2f} m³'
    ))
    fig.add_trace(go.Scatter(
        x=df['Week'], y=df['Available'], name='Available Capacity [m³]',
        mode='lines', line=dict(color=COLORS['capacity_line'], width=2.5, dash='dash'),
        hovertemplate='%{y:,.2f} m³'
    ))
    fig.update_layout(
        title=dict(text='Warehouse Space Utilization vs. Maximum Limit [m³]'),
        xaxis_title='Planning Week',
        yaxis_title='Warehouse Volume [m³]',
        legend_title_text='Capacity Metric'
    )
    return apply_clean_layout(fig, height=380, top_margin=85)

def build_cost_chart(df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart showing weekly expenditure across Purchasing, Manufacturing, and Storage."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Compras'], name='Purchasing Cost [USD $]',
        marker_color='#1E293B', hovertemplate='$%{y:,.2f}'
    ))
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Fabricacion'], name='Manufacturing Cost [USD $]',
        marker_color='#64748B', hovertemplate='$%{y:,.2f}'
    ))
    fig.add_trace(go.Bar(
        x=df['Week'], y=df['Almacenamiento'], name='Storage Cost [USD $]',
        marker_color='#94A3B8', hovertemplate='$%{y:,.2f}'
    ))
    fig.update_layout(
        title=dict(text='Weekly Cost Breakdown by Operational Category [USD $]'),
        barmode='stack',
        xaxis_title='Planning Week',
        yaxis_title='Total Cost [USD $]',
        legend_title_text='Cost Category'
    )
    return apply_clean_layout(fig, height=450, top_margin=85)

# Pre-generate figures in memory for zero latency
fig_procurement = build_procurement_chart(df_main)
fig_production = build_production_chart(df_main)
fig_cnc = build_machine_constraint_chart(machines['CNC'], 'Machine Usage: CNC Cutting [Minutes]')
fig_wire = build_machine_constraint_chart(machines['Wire'], 'Machine Usage: Wire Cutting [Minutes]')
fig_plasma = build_machine_constraint_chart(machines['Plasma'], 'Machine Usage: Plasma Cutting [Minutes]')
fig_assembly = build_machine_constraint_chart(machines['Assembly'], 'Machine Usage: Assembly & Sealing [Minutes]')
fig_inventory = build_inventory_chart(df_main)
fig_space = build_space_chart(machines['Space'])
fig_costs = build_cost_chart(df_costs)

# --- Initialize Dash Application ---
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    ],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
server = app.server
app.title = "Procurement and Production Plan"

# --- Dashboard Layout ---
app.layout = html.Div(style={'backgroundColor': '#FFFFFF', 'minHeight': '100vh', 'width': '100%'}, children=[

    # 1. TÍTULO PRINCIPAL EN EL TOPE ABSOLUTO (Arriba de la barra de navegación)
    html.Header(className="top-header-container", children=[
        html.H1("PROCUREMENT AND PRODUCTION PLAN", className="main-page-title")
    ]),

    # 2. BARRA DE NAVEGACIÓN CENTRADA (Debajo del título principal)
    html.Nav(className="sticky-navbar", children=[
        html.Div(className="nav-links-centered", children=[
            html.A("Procurement Plan", href="#procurement", className="nav-anchor-link active", id="nav-btn-procurement"),
            html.A("Production Plan", href="#production", className="nav-anchor-link", id="nav-btn-production"),
            html.A("Inventory", href="#inventory", className="nav-anchor-link", id="nav-btn-inventory"),
            html.A("Cost Analysis", href="#costs", className="nav-anchor-link", id="nav-btn-costs"),
            html.A("Strategy Explainer", href="#explainer", className="nav-anchor-link", id="nav-btn-explainer"),
        ])
    ]),

    # 3. CONTENEDOR FLUIDO DE ANCHO COMPLETO (Sin vacíos laterales excesivos)
    html.Main(className="fluid-page-container", children=[

        # SECCIÓN 1: PROCUREMENT PLAN
        html.Section(id="procurement", children=[
            html.Div(className="section-header-row", children=[
                html.H2("Procurement Plan", className="interactive-title", style={'fontSize': '1.5rem', 'margin': 0})
            ]),
            html.Div(className="chart-frame-card", children=[
                dcc.Graph(id="chart-procurement", figure=fig_procurement, config={'displayModeBar': False}),
                html.Div(className="insight-box", children=[
                    html.P([
                        "Most raw materials are purchased in early weeks to capitalize on lower supplier prices before weekly inflation. ",
                        "Fabric is purchased periodically on an as-needed basis to avoid volume accumulation and excessive storage costs. ",
                        "The total optimal cost is ",
                        html.Strong("$377,617.09"),
                        ", reflecting the addition of 1 sealing machine (31 units). This yields an exact savings of ",
                        html.Strong("$938.54"),
                        " compared to the 30-machine baseline ($378,555.62), setting the exact breakeven ceiling for machine acquisition."
                    ], className="insight-text")
                ])
            ])
        ]),

        # SECCIÓN 2: PRODUCTION PLAN
        html.Section(id="production", style={'marginTop': '3rem'}, children=[
            html.Div(className="section-header-row", children=[
                html.H2("Production Plan", className="interactive-title", style={'fontSize': '1.5rem', 'margin': 0})
            ]),
            html.Div(className="chart-frame-card", children=[
                dcc.Graph(id="chart-production", figure=fig_production, config={'displayModeBar': False}),
            ]),

            # STICKY HORIZONTAL SCROLL: Machine Constraint Analysis (CSS Scroll-Driven Animations)
            html.Div(className="machine-scroll-track", id="machine-scroll-track", children=[
                html.Div(className="machine-sticky-viewport", children=[
                    html.Div(className="machine-sticky-header", children=[
                        html.H3("Machine Constraint Analysis (Usage vs. Capacity) [Minutes]", className="subsection-title", style={'margin': '0 0 0.25rem 0'}),
                        html.P("Scroll down to inspect each machine in sequence (1 of 4 to 4 of 4)", className="machine-scroll-hint")
                    ]),
                    html.Div(className="machine-horizontal-strip", id="machine-horizontal-strip", children=[
                        # Slide 1: CNC Cutting
                        html.Div(className="machine-slide", children=[
                            html.Div(className="chart-frame-card machine-card", children=[
                                html.Span("Machine 1 of 4 • CNC Cutting", className="machine-badge"),
                                dcc.Graph(figure=fig_cnc, config={'displayModeBar': False})
                            ])
                        ]),
                        # Slide 2: Wire Cutting
                        html.Div(className="machine-slide", children=[
                            html.Div(className="chart-frame-card machine-card", children=[
                                html.Span("Machine 2 of 4 • Wire Cutting", className="machine-badge"),
                                dcc.Graph(figure=fig_wire, config={'displayModeBar': False})
                            ])
                        ]),
                        # Slide 3: Plasma Cutting
                        html.Div(className="machine-slide", children=[
                            html.Div(className="chart-frame-card machine-card", children=[
                                html.Span("Machine 3 of 4 • Plasma Cutting", className="machine-badge"),
                                dcc.Graph(figure=fig_plasma, config={'displayModeBar': False})
                            ])
                        ]),
                        # Slide 4: Assembly & Sealing (Primary Bottleneck)
                        html.Div(className="machine-slide", children=[
                            html.Div(className="chart-frame-card machine-card", children=[
                                html.Span("Machine 4 of 4 • Assembly & Sealing (Primary Bottleneck)", className="machine-badge bottleneck"),
                                dcc.Graph(figure=fig_assembly, config={'displayModeBar': False})
                            ])
                        ]),
                    ])
                ])
            ]),

            html.Div(className="insight-box", children=[
                html.P([
                    "Assembly sealing machines operate at 100% capacity across most weeks, constituting the binding operational bottleneck. ",
                    "Expanding sealing capacity from 30 to 31 machines captures exact cost savings of ",
                    html.Strong("$938.54"),
                    " (from $378,555.62 to $377,617.09). Adding capacity to CNC, Wire, or Plasma cutting yields $0 in savings because they already operate with substantial slack."
                ], className="insight-text")
            ])
        ]),

        # SECCIÓN 3: INVENTORY
        html.Section(id="inventory", style={'marginTop': '3rem'}, children=[
            html.Div(className="section-header-row", children=[
                html.H2("Inventory", className="interactive-title", style={'fontSize': '1.5rem', 'margin': 0})
            ]),
            html.Div(className="chart-frame-card", children=[
                dcc.Graph(id="chart-inventory", figure=fig_inventory, config={'displayModeBar': False}),

                html.Hr(className="gold-divider"),

                html.H3("Warehouse Space Constraint Analysis [m³]", className="subsection-title"),

                html.Div(className="chart-frame-card", children=[
                    dcc.Graph(id="chart-space", figure=fig_space, config={'displayModeBar': False})
                ]),

                html.Div(className="insight-box", children=[
                    html.P([
                        "Physical inventory in warehouse storage strictly reflects physical stock and incoming deliveries. ",
                        "Warehouse space shows ample slack across the horizon, with space utilization peaking in ",
                        html.Strong("Week 3"),
                        " when sheet metal orders placed in Week 1 physically arrive after their 2-week supplier lead time."
                    ], className="insight-text")
                ])
            ])
        ]),

        # SECCIÓN 4: COST ANALYSIS & BUDGET BREAKDOWN
        html.Section(id="costs", style={'marginTop': '3rem'}, children=[
            html.Div(className="section-header-row", children=[
                html.H2("Cost Analysis & Budget Breakdown", className="interactive-title", style={'fontSize': '1.5rem', 'margin': 0})
            ]),
            html.Div(className="chart-frame-card", children=[
                dcc.Graph(id="chart-costs", figure=fig_costs, config={'displayModeBar': False}),

                html.Div(className="insight-box", children=[
                    html.P([
                        "The overall budget comprises three expenditure components: ",
                        html.Strong("Purchasing: $178,552.34 (47.28%)"),
                        ", ",
                        html.Strong("Manufacturing: $179,937.08 (47.65%)"),
                        ", and ",
                        html.Strong("Storage: $19,127.67 (5.07%)"),
                        ", summing to a total optimal cost of ",
                        html.Strong("$377,617.09"),
                        ". Over 26.7% of total expenditure occurs in Week 1 ($100,953.56) to pre-purchase raw materials and minimize cumulative inflationary penalties."
                    ], className="insight-text")
                ])
            ])
        ]),

        # SECTION 5: STRATEGY EXPLAINER (LANGGRAPH ORCHESTRATION)
        html.Section(id="explainer", style={'marginTop': '3.5rem', 'marginBottom': '2rem'}, children=[
            html.Div(className="section-header-row", children=[
                html.H2("Strategy Explainer (AI Agent)", className="interactive-title", style={'fontSize': '1.5rem', 'margin': 0}),
            ]),
            html.P(
                "Interactive explanatory agent orchestrated with LangGraph synthesizing the 5 strategic pillars of the supply chain. "
                "Powered by Gemini 3.5 Flash-Lite (with failover to Gemini 3.1 Flash-Lite and local deterministic engine).",
                style={'color': COLORS['text_muted'], 'fontSize': '0.98rem', 'marginBottom': '1.5rem', 'maxWidth': '900px'}
            ),
            html.Div(className="chart-frame-card", style={'padding': '1.5rem 1.75rem'}, children=[
                # 1. Five Strategic Pillar Buttons
                html.Div(className="pillar-btn-container", children=[
                    html.Button("1. Context & Demand", id="btn-pilar-context", className="pillar-btn", n_clicks=0),
                    html.Button("2. Constraints & Bottlenecks", id="btn-pilar-constraints", className="pillar-btn", n_clicks=0),
                    html.Button("3. Mathematical Formulation (LP)", id="btn-pilar-model", className="pillar-btn", n_clicks=0),
                    html.Button("4. Procurement Decisions", id="btn-pilar-decisions", className="pillar-btn", n_clicks=0),
                    html.Button("5. Financial Impact & ROI", id="btn-pilar-impact", className="pillar-btn", n_clicks=0),
                ]),
                # 2. Chat / Response Window with Loading spinner
                dcc.Loading(
                    id="explainer-loading",
                    type="dot",
                    color="#0F172A",
                    children=[
                        html.Div(id="explainer-response-container", className="explainer-response-card", children=[
                            # User message bubble (shown when a question or pillar is submitted)
                            html.Div(id="chat-user-bubble-container", style={'display': 'none'}),
                            # Agent response block
                            html.Div(id="chat-agent-bubble-container", children=[
                                html.Div(className="explainer-header-meta", children=[
                                    html.H3("Supply Chain Strategy Assistant", id="explainer-topic-title", className="explainer-topic-title"),
                                    html.Span("⚡ LangGraph Agent", id="explainer-model-badge", className="explainer-model-badge")
                                ]),
                                dcc.Markdown(
                                    id="explainer-markdown-content",
                                    children="Select one of the 5 strategic pillars above or type a custom question below to start the model analysis.",
                                    className="explainer-markdown-body"
                                )
                            ])
                        ])
                    ]
                ),
                # 3. Custom Query Input Row (Below the chat / response window)
                html.Div(className="explainer-query-row", children=[
                    dcc.Input(
                        id="explainer-input-query",
                        type="text",
                        placeholder="Ask a specific question about the model, costs, constraints, or decisions...",
                        className="explainer-input",
                        n_submit=0
                    ),
                    html.Button("Ask Agent", id="explainer-submit-btn", className="explainer-submit-btn", n_clicks=0)
                ])
            ])
        ]),

        # FOOTER (Créditos con formato centrado y separación clara de palabras)
        html.Footer(className="dashboard-footer", children=[
            html.Div(className="footer-credits-container", children=[
                html.Span("E t h a n", className="footer-word"),
                html.Span("B u l a", className="footer-word"),
                html.Span("&", className="footer-ampersand"),
                html.Span("C e s i a", className="footer-word"),
                html.Span("B u r g o s", className="footer-word"),
            ])
        ])

    ])
])

# --- Callbacks ---
@app.callback(
    Output("chat-user-bubble-container", "children"),
    Output("chat-user-bubble-container", "style"),
    Output("explainer-topic-title", "children"),
    Output("explainer-model-badge", "children"),
    Output("explainer-markdown-content", "children"),
    Output("btn-pilar-context", "className"),
    Output("btn-pilar-constraints", "className"),
    Output("btn-pilar-model", "className"),
    Output("btn-pilar-decisions", "className"),
    Output("btn-pilar-impact", "className"),
    Output("explainer-input-query", "value"),
    Input("btn-pilar-context", "n_clicks"),
    Input("btn-pilar-constraints", "n_clicks"),
    Input("btn-pilar-model", "n_clicks"),
    Input("btn-pilar-decisions", "n_clicks"),
    Input("btn-pilar-impact", "n_clicks"),
    Input("explainer-submit-btn", "n_clicks"),
    Input("explainer-input-query", "n_submit"),
    dash.State("explainer-input-query", "value"),
    prevent_initial_call=True
)
def handle_explainer_interaction(c_ctx, c_con, c_mod, c_dec, c_imp, c_sub, n_sub, query_val):
    ctx_trigger = dash.callback_context.triggered_id
    
    btn_classes = {
        "btn-pilar-context": "pillar-btn",
        "btn-pilar-constraints": "pillar-btn",
        "btn-pilar-model": "pillar-btn",
        "btn-pilar-decisions": "pillar-btn",
        "btn-pilar-impact": "pillar-btn",
    }
    
    pillar_labels = {
        "btn-pilar-context": "1. Context & Demand",
        "btn-pilar-constraints": "2. Constraints & Bottlenecks",
        "btn-pilar-model": "3. Mathematical Formulation (LP)",
        "btn-pilar-decisions": "4. Procurement Decisions",
        "btn-pilar-impact": "5. Financial Impact & ROI",
    }
    
    topic = "context"
    explicit_topic = None
    user_bubble_content = None
    new_input_val = dash.no_update
    
    if ctx_trigger == "btn-pilar-context":
        topic = "context"
        explicit_topic = "context"
        btn_classes["btn-pilar-context"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-context"], className="chat-user-text")
        ])
    elif ctx_trigger == "btn-pilar-constraints":
        topic = "constraints"
        explicit_topic = "constraints"
        btn_classes["btn-pilar-constraints"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-constraints"], className="chat-user-text")
        ])
    elif ctx_trigger == "btn-pilar-model":
        topic = "model"
        explicit_topic = "model"
        btn_classes["btn-pilar-model"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-model"], className="chat-user-text")
        ])
    elif ctx_trigger == "btn-pilar-decisions":
        topic = "decisions"
        explicit_topic = "decisions"
        btn_classes["btn-pilar-decisions"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-decisions"], className="chat-user-text")
        ])
    elif ctx_trigger == "btn-pilar-impact":
        topic = "impact"
        explicit_topic = "impact"
        btn_classes["btn-pilar-impact"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-impact"], className="chat-user-text")
        ])
    elif ctx_trigger in ("explainer-submit-btn", "explainer-input-query"):
        if query_val and query_val.strip():
            cleaned_query = query_val.strip()
            topic = cleaned_query
            explicit_topic = None
            user_bubble_content = html.Div(className="chat-user-message", children=[
                html.Div(className="chat-user-header", children=[
                    html.Span("👤 You", className="chat-user-badge"),
                ]),
                html.P(f'"{cleaned_query}"', className="chat-user-text")
            ])
            new_input_val = ""
        else:
            topic = "context"
            explicit_topic = "context"
            btn_classes["btn-pilar-context"] = "pillar-btn active"
            user_bubble_content = html.Div(className="chat-user-message", children=[
                html.Div(className="chat-user-header", children=[
                    html.Span("Strategic Pillar", className="chat-user-badge"),
                ]),
                html.P(pillar_labels["btn-pilar-context"], className="chat-user-text")
            ])
    else:
        topic = "context"
        explicit_topic = "context"
        btn_classes["btn-pilar-context"] = "pillar-btn active"
        user_bubble_content = html.Div(className="chat-user-message", children=[
            html.Div(className="chat-user-header", children=[
                html.Span("Strategic Pillar", className="chat-user-badge"),
            ]),
            html.P(pillar_labels["btn-pilar-context"], className="chat-user-text")
        ])

    result = get_explanation(topic_or_query=topic, explicit_topic=explicit_topic)
    
    title = result.get("title", "Strategic Supply Chain Analysis")
    model_name = result.get("model_used", "Gemini 3.5 Flash-Lite")
    explanation = result.get("explanation", "")
    badge_text = f"⚡ {model_name}"
    
    bubble_style = {'display': 'block'} if user_bubble_content else {'display': 'none'}
    
    return (
        user_bubble_content,
        bubble_style,
        title,
        badge_text,
        explanation,
        btn_classes["btn-pilar-context"],
        btn_classes["btn-pilar-constraints"],
        btn_classes["btn-pilar-model"],
        btn_classes["btn-pilar-decisions"],
        btn_classes["btn-pilar-impact"],
        new_input_val
    )

if __name__ == '__main__':
    app.run(debug=True)
