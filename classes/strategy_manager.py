# strategy_manager.py
from tkinter import N
from turtle import position
import pandas as pd
import numpy as np
import pyupbit

class StrategyManager:
    def __init__(self, sl__multiplier=2, tp_multiplier=3):
        self.current_signal = None
        self.exit_signal = None
        self.sl_multiplier = sl__multiplier  
        self.tp_multiplier = tp_multiplier
        self.exit_signal = None

    
    def calculate_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        return atr


    def entry_condition(self, indicators_data):
        df = pd.DataFrame(index=indicators_data.index, data=indicators_data.values, columns=indicators_data.keys())

        # focus only on the last two candles to check the signals.
        last_two = df.loc[df.index[-2:], ['close','YYL', 'YYL_slow']]
        status_prev  = 1 if last_two.loc[last_two.index[0], 'YYL'] > last_two.loc[last_two.index[0], 'YYL_slow'] else (-1 if last_two.loc[last_two.index[0], 'YYL'] < last_two.loc[last_two.index[0], 'YYL_slow'] else 0)
        status_current = 1 if last_two.loc[last_two.index[1],'YYL'] > last_two.loc[last_two.index[1], 'YYL_slow'] else (-1 if last_two.loc[last_two.index[1], 'YYL'] < last_two.loc[last_two.index[1], 'YYL_slow'] else 0)
        add_row = pd.DataFrame({'status': [status_prev, status_current]}, index=last_two.index)
        last_two = pd.concat([last_two, add_row], axis=1)

        # set default signal ==0    
        entry = 'neutral'

        # Buy signal condition: signal_diff == 1 or 2 and YYL <= -75
        signal_diff = status_current - status_prev
        if (signal_diff in [1, 2]) and (last_two.loc[last_two.index[1], 'YYL'] <= -75):
            entry = 'long'
        
        elif (signal_diff in [-1, -2]) and (last_two.loc[last_two.index[1], 'YYL'] >= 75):
            entry = 'short'

        
        atr = self.calculate_atr(df, period=14)
        latest_atr = atr.loc[atr.index[-1]]

        # 현제캔들에서 스탑과 익절 레벨은 이전 캔들 클로즈 가격에 ATR을 적용한다
        current_price = df['close'].loc[df.index[-2]]
        stop_loss = current_price - (latest_atr * self.sl_multiplier)
        take_profit = current_price + (latest_atr * self.tp_multiplier)
        
        signals =pd.DataFrame({'signal':[signal_diff],'entry': [entry],'stop_loss':[stop_loss],'take_profit':[take_profit]}, index=[last_two.index[1]])
        
        
        last_two = pd.concat([last_two, signals], axis=1)
        self.current_signal = last_two
        
        return self.current_signal
    


    def exit_condition(self,entry_data):
        df = pd.DataFrame(index=entry_data.index, data=entry_data.values, columns=entry_data.keys())
        self.exit_signal = pd.DataFrame({
                            'current_price': [df['close'].loc[df.index[-1]]],
                            'signal': [df['signal'].loc[df.index[-1]]],
                            'stop_loss': [df['stop_loss'].loc[df.index[-1]]],
                            'take_profit': [df['take_profit'].loc[df.index[-1]]],
                            
        }, index=[df.index[-1]])

        return self.exit_signal

    def backtest():
        pass








