#!

#Lead indicator RSI, lag MACD, and AVG price. Limit orders for execution. Config and robinhood account necessary to run.
#https://join.robinhood.com/steve64
#https://robin-stocks.readthedocs.io/en/latest/
#https://www.alpharithms.com/calculate-macd-python-272222/ <-MACD calculation, as pandas was not working with the way I wrote my script.
#https://technical-analysis-library-in-python.readthedocs.io/en/latest/
#*https://www.programcreek.com/python/example/92323/talib.BBANDS

from audioop import avgpp
from curses import window
from datetime import datetime
from time import localtime, strftime
from os import waitpid
from time import sleep
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from pandas._libs.tslibs.timestamps import Timestamp
from pandas.core.dtypes import dtypes
from pandas.core.indexes.datetimes import date_range
import robin_stocks as rh
import talib as ta
import statistics
import math
from statistics import stdev
import pandas_ta
from pandas_ta import rsi, macd, bbands
#from pandas_ta import volatility
#from pandas_ta.volatility import bbands
from pandas_ta import bbands 
from config010322 import Username, Password

#login
rh.robinhood.authentication.login(
username=Username, 
password=Password, 
expiresIn=86400, 
store_session=True)

#start prompt
print("::loading profile::")
print("::profile loaded::")

#set variable initial values
i=0
q=0
n=0
x0=0
x1=0
x2=0
x3=0
x4=0

#the program is set to loop for roughly 24 hours
while i < 55760:#update to 5760 

#Acquire data to iterate. The follwing API requests provide the raw data.

    positions=rh.robinhood.crypto.get_crypto_positions(info=None)
    a=rh.robinhood.crypto.get_crypto_quote(symbol='ETC', info="ask_price")
    b=rh.robinhood.crypto.get_crypto_quote(symbol='ETC', info="bid_price")

    cr_buy_pwr=rh.robinhood.profiles.load_account_profile(info="crypto_buying_power")

    balance=rh.robinhood.profiles.load_account_profile(info=None)

    ticker=rh.robinhood.crypto.get_crypto_quote(symbol='ETC', info=None)

    all_param=rh.robinhood.crypto.get_crypto_historicals(
        symbol='ETC', interval='15second', span='hour', bounds='24_7', info=None)

    time=strftime("%Y-%m-%d %H:%M:%S", localtime())

#%account usage

    #ffe=(((np.float64(cr_buy_pwr))*2) // 20)#funds for execution #2/50=4% of account
    ffe=(((np.float64(cr_buy_pwr))*2) // 2)

#Convert API requests to DataFrames

    ask=pd.Series(a)
    bdd=pd.Series(b)

    pos=pd.DataFrame(positions)

    cbp=(cr_buy_pwr)

    tick=pd.Series(ticker)

    df=pd.DataFrame(all_param)

    series=pd.Series(all_param)

#Convert DataFrames/values to corrected dataypes for operations

    ask.astype(np.float32)
    bdd.astype(np.float32)

    ask=np.float32(ask[0])
    bdd=np.float32(bdd[0])

    fask="{:.2f}".format(ask)
    fbdd="{:.2f}".format(bdd)

    pos["quantity_available"]=pos["quantity_available"].astype(np.float64)

    df["open_price"]=df["open_price"].astype(np.float64)
    df["close_price"]=df["close_price"].astype(np.float64)
    df["high_price"]=df["high_price"].astype(np.float64)
    df["low_price"]=df["low_price"].astype(np.float64)

    df["rsi"]=pandas_ta.rsi(close= df["close_price"])

    df["rsi"]=df["rsi"].astype(np.float64)

# calculate MACD values

    k = df['close_price'].ewm(span=10, adjust=False, min_periods=12).mean()
# Get the (10 or 12)-day EMA of the closing price
    d = df['close_price'].ewm(span=16, adjust=False, min_periods=26).mean()
# Subtract the (16 or 26)-day EMA from the 12-Day EMA to get the MACD
    macd = k - d
# Get the (3 or 9)-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=3, adjust=False, min_periods=9).mean()
# Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
    macd_h = macd - macd_s
# Add all of our new values for the MACD to the dataframe
    df['macd'] = df.index.map(macd)
    df['macd_h'] = df.index.map(macd_h)
    df['macd_s'] = df.index.map(macd_s)

    df['macd'] = df['macd'].astype(np.float64)
    df['macd_h'] = df['macd_h'].astype(np.float64)
    df['macd_s'] = df['macd_s'].astype(np.float64)

    df.dropna(axis=0, how='any', inplace=True)

    def bbands(source, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
        return pandas_ta.bbands(source, timeperiod, nbdevup, nbdevdn, matype)

# Initialize Bollinger Bands Indicator
    indicator_bb = pandas_ta.bbands(close=df['close_price'], window=20, window_dev=1)

    indicator_bb.dropna(axis=0, how='any', inplace=True)

    limit=np.float32(indicator_bb.iloc[200,2])

    #float(limit="{:.2f}".format(indicator_bb.iloc[200,2]))
    float(limit)

    avgprice=((ask+bdd)/2)

    avgprice=np.float32(avgprice)

    #float(avgprice="{:.2f}".format(avgprice))
    float(avgprice)

    #print(avgprice)
    #print(type(avgprice))
    #print(limit)
    #print(type(limit))
#print(type(indicator_bb))

    print("bandu",indicator_bb.iloc[200,2])
    print("avg price:",((ask+bdd)/2))

#print base decision values
    print("ffe:", ffe)
    print("Acct bal:",cbp)
    print("ask:", fask)
    print("bid:", fbdd)
    print("avgprice:",avgprice)
    print("limit:",limit)
    print("holding",pos.iloc[2,6])
    print("rsi:",df.iloc[200,9])
    print("macd:",df.iloc[200,10])
    print("signal:",df.iloc[200,12])

    #print(type(((np.float32(fask))+(np.float32(fbdd))/2)))
    #print(type((np.float32(indicator_bb.iloc[200,2]))))

    #print(((fask+fbdd)/2))
    #print(type((np.float32(indicator_bb.iloc[200,2]))))
#Execute buy/sell/wait loop
    try:
        if  (
            pos.iloc[2,6] <= 1 and ffe > 40 and df.iloc[200,9] <= 35 and q < 1 and df.iloc[200,10] < df.iloc[200,12] and avgprice < limit and df.iloc[200,11] < df.iloc[199,11]): #and MACD below Signal
                x0=ffe
                rh.robinhood.orders.order_buy_crypto_limit(symbol="ETC", quantity=1, limitPrice=(fask), timeInForce='gtc')
                x1=ffe
                x3=(fask)
                q=1
                n=0
                print("i=", i, "\n", q, "\n", "x1=", x1, "\n", "x2=", x2, "\n")
        elif (pos.iloc[2,6] >= 1 and q >= 1 and q < 3):
            rh.robinhood.orders.order_sell_crypto_limit(
                  symbol="ETC", quantity=1, limitPrice=(float(format(((float(x3))+0.01),'.2f'))), timeInForce='gtc')
            x2=ffe
            x4=(float(x3))+0.01
            q=2
            n=0
            print("i=", i, "\n", "q=", q, "\n", "x1=", x1, "\n", "x2=", x2, "\n")
            print("x0=", x0, "\n", "x4=",x4,"\n")
        elif (ffe >= x0 and q > 0): 
            q=0
            n=0
            print(((ask+bdd)/2),"\n",time,"\n", "i=", i, "\n", "q=", q, "\n", "x1=", x1, "\n", "x2=", x2, "\n")
            wait=sleep(600)
        elif n>5999:
            q=0
            n=0
        else: print("No transaction","@","$",((ask+bdd)/2),"\n",time,"\n","i=", i,"\n","q=", q, "\n", "x1=", x1, "\n", "x2=", x2, "\n")
             
    finally:
        
        i += 1
        n += 1

