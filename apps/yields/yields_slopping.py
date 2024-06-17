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
                dcc.Store(id='sloppingdata_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Add Slopping Data'),
        html.Hr(),
        dbc.Alert(id='sloppingdata_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='slopping_date',
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
                        dbc.Label("Quality", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='slopping_quality',
                                options=[
                                        {'label': 'Coker Naphtha', 'value': 'Coker Naphtha'},
                                        {'label': 'Light Coker Gas Oil (LCGO)', 'value': 'Light Coker Gas Oil'},
                                        {'label': 'Heavy Coker Gas Oil (HCGO)', 'value': 'Heavy Coker Gas Oil'},
                                        {'label': 'HVGO or VTB', 'value': 'HVGO or VTB'},
                                ],
                                placeholder="Select a Quality"
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
                                id='slopping_amount',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Disposition", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='string', 
                                id='slopping_disposition',
                                placeholder="Enter Disposition"
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
                            id='sloppingdata_removerecord',
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
            id='sloppingdata_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='sloppingdata_submit',
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
            id='sloppingdata_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####

@app.callback(
    [
        Output('sloppingdata_toload', 'data'),
        Output('sloppingdata_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def slopping_loaddropdown(pathname, search):
    
    if pathname == '/slopping':
        
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
        Output('sloppingdata_alert', 'color'),
        Output('sloppingdata_alert', 'children'),
        Output('sloppingdata_alert', 'is_open'),
        Output('sloppingdata_successmodal', 'is_open')
    ],
    [
        Input('sloppingdata_submit', 'n_clicks')
    ],
    [
        State('slopping_date', 'date'),
        State('slopping_quality', 'value'),
        State('slopping_amount', 'value'),
        State('slopping_disposition', 'value'),
        State('url', 'search'),
        State('sloppingdata_removerecord', 'value'),
    ]
)
def sloppingdata_save(submitbtn, date, quality, amount, disposition, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'sloppingdata_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not date:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not quality:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not amount:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not disposition:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_07 (Slopping_Date, Slopping_Quality, Slopping_Amount, Slopping_Disposition, T_07_DELETE_IND)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    values = [ date, quality, amount, disposition, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    sloppingdataid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_07
                    SET
                        Slopping_Date = %s,
                        Slopping_Quality= %s,
                        Slopping_Amount= %s,
                        Slopping_Disposition= %s,
                        T_07_DELETE_IND = %s
                    WHERE
                        T_07_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ date, quality, amount, disposition, to_delete, sloppingdataid]

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
        Output('sloppingdata_date', 'date'),
        Output('sloppingdata_quality', 'value'),
        Output('sloppingdata_amount', 'value'),
        Output('sloppingdata_disposition', 'value'),        
    ],
    [
        Input('sloppingdata_toload', 'modified_timestamp')
    ],
    [
        State('sloppingdata_toload', 'data'),
        State('url', 'search'),
    ]
)
def sloppingdata_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    sloppingdataid = parse_qs(parsed.query).get('id', [None])[0]
    if sloppingdataid:
        sql = """
            SELECT Slopping_Date, Slopping_Quality, Slopping_Amount, Slopping_Disposition
            FROM T_07
            WHERE T_07_ID = %s
        """
        values = [sloppingdataid]
        col = ['sloppingdate', 'sloppingquality','sloppingamount', 'sloppingdisposition']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            sloppingdate = df['sloppingdate'][0]
            sloppingquality = df['sloppingquality'][0]            
            sloppingamount = df['sloppingamount'][0]
            sloppingdisposition = df['sloppingdisposition'][0]

            return [sloppingdate, sloppingquality, sloppingamount, sloppingdisposition]
    
    return [None, None, None, None, None]