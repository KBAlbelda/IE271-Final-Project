from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate

#### ==== #### ==== #### ==== #### ==== ####

from app import app

#### ==== #### ==== COMMON HEADER ==== #### ==== ####

navlink_style = {'color': '#fff'}

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("DCU Dashboard", className="ml-2")),
                ],
                align="center",
                className='g-0'
            ),
            href="/home",
        ),
        dbc.NavLink("Home", href="/home", style=navlink_style),
        dbc.NavLink("Yields", href="/yields", style=navlink_style),
        dbc.NavLink("Coke Drums", href="/coke-drums", style=navlink_style),
        dbc.NavLink("Coker Heaters", href="/coker-heaters", style=navlink_style),
    ],
    dark=True,
    color='dark'
)