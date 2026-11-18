"""
Automated Test Suite for Supply Chain & Procurement Dashboard.
Follows python-testing-patterns and modern-python best practices.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
from app import (
    load_dashboard_data,
    build_procurement_chart,
    build_production_chart,
    build_machine_constraint_chart,
    build_inventory_chart,
    build_space_chart,
    build_cost_chart,
    app
)

@pytest.fixture(scope="module")
def dashboard_data():
    """Loads and caches the dashboard datasets."""
    df_main, machines, df_costs = load_dashboard_data()
    return df_main, machines, df_costs

def test_data_loading_structure(dashboard_data):
    """Verifies that all primary datasets and machine frames load with expected columns."""
    df_main, machines, df_costs = dashboard_data
    
    assert not df_main.empty, "Primary dataframe should not be empty"
    assert 'Week' in df_main.columns, "Main dataframe must contain English 'Week' column"
    assert 'Week_Short' in df_main.columns, "Main dataframe must contain 'Week_Short' column"
    assert len(df_main) == 11, "Should have strictly 11 weeks of planning data"

    assert not df_costs.empty, "Costs dataframe should not be empty"
    assert len(df_costs) == 11, "Costs dataframe should have strictly 11 weeks"
    for col in ['Compras', 'Fabricacion', 'Almacenamiento', 'Total']:
        assert col in df_costs.columns, f"Cost dataframe must contain column '{col}'"

    required_machines = ['CNC', 'Wire', 'Plasma', 'Assembly', 'Space']
    for m in required_machines:
        assert m in machines, f"Machine dictionary must contain {m}"
        assert not machines[m].empty, f"{m} dataframe should not be empty"

def test_procurement_chart_generation(dashboard_data):
    """Verifies procurement figure traces, units, and layout configuration."""
    df_main, _, _ = dashboard_data
    fig = build_procurement_chart(df_main)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3, "Procurement chart must have 3 material traces"
    assert 'Rolls' in fig.layout.yaxis.title.text, "Y-axis title must explicitly state [Rolls]"
    trace_names = [t.name for t in fig.data]
    assert any('Fabric' in name for name in trace_names)
    assert any('Thread' in name for name in trace_names)
    assert any('Sheet Metal' in name for name in trace_names)

def test_production_and_constraints_charts(dashboard_data):
    """Verifies production and machine constraint figures."""
    df_main, machines, _ = dashboard_data
    fig_prod = build_production_chart(df_main)
    assert isinstance(fig_prod, go.Figure)
    assert len(fig_prod.data) == 2, "Production chart must include Planned FG and Forecast"
    assert 'Hundreds' in fig_prod.layout.yaxis.title.text or '100 u' in fig_prod.layout.yaxis.title.text

    fig_assembly = build_machine_constraint_chart(machines['Assembly'], 'Machine Usage: Assembly & Sealing [Minutes]')
    assert isinstance(fig_assembly, go.Figure)
    assert len(fig_assembly.data) == 2, "Constraint chart must have Usage and Capacity traces"
    assert 'Minutes' in fig_assembly.layout.yaxis.title.text

def test_inventory_and_space_charts(dashboard_data):
    """Verifies inventory levels and space utilization figures."""
    df_main, machines, _ = dashboard_data
    fig_inv = build_inventory_chart(df_main)
    assert isinstance(fig_inv, go.Figure)
    assert len(fig_inv.data) == 4, "Inventory chart must have 4 stock categories"

    fig_space = build_space_chart(machines['Space'])
    assert isinstance(fig_space, go.Figure)
    assert len(fig_space.data) == 2, "Space chart must have Occupied and Capacity traces"
    assert 'm³' in fig_space.layout.yaxis.title.text

def test_cost_breakdown_chart(dashboard_data):
    """Verifies weekly cost breakdown stacked bar chart."""
    _, _, df_costs = dashboard_data
    fig_cost = build_cost_chart(df_costs)
    assert isinstance(fig_cost, go.Figure)
    assert len(fig_cost.data) == 3, "Cost chart must have 3 traces (Purchasing, Manufacturing, Storage)"
    assert fig_cost.layout.barmode == 'stack', "Cost chart must be a stacked bar chart"
    assert 'USD $' in fig_cost.layout.yaxis.title.text

def test_dash_app_layout():
    """Verifies that the Dash layout defines all 4 section anchors, titles, and sticky horizontal scroll track."""
    layout = app.layout
    assert layout is not None, "Dash application must have a valid layout"
    
    # Traverse layout tree to verify required elements
    ids_found = set()
    classes_found = set()
    
    def traverse(component):
        if hasattr(component, 'id') and component.id:
            ids_found.add(component.id)
        if hasattr(component, 'className') and component.className:
            for cls in component.className.split():
                classes_found.add(cls)
        if hasattr(component, 'children'):
            children = component.children
            if isinstance(children, list):
                for child in children:
                    traverse(child)
            elif children:
                traverse(children)
                
    traverse(layout)
    assert 'procurement' in ids_found, "Missing '#procurement' section"
    assert 'production' in ids_found, "Missing '#production' section"
    assert 'inventory' in ids_found, "Missing '#inventory' section"
    assert 'costs' in ids_found, "Missing '#costs' section"
    assert 'explainer' in ids_found, "Missing '#explainer' section"
    assert 'chat-user-bubble-container' in ids_found, "Missing '#chat-user-bubble-container' in explainer card"
    assert 'machine-scroll-track' in ids_found, "Missing '#machine-scroll-track' element"
    assert 'machine-horizontal-strip' in ids_found, "Missing '#machine-horizontal-strip' element"
    assert 'machine-slide' in classes_found, "Missing '.machine-slide' class"

def test_explainer_agent_pillars():
    """Verifies that the LangGraph Explainer Agent resolves all 5 pillars and custom queries in English."""
    from agents.explainer_graph import get_explanation
    
    pillars = ['context', 'constraints', 'model', 'decisions', 'impact']
    for p in pillars:
        res = get_explanation(p, explicit_topic=p)
        assert isinstance(res, dict)
        assert res.get('topic') == p
        assert len(res.get('explanation', '')) > 50, f"Explanation for {p} should be detailed"
        assert res.get('model_used') is not None

    # Custom query test
    custom_res = get_explanation("How much money does adding the 31st sealing machine save?")
    assert "$938.54" in custom_res.get('explanation', '') or "938" in custom_res.get('explanation', '')
