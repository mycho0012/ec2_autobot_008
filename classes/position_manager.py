# position_manager.py
import pandas as pd
import numpy as np
import time
import datetime


class PositionManager:
    def __init__(self, initial_capital=10000000, win_probability=0.6, net_odds=2):
        self.initial_capital = initial_capital
        self.win_probability = win_probability
        self.net_odds = net_odds
        self.execution_data = None
        self.balances = {'KRW-BTC': 0}  # Initialize with 0 balance for KRW-BTC
        self.trade_id=None
        self.position_data = None

    # 켈리 값을 계산한다.
    def kelly_fraction(self):
        """Calculate the investment amount using the Kelly fraction formula."""
        if self.win_probability <= 0 or self.win_probability >= 1:
            raise ValueError("Win probability must be between 0 and 1")
        if self.net_odds <= 0:
            raise ValueError("Net odds must be greater than 0")
        
        kelly = (self.win_probability * (self.net_odds + 1) - 1) / self.net_odds
        return max(0, kelly)  # Ensure we don't return a negative fraction

    # 초기원화발란스에 켈리값을 적요해서 베팅 금액을 설정한다. 
    def calculate_position_size(self, capital, kelly_fraction):
        """Calculate the position size based on the capital and Kelly fraction."""
        investment = capital * kelly_fraction
        return investment
    
    # def record_position_data(self, trade_id, executed_price,buy_quantity,sell_quantity,type):
       
    #     data = []

    #     if type == 'long':
    #         data.append({
    #             'position_id':f"psn_{int(time.time())}",  # Replace with actual trade ID
    #             'type': 'long',  # Replace with actual trade type,
    #             'symbol': 'KRW-BTC',
    #             'entry_price': executed_price,  # Reflect actual entry price
    #             'buy_quantity': buy_quantity,
    #             'sell_quantity': 0,
    #             'status': 'open'
    #         })
    #     elif type == 'short':
    #          data.append({
    #             'position_id':f"psn_{int(time.time())}",  # Replace with actual trade ID
    #             'type': 'short',  # Replace with actual trade type,
    #             'symbol': 'KRW-BTC',
    #             'entry_price':executed_price,  # Reflect actual entry price
    #             'buy_quantity': 0,
    #             'sell_quantity': sell_quantity,
    #             'status': 'close'
    #         })
        
    #     self.position_data = pd.DataFrame(data)
    #     return self.position_data

    
    def execution_trade(self, data_manager, entry_data, exit_data, invested_amount, coin_balance, max_loss):
        current_signal = entry_data.loc[entry_data.index[-1], 'entry']
        current_price = exit_data.loc[exit_data.index[-1], 'current_price']
        stop_loss = entry_data.loc[entry_data.index[-1], 'stop_loss']
        take_profit = entry_data.loc[entry_data.index[-1], 'take_profit']
        yyl = entry_data.loc[entry_data.index[-1], 'YYL']
        yyl_slow = entry_data.loc[entry_data.index[-1], 'YYL_slow']
        invested_amt = invested_amount
        quantity = invested_amt / current_price
        loss_threshold = max_loss

        #set trading log ID
         # Replace with actual trade ID
        self.trade_id=f"log_{int(time.time())}"
        
        if current_signal == 'long':
            print("Executing buy at market price")
            data_manager.execute_buy_market_price(invested_amt)
           # self.record_position_data(self.trade_id,current_price,invested_amt,quantity,coin_balance,current_signal)

        elif current_signal == 'short' or current_price <= stop_loss or current_price >= take_profit or current_price <= loss_threshold:
            print("Executing sell at market price")
            if coin_balance > 0:
                data_manager.execute_sell_market_price(coin_balance)
            elif coin_balance==0:
                print("No coin balance to sell.")
            #self.record_position_data(self.trade_id,current_price,invested_amt,quantity,coin_balance,current_signal)

        else:
            print("No execution as signal is neutral.")

        data = []
    
        data.append({
            'trade_id':self.trade_id,  # Replace with actual trade ID
            'type': current_signal,
            'timestamp': entry_data.index[-1],
            'symbol': 'KRW-BTC',
            'price': current_price,
            'yyl':yyl,
            'yyl_slow':yyl_slow,
            'quantity': quantity,
            'total_value': invested_amt,  # Reflect actual value
            'fee': 0.0,  # Reflect actual fees
            'status': 'successful',
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'strategy': 'YingYangVolatility',
            'notes': 'Trade execution log.'
        })
        self.execution_data = pd.DataFrame(data)
        return self.execution_data

    def read_positon_data(self, symbol):
        """Read the current balance for the given symbol."""
        if symbol in self.balances:
            return self.balances[symbol]
        else:
            raise ValueError(f"No balance information for symbol: {symbol}")

    # You may want to add a method to update balances after trades
    def update_balance(self, symbol, new_balance):
        """Update the balance for a given symbol."""
        self.balances[symbol] = new_balance

    