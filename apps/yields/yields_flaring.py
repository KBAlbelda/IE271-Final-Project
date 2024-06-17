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
                dcc.Store(id='flaringdata_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Add Flaring Data'),
        html.Hr(),
        dbc.Alert(id='flaringdata_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='flaring_date',
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
                        dbc.Label("Amount", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='flaring_amount',
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
                            id='flaringdata_removerecord',
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
            id='flaringdata_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='flaringdata_submit',
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
            id='flaringdata_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####

@app.callback(
    [
        Output('flaringdata_toload', 'data'),
        Output('flaringdata_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def flaring_loaddropdown(pathname, search):
    
    if pathname == '/flaring':
        
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
        Output('flaringdata_alert', 'color'),
        Output('flaringdata_alert', 'children'),
        Output('flaringdata_alert', 'is_open'),
        Output('flaringdata_successmodal', 'is_open')
    ],
    [
        Input('flaringdata_submit', 'n_clicks')
    ],
    [
        State('flaring_date', 'date'),
        State('flaring_amount', 'value'),
        State('url', 'search'),
        State('flaringdata_removerecord', 'value'),
    ]
)
def flaringdata_save(submitbtn, date, amount, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'flaringdata_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not date:
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
                        INSERT INTO T_06 (Flaring_Date, Flaring_Amount, T_06_DELETE_IND)
                        VALUES (%s, %s, %s)
                    '''
                    values = [ date, amount, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    flaringdataid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_06
                    SET
                        Flaring_Date = %s,
                        Flaring_Amount= %s,
                        T_06_DELETE_IND = %s
                    WHERE
                        T_06_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ date, amount, to_delete, flaringdataid]

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
        Output('flaringdata_date', 'date'),
        Output('flaringdata_amount', 'value'),
    ],
    [
        Input('flaringdata_toload', 'modified_timestamp')
    ],
    [
        State('flaringdata_toload', 'data'),
        State('url', 'search'),
    ]
)
def flaringdata_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    flaringdataid = parse_qs(parsed.query).get('id', [None])[0]
    if flaringdataid:
        sql = """
            SELECT Flaring_Date, Flaring_Amount
            FROM T_06
            WHERE T_06_ID = %s
        """
        values = [flaringdataid]
        col = ['flaringdate', 'flaringamount']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            flaringdate = df['flaringdate'][0]
            flaringamount = df['flaringamount'][0]

            return [flaringdate, flaringamount]
    
    return [None, None, None, None, None]
