# classes/strategy.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TradingStrategy:
    def __init__(self):
        """
        Initializes the TradingStrategy class.
        """
        self.signals = None

    def generate_signals(self, indicator_data, price_data):
        """
        Generates trading signals based on the latest candle.
        :param indicator_data: Ying Yang Volatility indicator DataFrame (including Pan Bands and YingYang Cycle)
        :param price_data: Price data (OHLCV DataFrame)
        :return: Signals DataFrame with only the latest signal
        """
        if indicator_data is None:
            raise ValueError("Indicator data must be provided.")

        try:
            # Combine price data with indicator data
            df = indicator_data.join(price_data['close'])
            df.dropna(inplace=True)

            if len(df) < 2:
                logger.warning("Not enough data to generate signals.")
                return pd.DataFrame({'Signal': [0]}, index=[df.index[-1]])

            # Focus only on the last two candles
            latest_two = df.iloc[-2:]

            # Calculate status for the last two candles
            status_prev = 1 if latest_two['YYL'].iloc[0] > latest_two['YYL_slow'].iloc[0] else (-1 if latest_two['YYL'].iloc[0] < latest_two['YYL_slow'].iloc[0] else 0)
            status_current = 1 if latest_two['YYL'].iloc[1] > latest_two['YYL_slow'].iloc[1] else (-1 if latest_two['YYL'].iloc[1] < latest_two['YYL_slow'].iloc[1] else 0)

            signal_diff = status_current - status_prev
            latest_timestamp = latest_two.index[-1]
            latest_price = latest_two['close'].iloc[1]

            signal = 0  # Default to no signal

            # Buy signal condition: signal_diff == 1 or 2 and YYL <= -75
            if (signal_diff in [1, 2]) and (latest_two['YYL'].iloc[1] <= -75):
                signal = 1
                logger.info(f"Buy signal generated at index {latest_timestamp}, Price: {latest_price} KRW.")

            # Sell signal condition: signal_diff == -1 or -2 and YYL >= 75
            elif (signal_diff in [-1, -2]) and (latest_two['YYL'].iloc[1] >= 75):
                signal = -1
                logger.info(f"Sell signal generated at index {latest_timestamp}, Price: {latest_price} KRW.")

            # Create a DataFrame with only the latest signal
            signals = pd.DataFrame({'Signal': [signal]}, index=[latest_timestamp])

            self.signals = signals
            logger.info("Signals generated successfully.")
            return self.signals
        except Exception as e:
            logger.error(f"Failed to generate signals: {e}")
            raise
