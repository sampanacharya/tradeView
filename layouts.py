###### LAYOUTS ###########
import dash 
from dash import dcc
from dash import html
from plotly import graph_objects as go
from ds import *
import datetime as dt

INITIAL_LAYOUT = html.Div([
    # Title
    html.H1('Trade Chart'),

    # Text Field
    html.Div([
        html.Label("Enter your command:"),
        dcc.Input(
            id = "ner-command",
            type = "text",
            placeholder = "Enter something like 'Apply RSI on BTCUSDT for an interval of 1m'",
            style = {
                'width': '400px',
                'height': '80px',
                'font-size': '16px',
                'padding': '10px',
                'border-radius': '5px',
                'border': '1px solid #ccc',
            },
            value = "",
        )
    ], style = {'margin-bottom': '20px'}),
    
    html.Label("Didn't get the expected results ? Click on the button below to submit your prompt and impprove the model.\n"),
    html.Button("Submit your prompt", id = "submit-button", n_clicks = 0),
    html.Br(),
    html.Label("OR"),
    
    # Menu Bar
    html.Div([
        # Symbol for the data points
        html.Label("Enter a symbol"),
        dcc.Dropdown(id = 'symbol', options=SYMBOL_DS,value = '',),
        
        # Interval between the data points
        html.Label("Select a interval"),
        dcc.Dropdown(id = 'interval', options=INTERVAL_DICT, value = "",
                     style = {'display': 'inline-block', 'width':'200px'}),
        
        # Number of data points to be fetched
        html.Label("Enter the values(if left blank realtime values will be plotted)"),
        dcc.Input(id='limit', type='text',value='100', placeholder = '100'),

        # Date Range
        html.Label("Select a timeframe(if left empty recent values will be plotted)"),
        dcc.DatePickerRange(id = 'date-picker',
                            min_date_allowed=dt.datetime(2017,1,1),
                            max_date_allowed=dt.datetime.now(),
                            initial_visible_month=str(dt.datetime.now())[:10],
                            )

    ]),

    # Indicators
    html.Label("Indicators"),
    dcc.Dropdown(id = "indicator", options = INDICATOR_DS, value = [], multi=True),
    
    # Indicators Settings Containers
    html.Div(id = "indicator-settings-container"),
    html.Button("Update Chart", id = "update"),

    # Strtegies for backtesting
    dcc.Dropdown(id = "strategies", options = STRATEGIES_DS, value = ""),
    # Graph Object
    dcc.Graph(id='trade-chart', style = {'height': '700px'}),
    dcc.Graph(id ='indicator-chart',style = {'height' : '200px', 'display': 'none'}),

    # Interval Update Component
    dcc.Interval(
    id='interval-component',
    interval=60000, # update every 1 minute
    n_intervals=0)
])
