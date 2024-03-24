import os, pandas
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

dataframes = {}

for filename in os.listdir('datasets'):
    #print(filename)
    symbol = filename.split(".")[0]
    #print(symbol)
    df = pandas.read_csv('datasets/{}'.format(filename))
    if df.empty:
        continue

    df['20sma'] = df['Close'].rolling(window=20).mean()
    df['stddev'] = df['Close'].rolling(window=20).std()
    df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    df['upper_band'] = df['20sma'] + (2 * df['stddev'])

    df['TR'] = abs(df['High'] - df['Low'])
    df['ATR'] = df['TR'].rolling(window=20).mean()

    df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

    #Momentum Indicator
    df['donchian_midline'] = (df['High'].rolling(window=20).max()+df['Low'].rolling(window=20).min())/2
    df['histogram_bar'] = df['Close'] - ((df['donchian_midline']+ df['20sma'])/2)
    fit_y = np.array(range(0,20))
    df['histogram_bar'] = df['histogram_bar'].rolling(window = 20).apply(lambda x : np.polyfit(fit_y, x, 1)[0] * (20-1) +np.polyfit(fit_y, x, 1)[1], raw=True)

    # Squeeze on/off df
    df['squeeze_on'] = (df['lower_band'] > df['lower_keltner']) & (df['upper_band'] < df['upper_keltner'])
    df['squeeze_off'] = (df['lower_band'] < df['lower_keltner']) & (df['upper_band'] > df['upper_keltner'])

    #TODO implement
    # # entry point for long position:
    # # 1. black cross becomes gray (the squeeze is released)
    # long_cond1 = (df['squeeze_off'][-2] == False) & (df['squeeze_off'][-1] == True) 
    # # 2. bar value is positive => the bar is light green
    # long_cond2 = df['value'][-1] > 0
    # enter_long = long_cond1 and long_cond2
    # # entry point for short position:
    # # 1. black cross becomes gray (the squeeze is released)
    # short_cond1 = (df['squeeze_off'][-2] == False) & (df['squeeze_off'][-1] == True) 
    # # 2. bar value is negative => the bar is light red 
    # short_cond2 = df['value'][-1] < 0
    # enter_short = short_cond1 and short_cond2

    # if df.iloc[-3]['squeeze_on'] and not df.iloc[-1]['squeeze_on']:
    #     print("{} is coming out the squeeze".format(symbol))

    # save all dataframes to a dictionary
    # we can chart individual names below by calling the chart() function
    dataframes[symbol] = df


def chart(df):
    candlestick = go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])
    upper_band = go.Scatter(x=df['Date'], y=df['upper_band'], name='Upper Bollinger Band', line={'color': 'red'})
    lower_band = go.Scatter(x=df['Date'], y=df['lower_band'], name='Lower Bollinger Band', line={'color': 'red'})

    upper_keltner = go.Scatter(x=df['Date'], y=df['upper_keltner'], name='Upper Keltner Channel', line={'color': 'blue'})
    lower_keltner = go.Scatter(x=df['Date'], y=df['lower_keltner'], name='Lower Keltner Channel', line={'color': 'blue'})
    plot1_list = [candlestick, upper_band, lower_band, upper_keltner, lower_keltner]
    #histogram
    histogram = go.Bar(x=df['Date'], y=df['histogram_bar'], name='Momentum Histogram', marker_color=['red' if val <=0 else 'green' for val in df['histogram_bar']])
    squeeze_on_off = go.Scatter(x=df['Date'], y=[0]*len(df), name='Squeeze on/off dots',marker=dict(
        color=['grey' if val else 'black' for val in df['squeeze_off']],
        size=5,  # Adjust the marker size as per your requirement
        ), mode='markers')

    subplots= make_subplots(rows=2, cols=1, shared_xaxes=True)

    for i in plot1_list: 
        subplots.add_trace(i, row=1, col=1)

    subplots.add_trace(histogram, row=2, col=1)
    subplots.add_trace(squeeze_on_off, row=2, col=1)

    subplots.show()

df = dataframes['TSLA']
chart(df)