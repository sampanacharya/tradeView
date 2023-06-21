import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests 
import json 
import pandas as pd
import datetime as dt
import numpy as np
from dash import dcc
from dash import html
from ds import INDICATOR_CATEGORY

def create_dataframe(url, symbol, interval, limit, startTime = "", endTime = ""):
    # URL
    url = url + "?symbol="+ symbol + "&interval=" + interval + "&limit=" + limit
    
    # start time and end time url customization
    if(startTime and endTime):
        # conversion of time to timestamp
        if(isinstance(startTime, str)):
            startTime += " 12:00:00"
            startTime = str(int(dt.datetime.timestamp(dt.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S"))) * 1000)
        else:
            startTime = str(int(dt.datetime.timestamp(startTime)) * 1000)
        
        if(isinstance(endTime, str)):
            endTime += " 12:00:00"
            endTime = str(int(dt.datetime.timestamp(dt.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S"))) * 1000)
        else:
            endTime = str(int(dt.datetime.timestamp(endTime)) * 1000)
        
        url += ("&startTime=" + startTime + "&endTime=" + endTime)
        
    elif(startTime):
        if(isinstance(startTime, str)):
            startTime += " 12:00:00"
            startTime = str(int(dt.datetime.timestamp(dt.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S"))) * 1000)
        else:
            startTime = str(int(dt.datetime.timestamp(startTime)) * 1000)
            
        url += ("&startTime=" + startTime)

    #print(url, dt.datetime.fromtimestamp(int(startTime) // 1000 ))
    # Dictionary
    dictio = {
        "Open": [],
        "High": [],
        "Low": [],
        "Close":[],
        "Volume": [],
        "Close Time": [],
    }

    # Loads data in json
    data = json.loads(requests.get(url).text)

    for i in range (len(data)):
        dictio["Open"].append(float(data[i][1]))
        dictio["High"].append(float(data[i][2]))
        dictio["Low"].append(float(data[i][3]))
        dictio["Close"].append(float(data[i][4]))
        dictio["Volume"].append(float(data[i][5]))
        dictio["Close Time"].append(float(data[i][6]))
    df = pd.DataFrame(dictio)
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df["Close Time"]]
    
    if(not startTime):
        startTime = df.index[0]
    else:
        endTime = df.index[1]
    return df

def generate_indicator_settings(indicators):
    setting_child = []
    for ind in indicators:
        comp = None
        if(ind in INDICATOR_CATEGORY['1']):
            #setting_child.append(html.Label(f"{ind} Period"))
            setting_child.append(dcc.Input(id = f"{ind}",
                                           type = 'number', 
                                           placeholder=f"{ind} Period"))
        elif(ind in INDICATOR_CATEGORY['2']):
            setting_child.append(dcc.Input(id = f"{ind}", 
                                           type = 'number', 
                                           placeholder=f"{ind} Period"))
        elif(ind in INDICATOR_CATEGORY['3']):
            setting_child.append(dcc.Input(id = f"{ind}",
                                           type = 'number',
                                           placeholder=f"{ind} Period"))
        
        elif(ind == "GANN_range"):
            setting_child.append(dcc.Input(id = f"{ind} Max", 
                                           type= "number", 
                                           placeholder="Highest Value",))
            setting_child.append(dcc.Input(id = f"{ind} Low",
                                           type = 'number', 
                                           placeholder="Lowest Value"))
        
    return setting_child

