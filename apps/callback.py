from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_html_components as html
import dash_bootstrap_components as dbc

#### ==== #### ==== #### ==== #### ==== ####

from apps import dbconnect as db
from app import app

@app.callback(
    Output('yields_graph', 'figure'),
    [Input('selected_yield_store', 'data'), Input('yield_stream_dropdown_options', 'value')]
)
def update_yield_graph(selected_yield, selected_dropdown_value):
    sql = (f"""
        SELECT Yield_Date, Yield_Amount, T_05_ID
        FROM T_05
        WHERE NOT T_05_delete_ind AND Yield_Stream = '{selected_dropdown_value}'
        ORDER BY Yield_Date DESC;
        """)
    df = pd.read_sql_query(sql, db.engine)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df['yield_date'], y=df['yield_amount'], mode='lines', name=selected_yield))

    figure.update_layout(title=(f"{selected_dropdown_value}"),
                          xaxis_title='Yield Date',
                          yaxis_title='Yield Amount')

    return figure

#### ==== #### ==== #### ==== #### ==== ####

@app.callback(
    Output('flaring_graph', 'figure'),
    [Input('update_flaring_graph_btn', 'n_clicks')]
)
def update_flaring_graph(n_clicks):
    sql = (f"""
        SELECT Flaring_Date, Flaring_Amount, T_06_ID
        FROM T_06
        WHERE NOT T_06_delete_ind
        ORDER BY Flaring_Date DESC;
        """)
    df = pd.read_sql_query(sql, db.engine)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df['flaring_date'], y=df['flaring_amount'], mode='lines'))

    figure.update_layout(title='Flaring Data',
                          xaxis_title='Flaring Date',
                          yaxis_title='Flaring Amount')

    return figure

#### ==== #### ==== #### ==== #### ==== ####

@app.callback(
    Output('slopping_graph', 'figure'),
    [Input('selected_slopping_store', 'data'), Input('slopping_quality_dropdown_options', 'value')]
)
def update_slopping_graph(selected_slopping, selected_dropdown_value):
    sql = (f"""
        SELECT Slopping_Date, Slopping_Amount, T_07_ID
        FROM T_07
        WHERE NOT T_07_delete_ind AND Slopping_Quality = '{selected_dropdown_value}'
        ORDER BY Slopping_Date DESC;
        """)
    df = pd.read_sql_query(sql, db.engine)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df['slopping_date'], y=df['slopping_amount'], mode='lines', name=selected_slopping))

    figure.update_layout(title=(f"{selected_dropdown_value}"),
                          xaxis_title='Slopping Date',
                          yaxis_title='Slopping Amount')

    return figure

#### ==== #### ==== #### ==== #### ==== ####

@app.callback(
    Output('cokedrum_graph', 'figure'),
    [
        Input('selected_cokedrum_number_store', 'data'), 
        Input('cokedrum_number_dropdown_options', 'value'),
        Input('selected_cokedrum_parameter_store', 'data'), 
        Input('cokedrum_parameter_dropdown_options', 'value')
    ]
)
def update_cokedrum_graph(
    selected_cokedrum_number, 
    selected_cokedrum_number_value,
    selected_cokedrum_parameter, 
    selected_cokedrum_parameter_value,
):
    sql = (f"""
            SELECT Drum_Cycle, {selected_cokedrum_parameter_value}, T_03_ID
            FROM T_03
            WHERE NOT T_03_delete_ind AND Drum_Number = '{selected_cokedrum_number_value}'
        """)
    df = pd.read_sql_query(sql, db.engine)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df['drum_cycle'], y=df[selected_cokedrum_parameter_value.lower()], mode='lines', name=selected_cokedrum_parameter))

    selected_cokedrum_parameter_value = selected_cokedrum_parameter_value.replace("_", " ")

    figure.update_layout(title=(f"{selected_cokedrum_parameter_value}"),
                          xaxis_title='Drum Cycle',
                          yaxis_title=(f"{selected_cokedrum_parameter_value}"))

    return figure

@app.callback(
    Output('heaterCOT_graph', 'figure'),
    [
        Input('selected_heater_number_store', 'data'), 
        Input('heater_number_dropdown_options', 'value'),
        Input('selected_heater_pass_store', 'data'), 
        Input('heater_pass_dropdown_options', 'value'),
        Input('selected_group_by_store', 'data'), 
        Input('group_by_dropdown_options', 'value'),
    ]
)
def update_heaterCOT_graph(
    selected_heater_number, 
    selected_heater_number_value,
    selected_heater_pass, 
    selected_heater_pass_value,
    selected_group_by, 
    selected_group_by_value,
):
    sql = (f"""
            SELECT Heater_Date, Heater_COT, Heater_Flow, T_01_ID
            FROM T_01
            WHERE NOT T_01_delete_ind AND Heater_Number = '{selected_heater_number_value}' 
            AND Heater_Pass= '{selected_heater_pass_value}'
            ORDER BY Heater_Date DESC;
        """)
    df = pd.read_sql_query(sql, db.engine)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=df['heater_date'], y=df[selected_group_by_value.lower()], mode='lines', name=selected_group_by))

    selected_group_by_value = selected_group_by_value.replace("_", " ")

    figure.update_layout(title=(f"{selected_group_by_value}"),
                          xaxis_title='Heater Date',
                          yaxis_title=(f"{selected_group_by_value}"))

    return figure


@app.callback(
    Output('spalling_table', 'children'),
    [Input('update_spalling_tbl_btn', 'n_clicks')]
)
def update_spalling_tbl_graph(n_clicks):
    sql = '''
        WITH LatestSpalling AS (
            SELECT
            Heater_Number,
            Heater_Pass,
            Spalling_Date,
            Spalling_SOR,
            Spalling_EOR,
            ROW_NUMBER() OVER (PARTITION BY Heater_Number, Heater_Pass ORDER BY
            Spalling_Date DESC) AS rn
            FROM
            T_02
        )
        SELECT
        Heater_Number,
        Heater_Pass,
        Spalling_Date,
        Spalling_SOR,
        Spalling_EOR
        FROM
        LatestSpalling
        WHERE
        rn = 1;
          '''
    df = pd.read_sql_query(sql, db.engine)

    column_mapping = {
        'heater_number': 'Heater',
        'heater_pass': 'Pass',
        'spalling_date': 'Date',
        'spalling_sor': 'Start of Run (SOR)',
        'spalling_eor': 'End of Run (EOR)',
    }

    df = df.rename(columns=column_mapping)

    table_header = [html.Th(col) for col in df.columns]
    table_rows = [
        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
        for i in range(len(df))
    ]
    table_body = [html.Tbody(table_rows)]
    table = dbc.Table([html.Thead(table_header)] + table_body, bordered=True)

    return table