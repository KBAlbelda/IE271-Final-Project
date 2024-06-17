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
                dcc.Store(id='cokerheatersspalling_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Spalling Details'),
        html.Hr(),
        dbc.Alert(id='cokerheatersspalling_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='heaterspalling_date',
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
                                id='heaterspalling_heaternumber',
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
                                id='heaterspalling_heaterpass',
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
                        dbc.Label("Start of Run", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='heaterspalling_SOR',
                                placeholder="677"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("End of Run", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='heaterspalling_EOR',
                                placeholder="580"
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
                            id='cokerheatersspalling_removerecord',
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
            id='cokerheatersspalling_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='cokerheatersspalling_submit',
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
            id='cokerheatersspalling_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== SAVING THE DATA ==== #### ==== ####
@app.callback(
    [
        Output('cokerheatersspalling_alert', 'color'),
        Output('cokerheatersspalling_alert', 'children'),
        Output('cokerheatersspalling_alert', 'is_open'),
        Output('cokerheatersspalling_successmodal', 'is_open')
    ],
    [
        Input('cokerheatersspalling_submit', 'n_clicks')
    ],
    [
        State('heaterspalling_date', 'date'),
        State('heaterspalling_heaternumber', 'value'),
        State('heaterspalling_heaterpass', 'value'),
        State('heaterspalling_SOR', 'value'),
        State('heaterspalling_EOR', 'value'),
        State('url', 'search'),
        State('cokerheatersspalling_removerecord', 'value'),
    ]
)
def cokerheatersspalling_save(submitbtn, date, heaternumber, heaterpass, SOR, EOR, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'cokerheatersspalling_submit' and submitbtn:

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
            elif not SOR:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'                
            elif not EOR:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_02 (Spalling_Date, Heater_Number, Heater_Pass, Spalling_SOR, Spalling_EOR, T_02_DELETE_IND)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    '''
                    values = [ date, heaternumber, heaterpass, SOR, EOR, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    cokerheatersspallingid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_02
                    SET
                        Spalling_Date = %s,
                        Heater_Number= %s,
                        Heater_Pass= %s,
                        Spalling_SOR = %s,
                        Spalling_EOR= %s,
                        T_02_DELETE_IND = %s
                    WHERE
                        T_02_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ date, heaternumber, heaterpass, SOR, EOR, to_delete, cokerheatersspallingid]

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
        Output('cokerheatersspalling_toload', 'data'),
        Output('cokerheatersspalling_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def spalling_loaddropdown(pathname, search):
    
    if pathname == '/coker-heaters/spalling_data':
        
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
        Output('heaterspalling_date', 'date'),
        Output('heaterspalling_heaternumber', 'value'),
        Output('heaterspalling_heaterpass', 'value'),
        Output('heaterspalling_SOR', 'value'),
        Output('heaterspalling_EOR', 'value'),
    ],
    [
        Input('cokerheatersspalling_toload', 'modified_timestamp')
    ],
    [
        State('cokerheatersspalling_toload', 'data'),
        State('url', 'search'),
    ]
)
def cokerheatersspalling_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    cokerheatersspallingid = parse_qs(parsed.query).get('id', [None])[0]
    if cokerheatersspallingid:
        sql = """
            SELECT Spalling_Date, Heater_Number, Heater_Pass, Spalling_SOR, Spalling EOR
            FROM T_02
            WHERE T_02_ID = %s
        """
        values = [cokerheatersspallingid]
        col = ['spallingdate', 'heaternumber', 'heaterpass', 'spallingSOR', 'spallingEOR']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            spallingdate = df['spallingdate'][0]
            heaternumber = df['heaternumber'][0]
            heaterpass = df['heaterpass'][0]
            spallingSOR = df['spallingSOR'][0]
            spallingEOR = df['spallingEOR'][0]

            return [spallingdate, heaternumber, heaterpass, spallingSOR, spallingEOR]
    
    return [None, None, None, None, None]