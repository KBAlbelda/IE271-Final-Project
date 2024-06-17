from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs

# Importing app and database connection module
from app import app
from apps import dbconnect as db

# Page layout definition
layout = html.Div(
    [
        html.Hr(),  # Horizontal line for separation
        
        # Yields Section
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Yields', className='card-header')),
                dbc.CardBody(
                    [
                        dbc.Button("Add Yield", href='/yields/yield_data?mode=add', className='btn btn-primary'),
                        html.Hr(),
                        html.H3('Sour Coker Fuel Gas'),
                        html.Div(id='yieldFG_datalist'),
                        html.Hr(),
                        html.H3('Sour Coker LPG'),
                        html.Div(id='yieldLPG_datalist'),
                        html.Hr(),
                        html.H3('Coker Naphtha'),
                        html.Div(id='yieldNaphtha_datalist'),
                        html.Hr(),
                        html.H3('Light Coker Gas Oil'),
                        html.Div(id='yieldLCGO_datalist'),
                        html.Hr(),
                        html.H3('Heavy Coker Gas Oil'),
                        html.Div(id='yieldHCGO_datalist'),
                        html.Hr(),
                        html.H3('Petcoke'),
                        html.Div(id='yieldCoke_datalist'),
                    ]
                ),
            ],
            className='card'
        ),

        # Flaring Section
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Flaring', className='card-header')),
                dbc.CardBody(
                    [
                        dbc.Button("Add Flaring", href='/flaring?mode=add', className='btn btn-primary'),
                        html.Hr(),
                        html.Div(id='flaring_datalist'),
                    ]
                ),
            ],
            className='card'
        ),

        # Slopping Section
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Slopping', className='card-header')),
                dbc.CardBody(
                    [
                        dbc.Button("Add Slopping", href='/slopping?mode=add', className='btn btn-primary'),
                        html.Hr(),
                        html.H3('Coker Naphtha'),
                        html.Div(id='sloppingNaphtha_datalist'),
                        html.Hr(),
                        html.H3('Light Coker Gas Oil'),
                        html.Div(id='sloppingLCGO_datalist'),
                        html.Hr(),
                        html.H3('Heavy Coker Gas Oil'),
                        html.Div(id='sloppingHCGO_datalist'),
                        html.Hr(),
                        html.H3('HVGO or VTB'),
                        html.Div(id='sloppingHVGOVTB_datalist'),
                    ]
                ),
            ],
            className='card'
        ),
    ]
)

# Callbacks for loading yield data
def load_yieldsdata_list(yield_stream, output_id):
    @app.callback(
        Output(output_id, 'children'),
        [Input('url', 'pathname')]
    )
    def update_data_list(pathname):
        if pathname == '/yields':
            sql = f""" 
                SELECT Yield_Date, Yield_Amount, T_05_ID
                FROM T_05
                WHERE 
                    NOT T_05_delete_ind AND Yield_Stream = '{yield_stream}'
            """
            values = []
            cols = ['Date', 'Amount', 'ID']
            
            df = db.querydatafromdatabase(sql, values, cols)
            
            if not df.empty:

                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %d, %Y')

                buttons = [html.Div(
                    dbc.Button('Edit', href=f'yields/yield_data?mode=edit&id={data_id}', size='sm', color='warning', className='btn btn-warning'),
                    style={'text-align': 'center'}
                ) for data_id in df['ID']]
                
                df['Action'] = buttons
                df = df[['Date', 'Amount', 'Action']]
                
                table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm', className='table table-hover')
                return [table]
            else:
                return ["No records to display"]
        else:
            raise PreventUpdate

load_yieldsdata_list('Sour Coker Fuel Gas', 'yieldFG_datalist')
load_yieldsdata_list('Sour Coker LPG', 'yieldLPG_datalist')
load_yieldsdata_list('Coker Naphtha', 'yieldNaphtha_datalist')
load_yieldsdata_list('Light Coker Gas Oil', 'yieldLCGO_datalist')
load_yieldsdata_list('Heavy Coker Gas Oil', 'yieldHCGO_datalist')
load_yieldsdata_list('Petcoke', 'yieldCoke_datalist')

# Callback for loading flaring data
@app.callback(
    Output('flaring_datalist', 'children'),
    [Input('url', 'pathname')]
)
def flaring_loaddatalist(pathname):
    if pathname == '/yields':
        sql = """ 
            SELECT Flaring_Date, Flaring_Amount, T_06_ID
            FROM T_06
            WHERE 
                NOT T_06_delete_ind
        """
        values = []
        cols = ['Date', 'Amount', 'ID']
        
        df = db.querydatafromdatabase(sql, values, cols)
        
        if not df.empty:

            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %d, %Y')

            buttons = [html.Div(
                dbc.Button('Edit', href=f'flaring?mode=edit&id={data_id}', size='sm', color='warning', className='btn btn-warning'),
                style={'text-align': 'center'}
            ) for data_id in df['ID']]
            
            df['Action'] = buttons
            df = df[['Date', 'Amount', 'Action']]
            
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm', className='table table-hover')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate

# Callbacks for loading slopping data
def load_sloppingdata_list(Slopping_Quality, output_id):
    @app.callback(
        Output(output_id, 'children'),
        [Input('url', 'pathname')]
    )
    def update_data_list(pathname):
        if pathname == '/yields':
            sql = f""" 
                SELECT Slopping_Date, Slopping_Amount, Slopping_Disposition, T_07_ID
                FROM T_07
                WHERE 
                    NOT T_07_delete_ind AND Slopping_Quality = '{Slopping_Quality}'
            """
            values = []
            cols = ['Date', 'Amount', 'Disposition', 'ID']
            
            df = db.querydatafromdatabase(sql, values, cols)
            
            if not df.empty:

                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %d, %Y')

                buttons = [html.Div(
                    dbc.Button('Edit', href=f'slopping?mode=edit&id={data_id}', size='sm', color='warning', className='btn btn-warning'),
                    style={'text-align': 'center'}
                ) for data_id in df['ID']]
                
                df['Action'] = buttons
                df = df[['Date', 'Amount', 'Disposition', 'Action']]
                
                table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm', className='table table-hover')
                return [table]
            else:
                return ["No records to display"]
        else:
            raise PreventUpdate

load_sloppingdata_list('Coker Naphtha', 'sloppingNaphtha_datalist')
load_sloppingdata_list('Light Coker Gas Oil', 'sloppingLCGO_datalist')
load_sloppingdata_list('Heavy Coker Gas Oil', 'sloppingHCGO_datalist')
load_sloppingdata_list('HVGO or VTB', 'sloppingHVGOVTB_datalist')
