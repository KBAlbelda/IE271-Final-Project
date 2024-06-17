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
        
        html.H2('Coke Drums'),
        html.Hr(),
        
        #### ==== COKE DRUM DATA ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Coke Drum Data')),
                dbc.CardBody(
                    [
                        dbc.Button("Add Coke Drum Data", href='/coke-drums/drum_data?mode=add'),
                        html.Hr(),
                        html.H3('Drum 1'),
                        html.Div("Table with Drum 1 data will go here.", id='cokedrum1home_datalist'),
                        html.Hr(),
                        html.H3('Drum 2'),
                        html.Div("Table with Drum 2 data will go here.", id='cokedrum2home_datalist'),
                        html.Hr(),
                        html.H3('Drum 3'),
                        html.Div("Table with Drum 3 data will go here.", id='cokedrum3home_datalist'),
                        html.Hr(),
                        html.H3('Drum 4'),
                        html.Div("Table with Drum 4 data will go here.", id='cokedrum4home_datalist')
                    ]
                )
            ]
        ),

        #### ==== CHEMICALS ==== ####

        dbc.Card(
            [
                dbc.CardHeader(html.H3('Chemicals')),
                dbc.CardBody(
                    [
                        dbc.Button("Add Chemical", href='/chemicals?mode=add'),
                        html.Hr(),
                        html.Div("Table with Chemicals will go here.", id='chemicals_list')
                    ]
                )
            ]
        )
    ]
)

#### ==== CALLBACKS ==== ####

def load_data_list(drum_number, output_id):
    @app.callback(
        Output(output_id, 'children'),
        [Input('url', 'pathname')]
    )
    def update_data_list(pathname):
        if pathname == '/coke-drums':
            sql = f""" 
                SELECT Drum_Cycle, Foam_Level, Coke_Level, Drum_Pressure, Drum_DP, Drum_Temperature, Switch_Temperature, Chemical_Name, Antifoam_Rate, T_03_ID
                FROM T_03 t
                INNER JOIN T_04 f on t.T_04_ID = f.T_04_ID
                WHERE 
                    NOT T_03_delete_ind AND Drum_Number = '{drum_number}'
                """
            values = []
            cols = ['Cycle', 'Foam', 'Coke', 'Pressure', 'DP', 'Temperature', 'Switching', 'Chemical', 'Rate', 'ID']
            
            df = db.querydatafromdatabase(sql, values, cols)
            
            if not df.empty:
                buttons = [html.Div(
                    dbc.Button('Edit', href=f'coke-drums/drum_data?mode=edit&id={data_id}', size='sm', color='warning'),
                    style={'text-align': 'center'}
                ) for data_id in df['ID']]
                
                df['Action'] = buttons
                df = df[['Cycle', 'Foam', 'Coke', 'Pressure', 'DP', 'Temperature', 'Switching', 'Chemical', 'Rate', 'Action']]

                table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm')
                return [table]
            else:
                return ["No records to display"]
        else:
            raise PreventUpdate

load_data_list('1', 'cokedrum1home_datalist')
load_data_list('2', 'cokedrum2home_datalist')
load_data_list('3', 'cokedrum3home_datalist')
load_data_list('4', 'cokedrum4home_datalist')

@app.callback(
    Output('chemicals_list', 'children'),
    [Input('url', 'pathname')]
)
def chemicals_loaddatalist(pathname):
    if pathname == '/coke-drums':
        sql = """ 
            SELECT Chemical_Name, Chemical_Service, Chemical_Supplier, T_04_ID
            FROM T_04
            WHERE 
                NOT T_04_delete_ind
            """
        values = []
        cols = ['Chemical', 'Service', 'Supplier', 'ID']
        
        df = db.querydatafromdatabase(sql, values, cols)
        
        if not df.empty:
            buttons = [html.Div(
                dbc.Button('Edit', href=f'chemicals?mode=edit&id={data_id}', size='sm', color='warning'),
                style={'text-align': 'center'}
            ) for data_id in df['ID']]
            
            df['Action'] = buttons
            df = df[['Chemical', 'Service', 'Supplier', 'Action']]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate
