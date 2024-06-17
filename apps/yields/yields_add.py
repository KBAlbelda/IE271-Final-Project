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
                dcc.Store(id='yieldsdata_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Add DCU Yield'),
        html.Hr(),
        dbc.Alert(id='yieldsdata_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='yields_date',
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
                        dbc.Label("Stream", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='yields_stream',
                                options=[
                                        {'label': 'Sour Coker Fuel Gas', 'value': 'Sour Coker Fuel Gas'},
                                        {'label': 'Sour Coker LPG', 'value': 'Sour Coker LPG'},
                                        {'label': 'Coker Naphtha', 'value': 'Coker Naphtha'},
                                        {'label': 'Light Coker Gas Oil (LCGO)', 'value': 'Light Coker Gas Oil'},
                                        {'label': 'Heavy Coker Gas Oil (HCGO)', 'value': 'Heavy Coker Gas Oil'},
                                        {'label': 'Petcoke', 'value': 'Petcoke'},
                                ],
                                placeholder="Select a Stream"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Amount", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='yields_amount',
                                placeholder="0"
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
                            id='yieldsdata_removerecord',
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
            id='yieldsdata_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='yieldsdata_submit',
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
                        href='/yields'
                    )
                )
            ],
            centered=True,
            id='yieldsdata_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####

@app.callback(
    [
        Output('yieldsdata_toload', 'data'),
        Output('yieldsdata_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def yields_loaddropdown(pathname, search):
    
    if pathname == '/yields/yield_data':
        
        #### ==== ADD OR EDIT MODE ==== ####

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        
        #### ==== CHECK BOX ==== ####

        removediv_style = {'display': 'none'} if not to_load else None    
    else:
        raise PreventUpdate
    return [to_load, removediv_style]


#### ==== #### ==== SAVING THE DATA ==== #### ==== ####
@app.callback(
    [
        Output('yieldsdata_alert', 'color'),
        Output('yieldsdata_alert', 'children'),
        Output('yieldsdata_alert', 'is_open'),
        Output('yieldsdata_successmodal', 'is_open')
    ],
    [
        Input('yieldsdata_submit', 'n_clicks')
    ],
    [
        State('yields_date', 'date'),
        State('yields_stream', 'value'),
        State('yields_amount', 'value'),
        State('url', 'search'),
        State('yieldsdata_removerecord', 'value'),
    ]
)
def yieldsdata_save(submitbtn, date, stream, amount, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'yieldsdata_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not date:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not stream:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not amount:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_05 (Yield_Date, Yield_Stream, Yield_Amount, T_05_DELETE_IND)
                        VALUES (%s, %s, %s, %s)
                    '''
                    values = [ date, stream, amount, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    yieldsdataid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_05
                    SET
                        Yield_Date = %s,
                        Yield_Stream= %s,
                        Yield_Amount= %s,
                        T_05_DELETE_IND = %s
                    WHERE
                        T_05_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ date, stream, amount, to_delete, yieldsdataid]

                    db.modifydatabase(sqlcode, values)

                    modal_open = True


            return [alert_color, alert_text, alert_open, modal_open]

        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

#### ==== #### ==== LOADING THE DATA ==== #### ==== ####

@app.callback(
    [
        Output('yieldsdata_date', 'date'),
        Output('yieldsdata_stream', 'value'),
        Output('yieldsdata_amount', 'value'),
    ],
    [
        Input('yieldsdata_toload', 'modified_timestamp')
    ],
    [
        State('yieldsdata_toload', 'data'),
        State('url', 'search'),
    ]
)
def yieldsdata_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    yieldsdataid = parse_qs(parsed.query).get('id', [None])[0]
    if yieldsdataid:
        sql = """
            SELECT Yield_Date, Yield_Stream, Yield_Amount
            FROM T_05
            WHERE T_05_ID = %s
        """
        values = [yieldsdataid]
        col = ['yielddate', 'yieldstream', 'yieldamount']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            yielddate = df['yielddate'][0]
            yieldstream = df['yieldstream'][0]
            yieldamount = df['yieldamount'][0]

            return [yielddate, yieldstream, yieldamount]
    
    return [None, None, None, None, None]
