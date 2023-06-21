import requests
import json
import talib as ta

# Interval Dictionary
INTERVAL_DICT  = [
    # minutes
    {'label' : "1 minute", 'value' :'1m'},
    {'label': '5 minute', 'value': '5m'},
    {'label': '30 minute', 'value': '30m'},
    # hours
    {'label' : '1 hour', 'value' : '1h'},
    {'label': '2 hour', 'value': '2h'},
    {'label': '3 hour', 'value': '3h'},
    {'label': '4 hour', 'value': '4h'},
    {'label': '1 day', 'value': '1d'},
]

# Indicator Cagegorised on the basis of number of arguments in TA-Lib
INDICATOR_CATEGORY = {
    '1' : ['EMA', 'KAMA', 'LINEARREG', 'MA', 'MAX', "MIDPOINT", 'MIN', 'SMA', 'T3', 'TEMA', 'TRIMA', 'TSF', 'WMA', 'DX',],
    '2': ['RSI','APO','CMO','MOM','PPO','ROC','ROCP','ROCR','ROCR100','TRIX'],
    '3' : ['ATR','CCI'],
}

# Indicators Data Structures
INDICATOR_DS = [
    {'label': 'Bollinger Bends', 'value':'bb'},
    {'label': 'GANN Range', 'value' : 'GANN_range'},
    {'label': 'Stochastic Oscillator', 'value': 'STOCH'},
    {'label': 'Moving Average Convergance Divergence', 'value':'MACD'},
]

full_form = {
    'ACOS': 'Vector Trigonometric ACos',
    'AD': 'Chaikin A/D Line',
    'ADD': 'Vector Arithmetic Add',
    'ADOSC': 'Chaikin A/D Oscillator',
    'ADX': 'Average Directional Movement Index',
    'ADXR': 'Average Directional Movement Index Rating',
    'APO': 'Absolute Price Oscillator',
    'AROON': 'Aroon',
    'AROONOSC': 'Aroon Oscillator',
    'ASIN': 'Vector Trigonometric ASin',
    'ATAN': 'Vector Trigonometric ATan',
    'ATR': 'Average True Range',
    'AVGPRICE': 'Average Price',
    'BBANDS': 'Bollinger Bands',
    'BETA': 'Beta',
    'BOP': 'Balance Of Power',
    'CCI': 'Commodity Channel Index',
    'CDL2CROWS': 'Two Crows',
    'CDL3BLACKCROWS': 'Three Black Crows',
    'CDL3INSIDE': 'Three Inside Up/Down',
    'CDL3LINESTRIKE': 'Three-Line Strike',
    'CDL3OUTSIDE': 'Three Outside Up/Down',
    'CDL3STARSINSOUTH': 'Three Stars In The South',
    'CDL3WHITESOLDIERS': 'Three Advancing White Soldiers',
    'CDLABANDONEDBABY': 'Abandoned Baby',
    'CDLADVANCEBLOCK': 'Advance Block',
    'CDLBELTHOLD': 'Belt-hold',
    'CDLBREAKAWAY': 'Breakaway',
    'CDLCLOSINGMARUBOZU': 'Closing Marubozu',
    'CDLCONCEALBABYSWALL': 'Concealing Baby Swallow',
    'CDLCOUNTERATTACK': 'Counterattack',
    'CDLDARKCLOUDCOVER': 'Dark Cloud Cover',
    'CDLDOJI': 'Doji',
    'CDLDOJISTAR': 'Doji Star',
    'CDLDRAGONFLYDOJI': 'Dragonfly Doji',
    'CDLENGULFING': 'Engulfing Pattern',
    'CDLEVENINGDOJISTAR': 'Evening Doji Star',
    'CDLEVENINGSTAR': 'Evening Star',
    'CDLGAPSIDESIDEWHITE': 'Up/Down-gap side-by-side white lines',
    'CDLGRAVESTONEDOJI': 'Gravestone Doji',
    'CDLHAMMER': 'Hammer',
    'CDLHANGINGMAN': 'Hanging Man',
    'CDLHARAMI': 'Harami Pattern',
    'CDLHARAMICROSS': 'Harami Cross Pattern',
    'CDLHIGHWAVE': 'High-Wave Candle',
    'CDLHIKKAKE': 'Hikkake Pattern',
    'CDLHIKKAKEMOD': 'Modified Hikkake Pattern',
    'CDLHOMINGPIGEON': 'Homing Pigeon',
    'CDLIDENTICAL3CROWS': 'Identical Three Crows',
    'CDLINNECK': 'In-Neck Pattern',
    'CDLINVERTEDHAMMER': 'Inverted Hammer',
    'CDLKICKING': 'Kicking',
    'CDLKICKINGBYLENGTH': 'Kicking - bull/bear determined by the longer marubozu',
    'CDLLADDER' : '',
    'CMO': 'Chande Momentum Oscillator',
    'DX': 'Direct Movement Index',
    'HT_DCPERIOD':'Hilbert Transform - Dominant Cycle Period',
    'HT_DCPHASE':'Hilbert Transform - Dominant Cycle Phase',
    'HT_PHASOR':'Hilbert Transform - Phasor Components',
    'HT_TRENDMODE':'Hilbert Transform - Trend vs Cycle Mode',
    'EMA': 'Expoenential Moving Average',
    'KAMA':"Kaufman's Adaptive Moving Average",
    'LINEARREG': 'Linear Regression',
    'MA' : 'Moving Average',
    'MAVP': 'Moving average with variable period',
    'MAX': 'Highest value over a specified period',
    'MAXINDEX': 'Index of highest value over a specified period',
    'MEDPRICE': 'Median price',
    'MFI': 'Money Flow Index',
    'MIDPOINT': 'MidPoint over period',
    'MIDPRICE': 'Midpoint price over period',
    'MIN': 'Lowest value over a specified period',
    'MININDEX': 'Index of lowest value over a specified period',
    'MINMAX': 'Lowest and highest values over a specified period',
    'MINMAXINDEX': 'Indexes of lowest and highest values over a specified period',
    'MINUS_DI': 'Minus Directional Indicator',
    'MINUS_DM': 'Minus Directional Movement',
    'MOM': 'Momentum',
    'NATR': 'Normalized Average True Range',
    'OBV': 'On Balance Volume',
    'PLUS_DI': 'Plus Directional Indicator',
    'PLUS_DM': 'Plus Directional Movement',
    'PPO': 'Percentage Price Oscillator',
    'ROC': 'Rate of change : ((price/prevPrice)-1)*100',
    'ROCP': 'Rate of change Percentage: (price-prevPrice)/prevPrice',
    'ROCR': 'Rate of change ratio: (price/prevPrice)',
    'ROCR100': 'Rate of change ratio 100 scale: (price/prevPrice)*100',
    'RSI': 'Relative Strength Index',
    'SAR': 'Parabolic SAR',
    'SAREXT': 'Parabolic SAR - Extended',
    'SMA': 'Simple Moving Average',
    'STDDEV': 'Standard Deviation',
    'STOCH': 'Stochastic',
    'STOCHF': 'Stochastic Fast',
    'STOCHRSI': 'Stochastic Relative Strength Index',
    'SUM': 'Summation',
    'T3': 'Triple Exponential Moving Average (T3)',
    'TEMA': 'Triple Exponential Moving Average',
    'TRANGE': 'True Range',
    'TRIMA': 'Triangular Moving Average',
    'TRIX': '1-day Rate-Of-Change (ROC) of a Triple Smooth EMA',
    'TSF': 'Time Series Forecast',
    'TYPPRICE': 'Typical price',
    'ULTOSC': 'Ultimate Oscillator',
    'VAR': 'Variance',
    'WCLPRICE': 'Weighted Close Price',
    'WILLR': 'Williams %R',
    'WMA': 'Weighted Moving Average'
}

ind = ['BBANDS']
for i in INDICATOR_CATEGORY["1"]:
    INDICATOR_DS.append({'label':full_form[i], 'value':i})

for i in INDICATOR_CATEGORY["2"]:
    INDICATOR_DS.append({'label':full_form[i], 'value':i})

for i in INDICATOR_CATEGORY["3"]:
    INDICATOR_DS.append({'label': full_form[i], 'value': i})
INDICATOR_DS = sorted(INDICATOR_DS, key = lambda x : x['label'])
# Symbols Data
SYMBOL_DS = []
for data in json.loads(requests.get("https://api3.binance.com/api/v3/ticker/price").text):
    SYMBOL_DS.append({'label': data['symbol'], 'value': data['symbol']})

# Colors for figure
COLORS = [
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgreen",
    "darkgrey",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkslategrey",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    # ... add more colors as needed
]

# Strategies
STRATEGIES_DS = [
    {'label': "SMA Crossover", "value": "smaCrossover"}
]
