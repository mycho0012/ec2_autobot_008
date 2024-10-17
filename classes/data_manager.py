# classes/data_manager.py
import pyupbit
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, access_key, secret_key):
        try:
            self.upbit = pyupbit.Upbit(access_key, secret_key)
            logger.info("Upbit client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Upbit client: {e}")
            raise

    def get_historical_data(self, symbol='KRW-BTC', interval='minute30', count=100):
        """
        Fetches historical data for a specified symbol from Upbit.
        :param symbol: Trading symbol (default: 'KRW-BTC')
        :param interval: Data interval (default: 'minute30')
        :param count: Number of candles to fetch (default: 100)
        :return: OHLCV data as a pandas DataFrame
        """
        try:
            df = pyupbit.get_ohlcv(symbol, interval=interval, count=count)
            if df is not None:
                logger.info(f"Historical data for {symbol} fetched successfully.")
            else:
                logger.warning(f"No historical data returned for {symbol}.")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise

    def get_balance(self, currency='KRW'):
        """
        Retrieves the balance of a specific currency from Upbit.
        :param currency: Currency code (default: 'KRW')
        :return: Balance as a float
        """
        try:
            balance = self.upbit.get_balance(currency)
            logger.info(f"Balance for {currency}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Failed to fetch balance for {currency}: {e}")
            raise

    def get_balances(self):
        """
        Retrieves all balances from Upbit.
        :return: List of balance dictionaries
        """
        try:
            balances = self.upbit.get_balances()
            logger.info("Fetched all balances successfully.")
            return balances
        except Exception as e:
            logger.error(f"Failed to fetch balances: {e}")
            raise

    def get_current_price(self, symbol='KRW-BTC'):
        """
        Fetches the current price for a specified symbol from Upbit.
        :param symbol: Trading symbol (default: 'KRW-BTC')
        :return: Current price as a float
        """
        try:
            price = pyupbit.get_current_price(symbol)
            if price is not None:
                logger.info(f"Current price for {symbol}: {price}")
            else:
                logger.warning(f"No current price returned for {symbol}.")
            return price
        except Exception as e:
            logger.error(f"Failed to fetch current price for {symbol}: {e}")
            raise

    def calculate_total_coin_value(self):
        """
        Calculates the total value of all coins in KRW.
        :return: Total coin value as a float
        """
        try:
            balances = self.upbit.get_balances()
            total = 0
            for balance in balances:
                if balance['currency'] != 'KRW' and float(balance['balance']) > 0:
                    symbol = f"KRW-{balance['currency']}"
                    current_price = self.get_current_price(symbol)
                    if current_price is not None:
                        total += float(balance['balance']) * current_price
                    else:
                        logger.warning(f"Skipping {balance['currency']} due to missing price.")
            logger.info(f"Total coin value: {total} KRW")
            return total
        except Exception as e:
            logger.error(f"Failed to calculate total coin value: {e}")
            raise
