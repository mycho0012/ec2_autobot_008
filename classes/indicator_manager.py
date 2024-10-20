# indicator_manager.py
import pandas as pd
import numpy as np
import requests
import pyupbit

class IndicatorManager:
    def __init__(self, window=20,span=10,multiplier=2):
        self.window = window
        self.span = span
        self.multiplier = multiplier

    
    def calculate_indicator(self, prices):
        prices_high = prices['high']
        prices_low = prices['low']
        prices_close = prices['close']

        ma= prices_close.ewm(span=self.window).mean()
        diff = (prices_close - ma)

        # calculate ying yang volatility

        yangvol = np.sqrt((diff**2*(diff > 0)).rolling(window=self.window).mean())
        yingvol = np.sqrt((diff**2*(diff <=0)).rolling(window=self.window).mean())
        totalvol = np.sqrt(yangvol**2 + yingvol**2)
        epsilon = 1e-10
        YYL = ((yangvol-yingvol)/(totalvol+epsilon))*100
        YYL_slow = YYL.rolling(window=self.span).mean()

        # calculate upper band and pan river band
        upper_band = ma + self.multiplier * yangvol
        lower_band = ma - self.multiplier * yingvol
        pan_river_up = (ma+upper_band)/2
        pan_river_down = (ma+lower_band)/2

        # calcualte yingyang cycle
        yingyang_cycle = (upper_band-ma)**2



        indicators =pd.DataFrame({
                        'high':prices_high,
                        'low':prices_low,
                        'close':prices_close,
                        'ma':ma,
                        'YYL':YYL,
                        'YYL_slow':YYL_slow,
                        'upper_band':upper_band,
                        'lower_band':lower_band,
                        'pan_river_up':pan_river_up,
                        'pan_river_down':pan_river_down 
        })
        indicators = indicators.dropna()
        return indicators