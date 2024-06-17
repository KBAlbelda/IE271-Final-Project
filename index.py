from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import webbrowser

#### ==== #### ==== #### ==== #### ==== ####

from app import app
from apps import commonmodules as cm
from apps import home

from apps.coker_heaters import coker_heaters_home,coker_heaters_heaters, coker_heaters_spalling
from apps.coker_drums import coker_drums_home, coker_drums_add, chemicals
from apps.yields import yields_home, yields_add, yields_flaring, yields_slopping

#### ==== #### ==== PAGE LAYOUT ==== #### ==== ####

CONTENT_STYLE = {
    "margin-top": "1em",
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=True),
        cm.navbar,
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)

#### ==== #### ==== LOADING ACTUAL PAGE ==== #### ==== ####

@app.callback(
    [
        Output('page-content', 'children')
    ],
    [
        Input('url', 'pathname')
    ]
)
def displaypage (pathname):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'url':
            if pathname == '/' or pathname == '/home':
                returnlayout = home.layout
            elif pathname == '/yields':
                returnlayout = yields_home.layout
            elif pathname == '/yields/yield_data':
                returnlayout = yields_add.layout
            elif pathname == '/flaring':
                returnlayout = yields_flaring.layout
            elif pathname == '/slopping':
                returnlayout = yields_slopping.layout
            elif pathname == '/coke-drums':
                returnlayout = coker_drums_home.layout
            elif pathname == '/coke-drums/drum_data':
                returnlayout = coker_drums_add.layout
            elif pathname == '/coker-heaters':
                returnlayout = coker_heaters_home.layout
            elif pathname == '/chemicals':
                returnlayout = chemicals.layout
            elif pathname == '/coker-heaters/heater_data':
                returnlayout = coker_heaters_heaters.layout
            elif pathname == '/coker-heaters/spalling_data':
                returnlayout = coker_heaters_spalling.layout
            else:
                returnlayout = 'ERROR 404'
            return [returnlayout]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

#### ==== #### ==== RUN APP ON WEB BROWSER ==== #### ==== ####

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)