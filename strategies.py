# CM_EMA trendbars
import datetime
import backtrader as bt
import requests
import pandas as pd
import logging
logging.basicConfig(filename='backtesting/backtest.log',
                    level = logging.INFO,
                    filemode='w')

class CM_EMA_TrendBars(bt.Strategy):
    params = (
        ('ema_period', 34),
        ('short_period', 12),
        ('long_period', 26),
        ('signal_period', 9),
        ('shema', True)
    )

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.ema_period)
        self.macd = bt.indicators.MACD(
            self.data.close, period_me1=self.params.short_period,
            period_me2=self.params.long_period,
            period_signal=self.params.signal_period)

        self.order = None
        self.entry_price = None
        self.stop_loss = None
        self.target_price = None
    
    def log(self, l):
        logging.info(l)

    def next(self):
        if self.order:
            return
        print(self.macd.macd[0], self.ema[0], self.macd.macd[-1], self.ema[-1], self.data.close[0])
        if self.macd.macd[0] * self.ema[0] > 0 and self.macd.macd[-1] * self.ema[-1] <= 0:
            # Bullish trend change
            self.entry_price = self.data.close[0]

            if(len(self.data.low.get(ago=-1, size=60)) > 0):
                self.stop_loss = max(self.data.high.get(ago=-1, size=60))
            else:
                self.stop_loss = self.data.high[0]

            self.target_price = self.entry_price + (self.entry_price - self.stop_loss)
            self.buy()
        elif self.macd.macd[0] * self.ema[0] < 0 and self.macd.macd[-1] * self.ema[-1] >= 0:
            # Bearish trend change
            self.entry_price = self.data.close[0]
            
            if len(self.data.low.get(ago=-1, size=60)) > 0:
                self.stop_loss = min(self.data.low.get(ago=-1, size=60))
            else:
                self.stop_loss = self.data.low[0]
            
            self.target_price = self.entry_price - (self.stop_loss - self.entry_price)
            self.sell()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('Buy executed at {}'.format(order.executed.price))
                self.log('Stop Loss: {}'.format(self.stop_loss))
                self.log('Target Price: {}'.format(self.target_price))
            elif order.issell():
                self.log('Sell executed at {}'.format(order.executed.price))
                self.log('Stop Loss: {}'.format(self.stop_loss))
                self.log('Target Price: {}'.format(self.target_price))

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Fetch data from Binance API
    symbol = 'BTCUSDT'
    interval = '1s'
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000'
    response = requests.get(url)
    data = response.json()
    

    # Prepare data for backtrader
    candle_data ="datetime,open,high,low,close,volume\n"
    for candle in data:
        #print(candle)
        timestamp = candle[0] / 1000.0  # Convert milliseconds to seconds
        #print(timestamp)
        dt = datetime.datetime.fromtimestamp(timestamp)
        #print("We are here !!",dt)
        open_, high, low, close, volume = map(float, candle[1:6])
        candle_data+=(','.join(map(str,[dt, open_, high, low, close, volume]))) +"\n"

    with open('data.csv','w') as f:
        f.write(candle_data)        

    df = pd.read_csv("data.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Add data feed
    data_feed = bt.feeds.PandasData(dataname = df, datetime=-1)
    #print(data_feed)
    cerebro.adddata(data_feed)


    # Add strategy
    cerebro.addstrategy(CM_EMA_TrendBars)

    # Set initial capital
    cerebro.broker.setcash(100000)

    # Set commission (if applicable)
    cerebro.broker.setcommission(commission=0.001)

    # Run the backtest
    cerebro.run()

    cerebro.plot()





