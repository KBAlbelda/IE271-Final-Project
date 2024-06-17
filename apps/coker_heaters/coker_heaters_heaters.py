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
     
        #### ==== RESET DATA ==== ####

        html.Div(
            [
                dcc.Store(id='cokerheatersdata_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Coker Heater Details'),
        html.Hr(),
        dbc.Alert(id='cokerheatersdata_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='heaterdata_date',
                                placeholder="Select a Date",
                                display_format="DD/MMM/YYYY",
                                style={'width': '100%'}
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Heater", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='heaterdata_heaternumber',
                                options=[
                                        {'label': 'Heater 1', 'value': '1'},
                                        {'label': 'Heater 2', 'value': '2'},
                                ],
                                placeholder="Select a Heater"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Pass", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='heaterdata_heaterpass',
                                options=[
                                        {'label': 'Pass 1', 'value': '1'},
                                        {'label': 'Pass 2', 'value': '2'},
                                        {'label': 'Pass 3', 'value': '3'},                                        
                                ],
                                placeholder="Select a Heater Pass"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Heater Coil Outlet Temperature", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='heaterdata_cot',
                                placeholder="500"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Heater Pass Flow", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='heaterdata_flow',
                                placeholder="800"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
            ]
        ),
        
        #### ==== DELETE CHECK MARK ==== ####

        html.Div(
            dbc.Row(
                [
                    dbc.Label("Delete Data?", width=2),
                    dbc.Col(
                        dbc.Checklist(
                            id='cokerheatersdata_removerecord',
                            options=[
                                {
                                    'label': "Mark for Deletion",
                                    'value': 1
                                }
                            ],
                            style={'fontWeight':'bold'}, 
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id='cokerheatersdata_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='cokerheatersdata_submit',
            n_clicks=0
        ),
        
        #### ==== TRIGGER PROMPT THAT IS WAS SUCCESSFUL ==== ####
        
        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Submission Successful'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/coker-heaters'
                    )
                )
            ],
            centered=True,
            id='cokerheatersdata_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== SAVING THE DATA ==== #### ==== ####
@app.callback(
    [
        Output('cokerheatersdata_alert', 'color'),
        Output('cokerheatersdata_alert', 'children'),
        Output('cokerheatersdata_alert', 'is_open'),
        Output('cokerheatersdata_successmodal', 'is_open')
    ],
    [
        Input('cokerheatersdata_submit', 'n_clicks')
    ],
    [
        State('heaterdata_date', 'date'),
        State('heaterdata_heaternumber', 'value'),
        State('heaterdata_heaterpass', 'value'),
        State('heaterdata_cot', 'value'),
        State('heaterdata_flow', 'value'),
        State('url', 'search'),
        State('cokerheatersdata_removerecord', 'value'),
    ]
)
def cokerheatersdata_save(submitbtn, date, heaternumber, heaterpass, COT, Flow, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'cokerheatersdata_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not date:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not heaternumber:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not heaterpass:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not COT:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'                
            elif not Flow:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_01 (Heater_Date, Heater_Number, Heater_Pass, Heater_COT, Heater_Flow, T_01_DELETE_IND)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                    values = [ date, heaternumber, heaterpass, COT, Flow, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    cokerheatersdataid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_01
                    SET
                        Heater_Date = %s,
                        Heater_Number= %s,
                        Heater_Pass= %s,
                        Heater_COT = %s,
                        Heater_Flow= %s,
                        T_01_DELETE_IND = %s
                    WHERE
                        T_01_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ date, heaternumber, heaterpass, COT, Flow, to_delete, cokerheatersdataid]

                    db.modifydatabase(sqlcode, values)

                    modal_open = True


            return [alert_color, alert_text, alert_open, modal_open]

        else:
            raise PreventUpdate

    else:
        raise PreventUpdate

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####

@app.callback(
    [
        Output('cokerheatersdata_toload', 'data'),
        Output('cokerheatersdata_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def heaters_loaddropdown(pathname, search):
    
    if pathname == '/coker-heaters/heater_data':
        
        #### ==== ADD OR EDIT MODE ==== ####

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        
        #### ==== CHECK BOX ==== ####

        removediv_style = {'display': 'none'} if not to_load else None    
    else:
        raise PreventUpdate
    return [to_load, removediv_style]

#### ==== #### ==== LOADING THE DATA ==== #### ==== ####
@app.callback(
    [
        Output('heaterdata_date', 'date'),
        Output('heaterdata_heaternumber', 'value'),
        Output('heaterdata_heaterpass', 'value'),
        Output('heaterdata_cot', 'value'),
        Output('heaterdata_flow', 'value'),
    ],
    [
        Input('cokerheatersdata_toload', 'modified_timestamp')
    ],
    [
        State('cokerheatersdata_toload', 'data'),
        State('url', 'search'),
    ]
)

def cokerheatersdata_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    cokerheatersdataid = parse_qs(parsed.query).get('id', [None])[0]
    if cokerheatersdataid:
        sql = """
            SELECT Heater_Date, Heater_Number, Heater_Pass, Heater_COT, Heater_Flow
            FROM T_01
            WHERE T_01_ID = %s
        """
        values = [cokerheatersdataid]
        col = ['heaterdate', 'heaternumber', 'heaterpass', 'heaterCOT', 'heaterflow']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            heaterdate = df['heaterdate'][0]
            heaternumber = df['heaternumber'][0]
            heaterpass = df['heaterpass'][0]
            heaterCOT = df['heaterCOT'][0]
            heaterflow = df['heaterflow'][0]

            return [heaterdate, heaternumber, heaterpass, heaterCOT, heaterflow]
    
    return [None, None, None, None, None]
