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
                dcc.Store(id='cokedrumdata_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Coke Drum Details'),
        html.Hr(),
        dbc.Alert(id='cokedrumdata_alert', is_open=False),
        
        #### ==== DATA INPUT ==== ####
        
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Drum Number", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='drumdata_drumnumber',
                                options=[
                                        {'label': 'Drum 1', 'value': '1'},
                                        {'label': 'Drum 2', 'value': '2'},
                                        {'label': 'Drum 3', 'value': '3'},
                                        {'label': 'Drum 4', 'value': '4'},
                                ],
                                placeholder="Select a Drum"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Cycle Number", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='drum_cycle',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Foam Level", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='foam_level',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Coke Level", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='coke_level',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Coking Pressure", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='drum_pressure',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Overhead DP", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='drum_dp',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Coking Temperature", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='drum_temperature',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Switching Temperature", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='switch_temperature',
                                placeholder="0"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Chemical", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='chemical_list',
                                placeholder='Chemical'
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Chemical Injection Rate", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='number', 
                                id='antifoam_rate',
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
                            id='cokedrumdata_removerecord',
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
            id='cokedrumdata_removerecord_div'
        ),

        #### ==== SUBMIT BUTTON ==== ####

        dbc.Button(
            'Submit',
            id='cokedrumdata_submit',
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
            id='cokedrumdata_successmodal',
            backdrop='static'
        )
    ]
)

#### ==== #### ==== CHECKING THE MODE ==== #### ==== ####
@app.callback(
    [
        Output('chemical_list', 'options'),
        Output('cokedrumdata_toload', 'data'),
        Output('cokedrumdata_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def chemicals_loaddropdown(pathname, search):
    
    if pathname == '/coke-drums/drum_data':

        #### ==== GET DROP DOWN ==== ####

        sql = """
            SELECT chemical_name as label, T_04_ID as value
            FROM T_04
            WHERE T_04_DELETE_IND = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        chemical_opts = df.to_dict('records')
        
        #### ==== ADD OR EDIT MODE ==== ####

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        
        #### ==== CHECK BOX ==== ####

        removediv_style = {'display': 'none'} if not to_load else None  
    
    else:
        raise PreventUpdate

    return [chemical_opts, to_load, removediv_style]

#### ==== #### ==== SAVING THE DATA ==== #### ==== ####
@app.callback(
    [
        Output('cokedrumdata_alert', 'color'),
        Output('cokedrumdata_alert', 'children'),
        Output('cokedrumdata_alert', 'is_open'),
        Output('cokedrumdata_successmodal', 'is_open')
    ],
    [
        Input('cokedrumdata_submit', 'n_clicks')
    ],
    [
        State('drumdata_drumnumber', 'value'),
        State('drum_cycle', 'value'),
        State('foam_level', 'value'),
        State('coke_level', 'value'),
        State('drum_pressure', 'value'),
        State('drum_dp', 'value'),
        State('drum_temperature', 'value'),
        State('switch_temperature', 'value'),
        State('chemical_list', 'value'),
        State('antifoam_rate', 'value'),
        State('url', 'search'),
        State('cokedrumdata_removerecord', 'value'),
    ]
)
def cokedrumdata_save(submitbtn, drumdata_drumnumber, drumcycle, foamlevel, cokelevel, drumpressure, drumdp, drumtemperature, switchtemperature, chemicallist, antifoamrate, search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'cokedrumdata_submit' and submitbtn:

            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not drumdata_drumnumber:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not drumcycle:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not foamlevel:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not cokelevel:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not drumpressure:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'                
            elif not drumdp:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not drumtemperature:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'            
            elif not switchtemperature:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'            
            elif not chemicallist:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            elif not antifoamrate:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Missing Input.'
            else:
 
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                
                #### ==== ADDING NEW DATA ==== ####

                if create_mode == 'add':

                    sql = '''
                        INSERT INTO T_03 (Drum_Number, Drum_Cycle, Foam_Level, Coke_Level, Drum_Pressure, Drum_DP, Drum_Temperature, Switch_Temperature, T_04_ID, Antifoam_Rate, T_03_DELETE_IND)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    values = [ drumdata_drumnumber, drumcycle, foamlevel, cokelevel, drumpressure, drumdp, drumtemperature, switchtemperature, chemicallist, antifoamrate, False]

                    db.modifydatabase(sql, values)
                    modal_open = True
                    
                #### ==== EDITING NEW DATA ==== ####

                elif create_mode == 'edit':
                    parsed = urlparse(search)
                    cokedrumdataid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE T_03
                    SET
                        Drum_Number = %s,
                        Drum_Cycle = %s,
                        Foam_Level = %s,
                        Coke_Level = %s,
                        Drum_Pressure = %s,
                        Drum_DP = %s,
                        Drum_Temperature = %s,
                        Switch_Temperature = %s,
                        T_04_ID = %s,
                        Antifoam_Rate = %s,
                        T_03_DELETE_IND = %s
                    WHERE
                        T_03_ID = %s
                    """
                    to_delete = bool(removerecord)
                    values = [ drumdata_drumnumber, drumcycle, foamlevel, cokelevel, drumpressure, drumdp, drumtemperature, switchtemperature, chemicallist, antifoamrate, to_delete, cokedrumdataid]

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
        Output('drumdata_drumnumber', 'value'),
        Output('drum_cycle', 'value'),
        Output('foam_level', 'value'),
        Output('coke_level', 'value'),
        Output('drum_pressure', 'value'),
        Output('drum_dp', 'value'),
        Output('drum_temperature', 'value'),
        Output('switch_temperature', 'value'),
        Output('chemical_list', 'value'),
        Output('antifoam_rate', 'value'),
    ],
    [
        Input('cokedrumdata_toload', 'modified_timestamp')
    ],
    [
        State('cokedrumdata_toload', 'data'),
        State('url', 'search'),
    ]
)

def cokedrumdata_load(timestamp, toload, search):
    if not toload:
        raise PreventUpdate
    
    parsed = urlparse(search)
    cokedrumdataid = parse_qs(parsed.query).get('id', [None])[0]
    if cokedrumdataid:
        sql = """
            SELECT Drum_Number, Drum_Cycle, Foam_Level, Coke_Level, Drum_Pressure, Drum_DP, Drum_Temperature, Switch_Temperature, T_04_ID, Antifoam_Rate
            FROM T_03
            WHERE T_03_ID = %s
        """
        values = [cokedrumdataid]
        col = ['drumnumber', 'drumcycle', 'foamlevel', 'cokelevel', 'drumpressure', 'drumdp', 'drumtemperature', 'switchtemperature', 't04id', 'antifoamrate']

        df = db.querydatafromdatabase(sql, values, col)
        if not df.empty:
            drumnumber = df['drumnumber'][0]
            drumcycle = df['drumcycle'][0]
            foamlevel = df['foamlevel'][0]
            cokelevel = df['cokelevel'][0]
            drumpressure = df['drumpressure'][0]
            drumdp = df['drumdp'][0]
            drumtemperature = df['drumtemperature'][0]
            switchtemperature = df['switchtemperature'][0]
            t04id = df['t04id'][0]
            antifoamrate = df['antifoamrate'][0]

            return [drumnumber, drumcycle, foamlevel, cokelevel, drumpressure, drumdp, drumtemperature, switchtemperature, t04id, antifoamrate]
    
    return [None, None, None, None, None]


