import dash
from dash import dcc
from dash import html
from dash import ctx
import plotly.graph_objs as go
import pandas as pd
import datetime as dt
import talib as ta
import spacy
import random
import json

from fns import *
from indicators import *
from ds import INDICATOR_DS, INDICATOR_CATEGORY, COLORS
from layouts import INITIAL_LAYOUT

# GLOBAL VARIABLES
app = dash.Dash(__name__)
ner_model = spacy.load("models/ner/ner")
ner_dict = {
    "IND": set(),
}

# LAYOUT DEFINITIONS
app.layout = INITIAL_LAYOUT
# CALLBACK FUNCTIONS
@app.callback(
    [dash.dependencies.Output('trade-chart','figure'),
     dash.dependencies.Output('indicator-chart','figure'),
     dash.dependencies.Output('indicator-chart','style'),],
    [dash.dependencies.Input('interval-component', 'n_intervals'),
     dash.dependencies.Input('ner-command', 'value'),
     dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('symbol','value'),
     dash.dependencies.Input('interval', 'value'),
     dash.dependencies.Input('limit', 'value'),
     dash.dependencies.Input('indicator', 'value'),
     dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date'),
     dash.dependencies.Input('update', 'n_clicks')
     ],
     [dash.dependencies.State('indicator-settings-container', 'children'),])
def update_figure(n, ner_text, n_clicks, symbol, interval, limit, indicators, start_date, end_date,update, container):
    # Getting Context
    trigger = ctx.triggered_id
    
    # Params update logic
    params = {}
    if container:
        for i in container:
            t = i['props']
            params[t['id']] = t['value']

    
    # INITIAL CHART
    URL = "https://api.binance.com/api/v3/uiKlines"
    
    # Data Type Change for Inidcators DS
    indicator_set = set(indicators)

    if(trigger == "ner-command"):
        doc = ner_model(ner_text)
        if len(doc) > 0:
            for enti in doc.ents:
                if(enti.label_ == "SYM"):
                    ner_dict["SYM"] = enti.text
                elif(enti.label_ == "INT"):
                    ner_dict['INT'] = enti.text
                elif(enti.label_ == "IND"):
                    ner_dict['IND'].add(enti.text) 
                
            
            df = create_dataframe(URL, ner_dict["SYM"], ner_dict["INT"], limit, start_date, end_date)
    
    else:
        df = create_dataframe(URL, symbol, interval, limit,start_date, end_date)
    
        
    # candlestick
    candlestick = go.Candlestick(x=df.index,
                                          open=df['Open'],
                                          high=df['High'],
                                          low=df['Low'],
                                          close=df['Close'])
    
    # Bar
    bar = go.Bar(x = df.index, y = df["Volume"], marker=dict(color = 'blue', opacity = 0.1), yaxis = 'y2')
    
    # Figure
    fig = go.Figure(data=[candlestick])
    fig.add_trace(bar)

    # 2nd Figure
    ind_fig = go.Figure(data=[])
    
    # style
    style = {'height':'300px', 'display': 'none'}

    # Checking for indicators
    if(ner_dict and ner_dict['IND']):
        for i in ner_dict["IND"]:
            indicator_set.add(i)

     
    for ind in indicator_set:
    # INDICATORS
        if(ind in INDICATOR_CATEGORY["1"]):
            # Scatter
            fn = getattr(ta, ind)
            gen = fn(df['Close'], params.get(ind, 2))
            fig.add_scatter(x = df.index, y = gen, mode = 'lines', name=ind, marker = dict(color=COLORS[random.randint(0, len(COLORS) - 1)]))
    
        elif(ind in INDICATOR_CATEGORY["2"]):
            # Calling the indicator function
            fn = getattr(ta, ind)
            gen = fn(df['Close'], params.get(ind, 7))

            # 2nd Figure
            sc = go.Scatter(x = df.index, y = gen, name = ind, marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)]))
            ind_fig.add_trace(sc)
            ind_fig.update_layout(title = "Indicators Chart",
                            yaxis = dict(title='Prices'),)
            
            style['display'] = 'block'

        elif(ind in INDICATOR_CATEGORY['3']):
            # Callling the indicator function
            fn = getattr(ta, ind)
            gen = fn(df['High'], df["Low"], df['Close'], params.get(ind, 7))
            
            sc = go.Scatter(x = df.index, y = gen, name = ind, marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)])) 
            ind_fig.add_trace(sc)
            ind_fig.update_layout(title = "Indicators", yaxis = dict(title = 'Prices'))

            style['display'] = 'block'

        elif(ind == "bb"):
            # BOLLINGER BENDS
            upper_bend, middle_bend, lower_bend = ta.BBANDS(df['Close'], timeperiod = 20, nbdevup = 2, nbdevdn = 2, matype = 0)
            fig.add_trace(go.Scatter(x = df.index, y = upper_bend, name = "Upper BB", marker = dict(color = 'blue')))
            fig.add_trace(go.Scatter(x = df.index, y = middle_bend, name = "Midddle BB", marker = dict(color = 'orange')))
            fig.add_trace(go.Scatter(x = df.index, y = lower_bend, name = "Lower BB", marker = dict(color = 'blue')))
        
        elif(ind == "GANN_range"):
            # GANN RANGE
            if(params.get("GANN_range Max") and params.get("GANN_range Low")):
                vals = GANN_range(params["GANN_range Max"], params["GANN_range Low"])
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[0], vals[0]],mode = 'lines', name = '0', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[1], vals[1]],mode = 'lines', name = '45', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[2], vals[2]],mode = 'lines', name = '90', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[3], vals[3]],mode = 'lines', name = '135', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[4], vals[4]],mode = 'lines', name = '180', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[5], vals[5]],mode = 'lines', name = '225', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[6], vals[6]],mode = 'lines', name = '270', marker = dict(color = 'yellow')))
                fig.add_trace(go.Scatter(x = [df.index[0], df.index[-1]], y = [vals[7], vals[7]],mode = 'lines', name = '315', marker = dict(color = 'yellow')))
                
            else:
                vals = GANN_range(max(df['Close']), min(df['Close']))         
    
        elif(ind == "STOCH"):
            # STOCH
            fn = getattr(ta, ind)
            gen1, gen2 = fn(df['High'], df["Low"], df['Close'], params.get(ind, 7))
            
            sc1 = go.Scatter(x = df.index, y = gen1, name = "Slowk", marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)])) 
            sc2 = go.Scatter(x = df.index, y = gen2, name = "Slowd", marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)])) 
            ind_fig.add_trace(sc1)
            ind_fig.add_trace(sc2)
            
            ind_fig.update_layout(title = "Indicators", yaxis = dict(title = 'Prices'))

            style['display'] = 'block'
        
        elif(ind == "MACD"):
            # MACD
            fn = getattr(ta, ind)
            macd, macd_signal, macd_hist = fn(df['Close'])

            sc1 = go.Scatter(x = df.index, y = macd, name = "MACD", marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)]))
            sc2 = go.Scatter(x = df.index, y = macd_signal, name = "MACD Signal", marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)]))
            hist = go.Bar(x = df.index, y = macd_hist, name = "MACD Histogram", marker = dict(color = COLORS[random.randint(0, len(COLORS) - 1)]))

            ind_fig.add_trace(sc1)
            ind_fig.add_trace(sc2)
            ind_fig.add_trace(hist)
            
            style['display'] = 'block'


    fig.update_layout(title='Trade Chart',
                      xaxis = dict(showgrid = False, zeroline = False),
                      xaxis_rangeslider_visible=False,
                      yaxis = dict(title = 'Prices', fixedrange=True, showgrid = False, zeroline = False),
                      yaxis2 = dict(title = "Volume", overlaying = 'y', side = 'right', fixedrange=True, showgrid = False, zeroline = False))
    
    
    del df
    indicator_set.clear()
    return fig, ind_fig,style

@app.callback(
    dash.dependencies.Output("indicator-settings-container", "children"),
    [dash.dependencies.Input('indicator', 'value')]
)
def update_indicator_settings(indicator):
    if indicator:
        return generate_indicator_settings(indicator)
    
# MAIN FUNCTIONS
if __name__ == "__main__":
    app.run_server(debug = True)