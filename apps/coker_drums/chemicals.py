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
                dcc.Store(id='chemical_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Coke Drum Chemicals'),
        html.Hr(),
        dbc.Alert(id='chemical_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Chemical Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='string', 
                                id='chemical_name',
                                placeholder="Enter chemical name here"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Chemical Service", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='string', 
                                id='chemical_service',
                                placeholder="Enter the service of the chemical here"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Chemical Supplier", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='string', 
                                id='chemical_supplier',
                                placeholder="Enter chemical supplier here"
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
                            id='chemical_removerecord',
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
            id='chemical_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='chemical_submit',
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
                        href='/coke-drums'
                    )
                )
            ],
            centered=True,
            id='chemical_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####

@app.callback(
    [
        Output('chemical_toload', 'data'),
        Output('chemical_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def chemical_loaddropdown(pathname, search):
    
    if pathname == '/chemicals':
        
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
        Output('chemical_alert', 'color'),
        Output('chemical_alert', 'children'),
        Output('chemical_alert', 'is_open'),
        Output('chemical_successmodal', 'is_open')
    ],
    [
        Input('chemical_submit', 'n_clicks')
    ],
    [
        State('chemical_name', 'value'),
        State('chemical_service', 'value'),
        State('chemical_supplier', 'value'),
        State('url', 'search'),
        State('chemical_removerecord', 'value'),
    ]
)
def chemical_save(submitbtn, name, service, supplier, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'chemical_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not name:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not service:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not supplier:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_04 (Chemical_Name, Chemical_Service, Chemical_Supplier, T_04_DELETE_IND)
                        VALUES (%s, %s, %s, %s)
                    '''
                    values = [ name, service, supplier, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    chemicalid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_04
                    SET
                        Chemical_Name = %s,
                        Chemical_Service = %s,
                        Chemical_Supplier = %s,
                        T_04_DELETE_IND = %s
                    WHERE
                        T_04_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ name, service, supplier, to_delete, chemicalid]

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
        Output('chemical_name', 'value'),
        Output('chemical_service', 'value'),
        Output('chemical_supplier', 'value'),
    ],
    [
        Input('chemical_toload', 'modified_timestamp')
    ],
    [
        State('chemical_toload', 'data'),
        State('url', 'search'),
    ]
)
def chemical_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    chemicalid = parse_qs(parsed.query).get('id', [None])[0]
    if chemicalid:
        sql = """
            SELECT Chemical_Name, Chemical_Service, Chemical_Supplier
            FROM T_04
            WHERE T_04_ID = %s
        """
        values = [chemicalid]
        col = ['chemicalname', 'chemicalservice', 'chemicalsupplier']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            chemicalname = df['chemicalname'][0]
            chemicalservice = df['chemicalservice'][0]
            chemicalsupplier = df['chemicalsupplier'][0]

            return [ chemicalname,chemicalservice, chemicalsupplier]

    return [None, None, None, None, None]