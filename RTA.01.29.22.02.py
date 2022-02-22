#Lead indicator RSI, lag MACD, and AVG price. Limit orders for execution. Config and robinhood account necessary to run.
#https://join.robinhood.com/steve64
#https://www.alpharithms.com/calculate-macd-python-272222/ <-MACD calculation, as pandas was not working with the way I wrote my script.

from datetime import datetime
from time import localtime, strftime
from os import waitpid
from time import sleep
from pandas._libs.tslibs.timestamps import Timestamp
from pandas.core.dtypes import dtypes
from pandas.core.indexes.datetimes import date_range
import robin_stocks as rh
import pandas as pd
from pandas import DataFrame, Series 
import pandas_ta
from pandas_ta import rsi, macd
from config import Username, Password
import numpy as np 

rh.robinhood.authentication.login(
username=Username, 
password=Password, 
expiresIn=86400, 
store_session=True)

print("::loading profile::")
#wait=sleep(1)
print("::profile loaded::")

i=0
n=0

while i < 5760:#update to 5760 

    wait=sleep(5)
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

    ffe=(((np.float64(cr_buy_pwr))*2) // 20)#funds for execution #2/50=4% of account

    print("ffe:", ffe)
    
    wait=sleep(5)

#Convert API requests to DataFrames

    ask=pd.Series(a)
    bdd=pd.Series(b)

    pos=pd.DataFrame(positions)

    cbp=(cr_buy_pwr)

    tick=pd.Series(ticker)

    df=pd.DataFrame(all_param)
    
    series=pd.Series(all_param)

    print("Acct bal:",cbp)

    #Convert DataFrame to corrected dataypes for operations

    ask.astype(np.float32)
    bdd.astype(np.float32)

    ask=np.float32(ask[0])
    bdd=np.float32(bdd[0])

    print("ask:", ask)
    print("bid:", bdd)

    pos["quantity_available"]=pos["quantity_available"].astype(np.float64)

    df["open_price"]=df["open_price"].astype(np.float64)
    df["close_price"]=df["close_price"].astype(np.float64)
    df["high_price"]=df["high_price"].astype(np.float64)
    df["low_price"]=df["low_price"].astype(np.float64)

    df["rsi"]=pandas_ta.rsi(close= df["close_price"])

    df["rsi"]=df["rsi"].astype(np.float64)

    positive_trend=(df.iloc[0,3] > ((df.iloc[0,3]+df.iloc[10,3]+df.iloc[20,3])/3))

    # calculate MACD values

    k = df['close_price'].ewm(span=12, adjust=False, min_periods=12).mean()
    # Get the 12-day EMA of the closing price
    d = df['close_price'].ewm(span=26, adjust=False, min_periods=26).mean()
    # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd = k - d
    # Get the 9-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
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

    print("holding",pos.iloc[2,6])
    print("rsi:",df.iloc[0,9])
    print("macd:",df.iloc[0,10])
    print("signal:",df.iloc[0,12])
    print(df.iloc[0,11])
    print(df.iloc[1,11])
    print(df.iloc[2,11])

    try:
        if  (
            pos.iloc[2,6] < 1/1000 and ffe > ask and df.iloc[0,9] <= 35 and df.iloc[0,10] > df.iloc[0,12] and df.iloc[0,11] < 0) or (
                pos.iloc[2,6] < 1/1000 and df.iloc[0,9] <= 35 and df.iloc[0,10] > df.iloc[0,12] and df.iloc[0,11] < 0) or(
                    pos.iloc[2,6] < 1/1000 and ffe > ask and positive_trend==True and df.iloc[0,11] < 0 and df.iloc[0,10] > df.iloc[0,12] 
                ): #or (
                    #pos.iloc[2,6] < 1/1000 and df.iloc[0,10] < 0 and df.iloc[0,10] > df.iloc[0,12] and df.iloc[0,11] > 0):
                        buy=rh.robinhood.orders.order_buy_crypto_limit(symbol="ETC", quantity=1, limitPrice=(ask+.02), timeInForce='gtc')
                        print("bought @ limit", (ask+.02),"\n", "rsi", df.iloc[0,9],"\n")
                        x=ffe - (ffe - (ask+.02)) #variable for last sale price
                        print(x)
                        wait=sleep(60)
                        sell=rh.robinhood.orders.order_sell_crypto_limit(
                                symbol="ETC", quantity=pos.iloc[2,6], limitPrice=(ask + .03), timeInForce='gtc')
                        print("consecutive sale pending at limit", ask+.03)
                        wait=sleep(60)
                        n==10 
        elif (
            pos.iloc[2,6] > 1/1000 and df.iloc[0,9] >= 69 and df.iloc[0,10] <= df.iloc[0,12] and df.iloc[0,11] < 0) or (
                pos.iloc[2,6] > 1/1000 and df.iloc[0,9] >= 71 and df.iloc[0,11] < 0) or (
                    pos.iloc[2,6] > 1/1000 and df.iloc[0,9] >= 65 and df.iloc[0,10] <= df.iloc[0,12] or (
                        pos.iloc[2,6] > 1/1000 and df.iloc[0,9] >= 70 and df.iloc[0,11] > 0
                    )
                ):
                        cancel=rh.robinhood.orders.cancel_all_crypto_orders()
                        print("canceled previous pending \n")
                        sell=rh.robinhood.orders.order_sell_crypto_limit(
                            symbol="ETC", quantity=pos.iloc[2,6], limitPrice=(bdd -.02), timeInForce='gtc')
                        wait=sleep(10)
                        print("selling @ limit", (bdd - .02),"\n", "rsi", df.iloc[0,9],"\n")
                        if pos.iloc[2,6] < 1:
                            print("sold")    
        elif pos.iloc[2,6] > 1/1000 and bdd > x:
                    cancel=rh.robinhood.orders.cancel_all_crypto_orders()
                    print("canceled previous pending \n")
                    sell=rh.robinhood.orders.order_sell_crypto_limit(
                        symbol="ETC", quantity=pos.iloc[2,6], limitPrice=bdd, timeInForce='gtc')
                    wait=sleep(10)
                    print("selling @ limit per x", bdd,"\n", "rsi", df.iloc[0,9],"\n")
                    if pos.iloc[2,6] < 1:
                        print("sold")
        elif n > 0:
                n-=1
        elif n==1:
            cancel=rh.robinhood.orders.cancel_all_crypto_orders()
            print("canceled previous pending \n")
            n-=1
        else: print("No transaction","@","$",((ask+bdd)/2),"\n",i,"\n") 

    finally:
        
        i += 1

    