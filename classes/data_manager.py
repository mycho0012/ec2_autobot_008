#data_manager.py
import pandas as pd
import numpy as np
import pyupbit

class DataManager:
    def __init__(self,access_key,secret_key,ticker='KRW-BTC',interval='minute30',count=300):
        self.upbit = pyupbit.Upbit(access_key,secret_key)
        self.ticker = ticker
        self.interval = interval
        self.count = count  
        self.coin_data = None

    def get_historical_data(self,ticker,interval,count):
        df=pyupbit.get_ohlcv(ticker,interval,count)
        return df


    def get_account_balance(self):
        account_balance = self.upbit.get_balance("KRW")
        return account_balance
    
    def get_coin_balance(self):
        balance = self.upbit.get_balance('KRW-BTC') 
        price =pyupbit.get_current_price('KRW-BTC')

        data=[]
        data.append({'symbol':'KRW-BTC',
                     'coin_balance':balance,
                     'current_price':price
                     })

        # if balance is None:
        #     balance = 0
        self.coin_data = pd.DataFrame(data)
        self.coin_data = self.coin_data.set_index('symbol')
       
        return self.coin_data
    

    def get_current_price(self,ticker):
        current_price = pyupbit.get_current_price(ticker)
        return current_price
    
    def execute_buy_market_price(self,ticker,invest_amount):
        self.upbit.buy_market_order(ticker,invest_amount)

    def exectute_sell_market_price(self,ticker,sell_amount):
        self.upbit.sell_market_order(ticker,sell_amount)

        