import datetime
from time import localtime, strftime, time
import pandas_ta
import pandas as pd
import yfinance as yf
import numpy as np
from pandasql import sqldf
from Config import Username, Password
import logging
import robin_stocks as rh
import yfinance as yf

#login
rh.robinhood.authentication.login(
username=Username, 
password=Password, 
expiresIn=86400, 
store_session=True)

i=0
x=0
l=0
#find if current datetime exists in the log, the following "file=open" opens the log file and if the current date time exists, it sets the variable to 1 which prevent the program from running as the subsequent script can only be ran if the x==0

file = open("log.py", "r")
for line in file:
	(strftime("%Y-%m-%d") in line)
	x=1
	print("prior instance")
	break			
logging.basicConfig(filename='log.py', level=logging.DEBUG)
print(strftime("%Y-%m-%d", localtime()))
logging.debug(strftime("%Y-%m-%d"))
if (x==0):
#API calls / data aquisition
	a1="{:.2f}".format(float(rh.robinhood.profiles.load_account_profile ( info="buying_power")))
	a1=float(a1)
	if (a1 != float):
		a1=0
	a2=rh.robinhood.account.get_open_stock_positions ( info="quantity")
	a3=pd.DataFrame(rh.robinhood.markets.get_markets ( info=None ))
	a4=pd.Series(rh.robinhood.markets.get_market_today_hours ( market="XNYS", info=None ))
	u1=rh.robinhood.stocks.get_events ( symbol="UDOW", info="position")
	if ((u1 != float) or (u1 > 0)):
		u1=0
	u2="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="UDOW", info="ask_price"))))
	u3="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="UDOW", info="bid_price"))))
	u4="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="UDOW", info="previous_close"))))
	u5=rh.robinhood.stocks.get_stock_historicals ( inputSymbols="UDOW", interval='hour',
	span='3month', bounds='regular', info=None )
	u5=pd.DataFrame(u5)
	u5['Close']=u5['close_price']
	u5['rsi']=pandas_ta.rsi(close= u5['Close'])
	u5['rsi']=u5['rsi'].astype(float)
	u5.dropna(axis=0, how='any', inplace=True)
	s1=rh.robinhood.stocks.get_events ( symbol="SDOW", info="position")
	if ((s1 != float) or (s1 > 0)):
		s1=0
	s2="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="SDOW", info="ask_price"))))
	s3="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="SDOW", info="bid_price"))))
	s4="{:.2f}".format(float(pd.Series(rh.robinhood.stocks.get_quotes ( inputSymbols="SDOW", info="previous_close"))))
	s5=rh.robinhood.stocks.get_stock_historicals ( inputSymbols="SDOW", interval='hour',
	span='3month', bounds='regular', info=None )
	s5=pd.DataFrame(s5)
	s5['Close']=s5['close_price']
	s5['rsi']=pandas_ta.rsi(close= s5['Close'])
	s5['rsi']=s5['rsi'].astype(np.float64)
	s5.dropna(axis=0, how='any', inplace=True)	
#display full data sets
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', None)
	pd.set_option('display.max_colwidth', None)

#The following is for debug purposes
#print(a1)
#print(type(a1))


#The following is program logic

	while (l < 1):

		print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
		l+=1
		if ((a4["is_open"]==True) and (a1 > 0) and (u1 < 1) and (s1 < 1) and (u5["rsi"] < 30)):
			print("buy udow" , "sell trailing stop")
			#rh.robinhood.orders.order_buy_market ( symbol="UDOW", quantity=1, timeInForce='gtc', extendedHours=False, jsonify=True )
			#rh.robinhood.orders.order_sell_trailing_stop ( symbol="UDOW", quantity=1, trailAmount,
			#trailType='percentage', timeInForce='gtc', extendedHours=False, jsonify=True )
			logging.debug(strftime("%Y-%m-%d"))
		elif ((a4["is_open"]==True) and (a1 > 0) and (u1 < 1) and (s1 < 1) and (s5["rsi"] < 30)):
			print("buy sdow", "sell trailing stop")
			#rh.robinhood.orders.order_buy_market ( symbol="SDOW", quantity=1, timeInForce='gtc', extendedHours=False, jsonify=True )
			#rh.robinhood.orders.order_sell_trailing_stop ( symbol="SDOW", quantity=1, trailAmount,
			#trailType='percentage', timeInForce='gtc', extendedHours=False, jsonify=True )
			logging.debug(strftime("%Y-%m-%d"))

else:
	print("we already ran")
