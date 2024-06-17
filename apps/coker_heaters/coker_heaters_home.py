from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs

#### ==== #### ==== #### ==== #### ==== ####

from app import app
from apps import dbconnect as db

#### ==== #### ==== PAGE LAYOUT ==== #### ==== ####

layout = html.Div(
    [

        #### ==== MAIN OUTLINE ==== ####

        html.H2('Coker Heaters'),
        html.Hr(),
        
        #### ==== COKER HEATER DATA INCLUDING COT ==== ####
        
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Coker Heater Data')
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Heater Pass Data",
                                    href='/coker-heaters/heater_data?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.Div(
                                    "Table with heater data will go here.",
                                    id='cokerheatershome_datalist'
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        #### ==== COKER HEATER SPALLING ==== ####
        
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Spalling History')
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Spalling",
                                    href='/coker-heaters/spalling_data?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.Div(
                                    "Table with Spalling Records will go here.",
                                    id='cokerheatershome_spallinglist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

#### ==== #### ==== LOAD HEATER DATA LIST ==== #### ==== ####

@app.callback(
    [
        Output('cokerheatershome_datalist', 'children')
    ],
    [
        Input('url', 'pathname'),
    ]
)
def cokerheatershome_loaddatalist(pathname):
    if pathname == '/coker-heaters':
        sql = """ 
            SELECT Heater_Date, Heater_Number, Heater_Pass, Heater_COT, Heater_Flow, T_01_ID
            FROM T_01
            WHERE 
                NOT T_01_delete_ind
            """
        values = []
        cols = ['Date', 'Heater', 'Pass', 'COT', 'Flow', 'ID']
        
        df = db.querydatafromdatabase(sql, values, cols)
        
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %d, %Y')

        if df.shape:
            buttons01 = []
            for data_id in df['ID']:
                buttons01 += [
                    html.Div(
                        dbc.Button('Edit', href=f'coker-heaters/heater_data?mode=edit&id={data_id}',
                                   size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            
            df['Action'] = buttons01
            
            df = df[['Date', 'Heater', 'Pass', 'COT', 'Flow', 'Action']]

            table01 = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                    hover=True, size='sm')
            return [table01]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate

#### ==== #### ==== SPALLING RECORDS LIST ==== #### ==== ####

@app.callback(
    [
        Output('cokerheatershome_spallinglist', 'children')
    ],
    [
        Input('url', 'pathname'),
    ]
)
def cokerheatershome_loadspallinglist(pathname):
    if pathname == '/coker-heaters':
        sql = """ 
            SELECT Spalling_Date, Heater_Number, Heater_Pass, Spalling_SOR, Spalling_EOR, T_02_ID
            FROM T_02
            WHERE 
                NOT T_02_delete_ind
            """
        values = []
        cols = ['Date', 'Heater', 'Pass', 'Start of Run', 'End of Run', 'ID']
        
        df = db.querydatafromdatabase(sql, values, cols)
        
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %d, %Y')

        if df.shape:
            buttons02 = []
            for spalling_id in df['ID']:
                buttons02 += [
                    html.Div(
                        dbc.Button('Edit', href=f'coker-heaters/spalling_data?mode=edit&id={spalling_id}',
                                   size='sm', color='warning'),
                        style={'text-align': 'center'}
                    )
                ]
            
            df['Action'] = buttons02
            
            df = df[['Date', 'Heater', 'Pass', 'Start of Run', 'End of Run', 'Action']]

            table02 = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                    hover=True, size='sm')
            return [table02]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate