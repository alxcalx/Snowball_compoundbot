
from logging import log
from numpy import double
from tradingview_ta import TA_Handler, Interval, Exchange
import datetime
import threading
from datetime import datetime, timedelta
from numpy.lib.function_base import average, kaiser
import time

import math

import pandas as pd
from binance.client import Client
from time import sleep
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from binance import ThreadedWebsocketManager
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException


api_key = ""
api_secret = ""

client = Client(api_key, api_secret)
#client.API_URL = 'https://testnet.binance.vision/api'
exchange_info = client.get_exchange_info()


#exchange_markets= ['SOLUSD','BTCUSD','ETHUSD','ADAUSD','MATICUSD','ATOMUSD' ,'BNBUSD','ALGOUSD', 'HBARUSD', 'ONEUSD', 'VETUSD', 'EGLDUSD', 'DOGEUSD', 'XTZUSD', 'OMGUSD','SUSHIUSD','AMPUSD','BCHUSD','XLMUSD','ICXUSD','HNTUSD','NANOUSD','EOSUSD','LTCUSD', 'COMPUSD','NEOUSD','IOTAUSD','ZILUSD', 'UNIUSD', 'STORJUSD','RVNUSD', 'ZECUSD','ENJUSD','OXTUSD','DASHUSD','AAVEUSD','MANAUSD','CRVUSD','BANDUSD', 'GRTUSD','QTUMUSD','ZRXUSD','ZENUSD','ANKRUSD','WAVESUSD','BATUSD','MKRUSD', 'FILUSD', 'ETCUSD', 'PAXGUSD','REPUSD', 'KNCUSD','ONTUSD']
d1 = datetime.now() - timedelta(hours = -4, minutes =3)
d2 = d1.strftime("%d/%m/%Y %H:%M:%S")
average_price_change_percentage_list = []

max_pair = ""
quantity=""
symbol=""
buy_market_order_price =""
    

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'pancakeswap-prediction-google-sheets-api-key.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets','v4', credentials=credentials)

SHEET_ID="116dZNCsx4j8lo68dGkXkTTOwn7WCORJg1QIsXxCH9WE"
 #Call Sheets API
sheet= service.spreadsheets()	 

def compound1():
 summary_list = []

 symbol_limit = sheet.values().get(spreadsheetId=SHEET_ID,range = "price_change!C16").execute()
 global symbol
 symbol = sheet.values().get(spreadsheetId=SHEET_ID,range = "price_change!B28").execute()

 symbol=symbol.get('values')
 symbol= str(symbol[0][0])
 symbol_limit=symbol_limit.get('values')
 symbol_limit = symbol_limit[0][0]

 print(symbol)
 assetbalance =client.get_asset_balance(asset='USDT') 
 result = sheet.values().append(spreadsheetId=SHEET_ID,range = 'analysis', valueInputOption="RAW", body={"majorDimension":"COLUMNS","values":[[float(assetbalance['free'])]]}).execute()
 symbol_ticker=client.get_ticker(symbol=symbol)
 price= symbol_ticker['lastPrice']
 order= client.order_limit_buy(symbol=symbol, 
   side='BUY',
   quoteOrderQty= assetbalance['free'],
   price= price*.997
  )
 order_= pd.DataFrame(order)
 buy_market_order_price = (float(order_['cummulativeQuoteQty'].iloc[-1]))/float((order_['executedQty'].iloc[-1]))
 print(round(float(buy_market_order_price),3))
 print('bought')
 last_bought_pair = symbol
 last_bought_pair_without_USD = last_bought_pair.__str__().replace('USDT', '')
 global quantity
 quantity = client.get_asset_balance(last_bought_pair_without_USD)
 print(round(float(quantity['free']),0))
 limit = 1.0 +float(symbol_limit)/200

 


def sell(pair, quantity_,price):
    try:
      print(quantity_)      
      symbol_info = client.get_symbol_info(pair)
      step_size = symbol_info['filters'][2]['stepSize']
      tick_size = symbol_info['filters'][0]['tickSize']
      precision_stepsize = int(round(-math.log(float(step_size), 10), 0))
      precision_ticksize = int(round(-math.log(float(tick_size), 10), 0))
      rounded_quantity= round(float(quantity_['free']),precision_stepsize)
      last_price = client.get_symbol_ticker(symbol=pair)
      if rounded_quantity>float(quantity_['free']):
        rounded_quantity = rounded_quantity - float(step_size)
        print(rounded_quantity)
      if float(last_price['price']) < float(price)*1.002:
       order =  client.order_limit_sell(
       symbol = pair,
       side='SELL',
       quantity = rounded_quantity,
       price= round(float(price * 1.003),precision_ticksize),
    #   stopPrice =round(float(price *.995),precision_ticksize),
     #  stopLimitPrice=round(float(price *.995),precision_ticksize),
     #  stopLimitTimeInForce = 'GTC'
         )

      else:
          order_market = client.order_market_sell(
           symbol = pair,
           side = 'SELL',
           quantity = round(float(quantity_['free']),precision_stepsize)*.999
          )
      if order != None:
       print(order)
      else: 
       print(order_market)
    except BinanceAPIException as e:
    # error handling goes here
     print(e)
    except BinanceOrderException as e:
    # error handling goes here 
     print(e.message)
    
    
    # pair_trade()


def getLatestTradeOrder():
 exchange_info = client.get_exchange_info()
      # Extract every ticker where trade happened
 traded = []
 for i in exchange_info['symbols']:
            tickerTransactions = client.get_all_orders(symbol =i['symbol'] )
            if tickerTransactions :
                traded.append(tickerTransactions[-1])
              #  print(tickerTransactions["symbol"], " transactions available")
 orders=pd.DataFrame(traded)   
 print(orders)
       # print(orders['updateTime'].argmax( ))
 symbol_row= orders.iloc[orders['updateTime'].argmax( )]
       # print(symbol_row)
 print(symbol_row['symbol'])
 traded = symbol_row['symbol']
 print(traded)
 return traded

#getLatestTradeOrder()

   
def start_trade():
     threading.Timer(5.0, start_trade).start()
     assetbalance =client.get_asset_balance(asset='USDT')
     if float(assetbalance['free'])>10.1:
          # time.sleep(5)
           compound1()
     else:
      ab=client.get_asset_balance(asset=symbol)
      print(ab)
      if int(ab['free'])>0: 
        sell(symbol,quantity,buy_market_order_price)
      print('still waiting')
       
      # if client.get_open_orders() == None:
       # symbol_info = client.get_symbol_info(getLatestTradeOrder())
       # step_size = symbol_info['filters'][2]['stepSize']
      #  precision_stepsize = int(round(-math.log(float(step_size), 10), 0))
 
      #  order_market = client.order_market_sell(
      #     symbol = getLatestTradeOrder(),
      #     side = 'SELL',
      #     quantity = round(float(quantity['free']),precision_stepsize)*.999)
      #  print(order_market)
      

start_trade()




def pr(quantity_):
   tick_size  = .001
   precision_ticksize = int(round(-math.log(float(tick_size), 10), 0))
   print (precision_ticksize)
   quantity = round(float(quantity_),precision_ticksize)
   if quantity>float(quantity_):
     quantity = quantity - float(tick_size)
   print(quantity)

#pr('78.494')
