# classes/indicator.py
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class YingYangIndicator:
    def __init__(self, window=20, span=10, pan_band_multiplier=2):
        """
        Initializes the YingYangIndicator class.
        :param window: Moving average period for YingYang Volatility calculation
        :param span: Moving average period for YYL_slow calculation
        :param pan_band_multiplier: Multiplier for determining Pan Bands' upper and lower limits
        """
        self.window = window
        self.span = span
        self.pan_band_multiplier = pan_band_multiplier

    def calculate(self, price_data):
        """
        Calculates all indicators and returns them as a DataFrame.
        :param price_data: Price data (OHLCV DataFrame)
        :return: Indicators DataFrame
        """
        try:
            price_close = price_data['close']
            ma = price_close.ewm(span=self.window, adjust=False).mean()
            diff = price_close - ma

            # Ying Yang Volatility calculation
            yang_vol = np.sqrt((diff**2 * (diff > 0)).rolling(window=self.window).mean())
            ying_vol = np.sqrt((diff**2 * (diff <= 0)).rolling(window=self.window).mean())
            total_vol = np.sqrt(yang_vol**2 + ying_vol**2)
            epsilon = 1e-10  # Small value to prevent division by zero
            YYL = ((yang_vol - ying_vol) / (total_vol + epsilon)) * 100
            YYL_slow = YYL.rolling(window=self.span).mean()

            # Pan Bands calculation
            upper_band = ma + self.pan_band_multiplier * yang_vol
            lower_band = ma - self.pan_band_multiplier * ying_vol
            pan_river_up = (ma + upper_band) / 2
            pan_river_down = (ma + lower_band) / 2

            # YingYang Cycle calculation
            cycle_values = (upper_band - ma) ** 2 - (ma - lower_band) ** 2
            rolling_window = 70
            min_cycle = cycle_values.rolling(window=rolling_window).min()
            max_cycle = cycle_values.rolling(window=rolling_window).max()
            scaled_cycle = (cycle_values - min_cycle) / (max_cycle - min_cycle + epsilon) * 200 - 100
            scaled_cycle = scaled_cycle.fillna(0)  # Handle NaN values

            # Combine all indicators into a single DataFrame
            indicators = pd.DataFrame({
                'ma': ma,
                'yang_vol': yang_vol,
                'ying_vol': ying_vol,
                'total_vol': total_vol,
                'YYL': YYL,
                'YYL_slow': YYL_slow,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'pan_river_up': pan_river_up,
                'pan_river_down': pan_river_down,
                'yingyang_cycle': scaled_cycle
            })

            logger.info("YingYang indicators calculated successfully.")
            return indicators
        except Exception as e:
            logger.error(f"Failed to calculate YingYang indicators: {e}")
            raise
