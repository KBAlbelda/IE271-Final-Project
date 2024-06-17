from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from apps import callback

#### ==== #### ==== #### ==== #### ==== ####

from apps import callback

#### ==== #### ==== PAGE LAYOUT ==== #### ==== ####

layout = html.Div(
    [
        #### ==== YIELDS DATA ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('DCU Yields')),
                dbc.CardBody(
                    [
                        dcc.Dropdown(
                            id='yield_stream_dropdown_options',
                            options=[
                                {'label': 'Sour Coker Fuel Gas', 'value': 'Sour Coker Fuel Gas'},
                                {'label': 'Sour Coker LPG', 'value': 'Sour Coker LPG'},
                                {'label': 'Coker Naphtha', 'value': 'Coker Naphtha'},
                                {'label': 'Light Coker Gas Oil (LCGO)', 'value': 'Light Coker Gas Oil'},
                                {'label': 'Heavy Coker Gas Oil (HCGO)', 'value': 'Heavy Coker Gas Oil'},
                                {'label': 'Petcoke', 'value': 'Petcoke'},
                            ],   
                            value='Sour Coker Fuel Gas'                       
                        ),
                        dcc.Store(id='selected_yield_store'),
                        dcc.Graph(id='yields_graph')
                    ]
                )
            ]
        ),

        #### ==== FLARING DATA ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Flaring Data')),
                dbc.CardBody(
                    [
                        dcc.Graph(id='flaring_graph'),
                        dbc.Button("Refresh", id='update_flaring_graph_btn')
                    ]
                )
            ]
        ),

        #### ==== SLOPPING DATA ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Slopping')),
                dbc.CardBody(
                    [
                        dcc.Dropdown(
                            id='slopping_quality_dropdown_options',
                            options=[
                                {'label': 'Coker Naphtha', 'value': 'Coker Naphtha'},
                                {'label': 'Light Coker Gas Oil (LCGO)', 'value': 'Light Coker Gas Oil'},
                                {'label': 'Heavy Coker Gas Oil (HCGO)', 'value': 'Heavy Coker Gas Oil'},
                                {'label': 'HVGO or VTB', 'value': 'HVGO or VTB'},
                            ],   
                            value='Coker Naphtha'                       
                        ),
                        dcc.Store(id='selected_slopping_store'),
                        dcc.Graph(id='slopping_graph')
                    ]
                )
            ]
        ),

        #### ==== COKE DRUMS ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Coke Drums')),
                dbc.CardBody(
                    [
                        dcc.Dropdown(
                            id='cokedrum_number_dropdown_options',
                            options=[
                                {'label': 'Drum 1', 'value': '1'},
                                {'label': 'Drum 2', 'value': '2'},
                                {'label': 'Drum 3', 'value': '3'},
                                {'label': 'Drum 4', 'value': '4'},
                            ],   
                            value='1'                       
                        ),
                        dcc.Dropdown(
                            id='cokedrum_parameter_dropdown_options',
                            options=[
                                {'label': 'Foam Level', 'value': 'Foam_Level'},
                                {'label': 'Coke Level', 'value': 'Coke_Level'},
                                {'label': 'Drum Coking Pressure', 'value': 'Drum_Pressure'},
                                {'label': 'Drum Coking DP', 'value': 'Drum_DP'},
                                {'label': 'Drum Coking Temperature', 'value': 'Drum_Temperature'},
                                {'label': 'Drum Switching Temperature', 'value': 'Switch_Temperature'},
                                {'label': 'Chemical Consumption', 'value': 'Antifoam_Rate'},                                                                                                                           
                            ],   
                            value='Foam_Level'                       
                        ),             
                        dcc.Store(id='selected_cokedrum_number_store'),
                        dcc.Store(id='selected_cokedrum_parameter_store'),        
                        dcc.Graph(id='cokedrum_graph')
                    ]
                )
            ]
        ),

        #### ==== HEATER COT ==== ####
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Coker Heater COTs')),
                dbc.CardBody(
                    [
                        dcc.Dropdown(
                            id='heater_number_dropdown_options',
                            options=[
                                {'label': 'Heater 1', 'value': '1'},
                                {'label': 'Heater 2', 'value': '2'},
                                {'label': 'Heater 3', 'value': '3'},
                            ],   
                            value='1'                       
                        ),
                        dcc.Dropdown(
                            id='heater_pass_dropdown_options',
                            options=[
                                {'label': 'Pass 1', 'value': '1'},
                                {'label': 'Pass 2', 'value': '2'},
                                {'label': 'Pass 3', 'value': '3'},
                            ],   
                            value='1'                       
                        ),         
                        dcc.Dropdown(
                            id='group_by_dropdown_options',
                            options=[
                                {'label': 'Heater COT', 'value': 'Heater_COT'},
                                {'label': 'Heater Flow', 'value': 'Heater_Flow'},
                            ],   
                            value='Heater_COT'                       
                        ),             
                        dcc.Store(id='selected_heater_number_store'),
                        dcc.Store(id='selected_heater_pass_store'),      
                        dcc.Store(id='selected_group_by_store'),      
                        dcc.Graph(id='heaterCOT_graph')
                    ]
                )
            ]
        ),

        #### ==== SPALLING RECORD ==== ####

        dbc.Card(
            [
                dbc.CardHeader(html.H3('Latest Spalling Record')),
                dbc.CardBody(
                    [
                        # html.Div(id='showspallingrecord'),
                        dbc.Table(id='spalling_table'),
                        dbc.Button("Refresh", id='update_spalling_tbl_btn')
                    ]
                )
            ]
        ),
    ]
)

callback.update_yield_graph
callback.update_flaring_graph
callback.update_slopping_graph
callback.update_cokedrum_graph
callback.update_heaterCOT_graph
callback.update_spalling_tbl_graph