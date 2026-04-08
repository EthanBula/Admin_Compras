import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

try:
    df = pd.read_csv('resultados_plan_abastecimiento.csv')
    df['Semana'] = 'Semana ' + df['Semana'].astype(str)
    def process_constraint_csv(filepath, use_col_name, capacity_col_name, index_col=None):
        df = pd.read_csv(filepath, index_col=index_col)
        df = df.T 
        if index_col is None: 
             df.columns = [use_col_name, capacity_col_name]
        else: 
            df = df.rename(columns={df.columns[0]: use_col_name, df.columns[1]: capacity_col_name})
        
        df.index.name = 'Semana'
        df = df.reset_index()
        df[use_col_name] = pd.to_numeric(df[use_col_name])
        df[capacity_col_name] = pd.to_numeric(df[capacity_col_name])
        return df

    #Restricciones
    df_cnc = process_constraint_csv('restriccion_maquina_uso_corte_cnc.csv', 'Uso', 'Disponible')
    df_hilo = process_constraint_csv('restriccion_maquina_uso_corte_hilo.csv', 'Uso', 'Disponible')
    df_plasma = process_constraint_csv('restriccion_maquina_uso_corte_plasma.csv', 'Uso', 'Disponible')
    df_ensamble = process_constraint_csv('restriccion_maquina_uso_ensamble.csv', 'Uso', 'Disponible')
    df_espacio = process_constraint_csv('restriccion_espacio.csv', 'Espacio Ocupado', 'Espacio Disponible', index_col=0)
except FileNotFoundError:
    print("Error: El archivo 'resultados_plan_abastecimiento.csv' no se encontró.")
    print("Por favor, asegúrate de que el archivo CSV está en el mismo directorio que el script.")
    #Crear un DataFrame vacío
    df = pd.DataFrame({
        'Semana': [], 'Compra_Tela': [], 'Compra_Hilo': [], 'Compra_Lamina': [],
        'Produccion_PT': [], 'Inv_Tela': [], 'Inv_Hilo': [], 'Inv_Lamina': [],
        'Inv_PT': [], 'Pronostico': []
    })


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  

COLORS = {
    'background': '#2E1010',
    'text': '#C6C5C5',
    'gold_line': '#D4AF37',
    'bar_color_1': '#a7a1a1',
    'bar_color_2': '#7a6a6a',
    'bar_color_3': '#C6C5C5',
    'line_color': '#D4AF37',
    'line_capacity_color': '#FF5733'
}

TAB_STYLE = {
    'backgroundColor': COLORS['background'],
    'color': '#7a6a6a',
    'border': 'none',
    'padding': '15px',
    'fontSize':'3em'
}

TAB_SELECTED_STYLE = {
    'backgroundColor': COLORS['background'],
    'color': '#a7a1a1',
    'borderBottom': f"3px solid {COLORS['gold_line']}",
    'border':'none',
    'padding': '15px',
    'fontSize':'3em'
}

#Layout
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'}, children=[
    
    # 1. Título Principal
    html.H1("PLAN DE ABASTECIMIENTO Y PRODUCCIÓN", style={
        'textAlign': 'center', 'color': COLORS['text'], 'fontSize': '4em', 
        'fontFamily': 'sans-serif', 'fontWeight': 'lighter', 'marginBottom': '120px', 'marginTop': '40px'
    }),
    
    # 2. Contenedor de Pestañas
    dcc.Tabs(id="main-tabs", value='tab-abastecimiento', children=[

        # Pestaña 1: Plan de Abastecimiento
        dcc.Tab(label='Plan de Abastecimiento', value='tab-abastecimiento', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div([
                dcc.Graph(id='abastecimiento-graph', style={'height': '80vh'}),
                html.P("Se buscará realizar la compra de gran parte de los insumos necesarios durante las primeras semanas, aprovechando que los precios de los insumos se encuentran más bajos. El insumo de tela se compra de forma periódica lo que se necesita para evitar acumulaciones por su alto volumen ocupado, lo que lleva a altos costos de almacenamiento. El costo total estimado es de $377474 contando con el aumento de 1 máquina selladora. La implementación de esta máquina conlleva al ahorro de aproximadamente $1000, por lo que eso es lo máximo que se debería pagar.", style={'color': COLORS['text'], 'padding': '20px', 'textAlign':'justify',
                                                                                                              'fontSize':'1.5em', 'marginTop': '40px'}),
            ], style={'padding': '20px'})
        ]),

        # Pestaña 2: Plan de Producción
        dcc.Tab(label='Plan de Producción', value='tab-produccion', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div([
                dcc.Graph(id='produccion-graph', style={'height': '80vh'}),
                html.Hr(style={'borderColor': COLORS['gold_line'], 'margin': '40px 0'}),
                html.H3("Análisis de Restricciones de Máquinas (Uso vs. Capacidad)", style={'color': COLORS['text'], 'textAlign': 'center'}),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(id='cnc-graph'), width=6),
                    dbc.Col(dcc.Graph(id='hilo-graph'), width=6),
                ], style={'marginTop': '20px'}),

                dbc.Row([
                    dbc.Col(dcc.Graph(id='plasma-graph'), width=6),
                    dbc.Col(dcc.Graph(id='ensamble-graph'), width=6),
                ], style={'marginTop': '20px'}),
                html.P("Se observa como las maquinas selladoras encargadas del ensamble son las que tienen un mayor porcentaje de utilizacion la mayor parte del tiempo, indicando que ahí se encuentra el cuello de botella y explicando por qué adicionar una maquina a ese proceso se traduce en una reducción de $1000, mientras que las otras representan cambios minimos en el costo.", style={'color': COLORS['text'], 'padding': '20px', 'textAlign':'justify','fontSize':'1.5em', 'marginTop': '40px'})
            ], style={'padding': '20px'})
        ]),

        # Pestaña 3: Inventario
        dcc.Tab(label='Inventario', value='tab-inventario', style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE, children=[
            html.Div([
                dcc.Graph(id='inventario-graph', style={'height': '80vh'}),
                html.Hr(style={'borderColor': COLORS['gold_line'], 'margin': '40px 0'}),
                html.H3("Análisis de Restricción de Espacio en Almacén", style={'textAlign': 'center', 'color': COLORS['text']}),
                dcc.Graph(id='espacio-graph', style={'height': '60vh', 'marginTop': '20px'}),
                html.P("Existe una buena holgura de espacio la mayoría de las semanas, con excepción de la semana 3, debido a que es cuando llegan los rollos de lamina pedidos la semana 1 por el Lead Time de 2 semanas.", style={'color': COLORS['text'], 'padding': '20px', 'textAlign':'justify','fontSize':'1.5em', 'marginTop': '40px'})
            ], style={'padding': '20px'})
        ]),
    ]),

    # 3. Pie de Página
    html.Footer(
        html.P("E t h a n  B u l a  &  C e s i a  B u r g o s", style={
            'textAlign': 'center', 'color': '#7a6a6a', 'padding': '40px 0 20px 0', 'fontSize': '2em'
        })
    )

])


#Callbacks

# Callback para el Gráfico de Abastecimiento
@app.callback(
    Output('abastecimiento-graph', 'figure'),
    Input('main-tabs', 'value') 
)
def update_abastecimiento_graph(tab):
    if tab == 'tab-abastecimiento' and not df.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(x=df['Semana'], y=df['Compra_Tela'], name='Compra de Tela', marker_color=COLORS['bar_color_1']))
        fig.add_trace(go.Bar(x=df['Semana'], y=df['Compra_Hilo'], name='Compra de Hilo', marker_color=COLORS['bar_color_2']))
        fig.add_trace(go.Bar(x=df['Semana'], y=df['Compra_Lamina'], name='Compra de Lámina', marker_color=COLORS['bar_color_3']))

        fig.update_layout(
            barmode='group',
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font_color=COLORS['text'],
            xaxis_title='Semana',
            yaxis_title='Cantidad Comprada',
            legend_title_text='Materia Prima',
            transition_duration=500,
            xaxis=dict(
                title_font=dict(size=24)  
            ),
            yaxis=dict(
                title_font=dict(size=24) 
            ),
            legend=dict(
                font=dict(size=24),             
                title_font=dict(size=24)        
            )
        )
        return fig
    # Devuelve una figura vacía si no es la pestaña correcta o el df está vacío
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])


# Callback para el Gráfico de Producción
@app.callback(
    Output('produccion-graph', 'figure'),
    Input('main-tabs', 'value')
)
def update_produccion_graph(tab):
    if tab == 'tab-produccion' and not df.empty:
        fig = go.Figure()

        # Gráfico de barras para la producción
        fig.add_trace(go.Bar(x=df['Semana'], y=df['Produccion_PT'], name='Producción Planificada', marker_color=COLORS['bar_color_1']))
        # Gráfico de línea para el pronóstico
        fig.add_trace(go.Scatter(x=df['Semana'], y=df['Pronostico'], name='Pronóstico de Demanda', mode='lines+markers', line=dict(color=COLORS['line_color'], width=3)))

        fig.update_layout(
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font_color=COLORS['text'],
            xaxis_title='Semana',
            yaxis_title='Unidades',
            legend_title_text='Variable',
            transition_duration=500,                    
            xaxis=dict(
                title_font=dict(size=24)  
            ),
            yaxis=dict(
                title_font=dict(size=24) 
            ),
            legend=dict(
                font=dict(size=24),             
                title_font=dict(size=24)        
            )
        )
        return fig
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])


# Callback para el Gráfico de Inventario
@app.callback(
    Output('inventario-graph', 'figure'),
    Input('main-tabs', 'value')
)
def update_inventario_graph(tab):
    if tab == 'tab-inventario' and not df.empty:
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df['Semana'], y=df['Inv_Tela'], name='Inventario de Tela', mode='lines+markers', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=df['Semana'], y=df['Inv_Hilo'], name='Inventario de Hilo', mode='lines+markers', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=df['Semana'], y=df['Inv_Lamina'], name='Inventario de Lámina', mode='lines+markers', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=df['Semana'], y=df['Inv_PT'], name='Inventario de Producto Terminado', mode='lines+markers', line=dict(color=COLORS['line_color'], width=4, dash='dash')))

        fig.update_layout(
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font_color=COLORS['text'],
            xaxis_title='Semana',
            yaxis_title='Unidades en Inventario',
            legend_title_text='Tipo de Inventario',
            transition_duration=500,
            xaxis=dict(
                title_font=dict(size=24)  
            ),
            yaxis=dict(
                title_font=dict(size=24)  
            ),
            legend=dict(
                font=dict(size=24),            
                title_font=dict(size=24)      
            )
        )
        return fig
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])
def create_constraint_figure(df, use_col, cap_col, title):
    if df.empty:
        return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'], title=f'{title} (Datos no disponibles)')
    
    fig = go.Figure()
    # Barra para el uso
    fig.add_trace(go.Bar(x=df['Semana'], y=df[use_col], name='Uso', marker_color=COLORS['bar_color_2']))
    # Línea para la capacidad
    fig.add_trace(go.Scatter(x=df['Semana'], y=df[cap_col], name='Capacidad', mode='lines', line=dict(color=COLORS['line_capacity_color'], width=3, dash='dot')))
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text'],
        title_text=title,
        xaxis_title='Semana',
        yaxis_title='Minutos',
        transition_duration=500,
        xaxis=dict(title_font=dict(size=16)),
        yaxis=dict(title_font=dict(size=16)),
        legend=dict(font=dict(size=12), title_font=dict(size=14))
    )
    return fig
@app.callback(Output('cnc-graph', 'figure'), Input('main-tabs', 'value'))
def update_cnc_graph(tab):
    if tab == 'tab-produccion':
        return create_constraint_figure(df_cnc, 'Uso', 'Disponible', 'Uso de Máquina: Corte CNC')
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

@app.callback(Output('hilo-graph', 'figure'), Input('main-tabs', 'value'))
def update_hilo_graph(tab):
    if tab == 'tab-produccion':
        return create_constraint_figure(df_hilo, 'Uso', 'Disponible', 'Uso de Máquina: Corte Hilo')
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

@app.callback(Output('plasma-graph', 'figure'), Input('main-tabs', 'value'))
def update_plasma_graph(tab):
    if tab == 'tab-produccion':
        return create_constraint_figure(df_plasma, 'Uso', 'Disponible', 'Uso de Máquina: Corte Plasma')
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

@app.callback(Output('ensamble-graph', 'figure'), Input('main-tabs', 'value'))
def update_ensamble_graph(tab):
    if tab == 'tab-produccion':
        return create_constraint_figure(df_ensamble, 'Uso', 'Disponible', 'Uso de Máquina: Ensamble')
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

@app.callback(Output('espacio-graph', 'figure'), Input('main-tabs', 'value'))
def update_espacio_graph(tab):
    if tab == 'tab-inventario':
        fig = create_constraint_figure(df_espacio, 'Espacio Ocupado', 'Espacio Disponible', 'Uso del Espacio de Almacén')
        fig.update_layout(yaxis_title='Espacio [m³]') # Corregir el título del eje Y
        return fig
    return go.Figure().update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])


if __name__ == '__main__':
    app.run(debug=True)