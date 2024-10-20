# main.py 
import pandas as pd
import numpy as np  
import pyupbit
import time 
import datetime
import schedule
import os
import signal
from dotenv import load_dotenv
from classes.data_manager import DataManager
from classes.position_manager import PositionManager    
from classes.strategy_manager import StrategyManager
from classes.indicator_manager import IndicatorManager
from classes.notion_manager import NotionManager
from classes.slack_manager import SlackManager

# Global variable to control the bot's execution
running = True

# Global variables for manager instances
data_manager = None
indicator_manager = None
position_manager = None
strategy_manager = None
notion_manager = None
slack_manager = None

def signal_handler(signum, frame):
    global running
    print("Received termination signal. Stopping the bot...")
    running = False

def initialize_bot():
    global data_manager, indicator_manager, position_manager, strategy_manager, notion_manager, slack_manager

    # load sensitive api stored in the env file for the further process
    load_dotenv(dotenv_path=os.path.join("config",".env"))
    access_key = os.getenv("ACCESS_KEY")
    secret_key = os.getenv("SECRET_KEY")
    ticker = "KRW-BTC"
    interval = "minute30"
    count = 300
    max_loss_pct = 0.05

    # assign class function and ready to use method in the classes
    data_manager = DataManager(access_key=access_key, secret_key=secret_key,ticker=ticker,interval=interval,count=count)
    indicator_manager = IndicatorManager(window=20,span=10,multiplier=2)
    position_manager = PositionManager()
    strategy_manager = StrategyManager() 
    notion_manager = NotionManager()
    slack_manager = SlackManager(
        webhook_url=os.getenv("SLACK_WEBHOOK_URL")
    )

    # Record initial account balance
    initial_balance = data_manager.get_account_balance()
    initial_coins = data_manager.get_coin_balance()
    coin_balance = int(initial_coins.loc[initial_coins.index[0], 'coin_balance'])
    current_price = int(initial_coins.loc[initial_coins.index[0], 'current_price'])
    notion_manager.record_account_balance(int(initial_balance), initial_coins.index[0], coin_balance, current_price)

    print(f"Bot initialized at {datetime.datetime.now()}.")
    slack_manager.send_message(f"Bot initialized at {datetime.datetime.now()}. Initial balance: {initial_balance} KRW, Current price: {current_price} KRW.")

def run_bot():
    global data_manager, indicator_manager, position_manager, strategy_manager, notion_manager, slack_manager

    ticker = "KRW-BTC"
    interval = "minute30"
    count = 300
    max_loss_pct = 0.05

    # get historical data per input arguments
    prices = data_manager.get_historical_data(ticker,interval,count)
    # Calculate indicators
    indicators = indicator_manager.calculate_indicator(prices)
    # Calculate Kelly value and initial investment amount
    kelly = position_manager.kelly_fraction()
    initial_balance = data_manager.get_account_balance()
    initial_coins = data_manager.get_coin_balance()
    invested_amount = initial_balance * kelly
    entry_data = strategy_manager.entry_condition(indicators) 
    exit_data = strategy_manager.exit_condition(entry_data)
        
    coin_balance = int(initial_coins.loc[initial_coins.index[0], 'coin_balance'])
    current_price = int(initial_coins.loc[initial_coins.index[0], 'current_price'])
    max_loss = int(current_price*max_loss_pct)

    # execution trades
    trade_log = position_manager.execution_trade(data_manager,entry_data,exit_data,invested_amount,coin_balance,max_loss)
    
    # Check if a new position (long or short) was opened and update Notion
    if isinstance(trade_log, pd.DataFrame) and not trade_log.empty:
        trade_type = trade_log['type'].iloc[0]
        if trade_type in ['long', 'short']:
            updated_balance = data_manager.get_account_balance()
            updated_coins = data_manager.get_coin_balance()
            updated_coin_balance = int(updated_coins.loc[updated_coins.index[0], 'coin_balance'])
            updated_current_price = int(updated_coins.loc[updated_coins.index[0], 'current_price'])
            notion_manager.record_account_balance(int(updated_balance), updated_coins.index[0], updated_coin_balance, updated_current_price)
            print(f"New {trade_type} position opened. Updated Notion with new account balance.")
    
    # Create trade log in Notion
    notion_manager.create_trade_log(trade_log)
    
    slack_manager.send_message(f"Bot running completed at {datetime.datetime.now()}. Current price: {current_price} KRW, Invested amount: {invested_amount} KRW.")

def time_until_next_30min():
    now = datetime.datetime.now()
    minutes_to_next = 30 - (now.minute % 30)
    seconds_to_next = minutes_to_next * 60 - now.second
    return seconds_to_next

def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Bot starting. Press Ctrl+C to stop.")
    
    initialize_bot()

    while running:
        run_bot()
        wait_time = time_until_next_30min()
        minutes, seconds = divmod(wait_time, 60)
        
        print(f"Waiting for {minutes} minutes and {seconds} seconds until next execution. Current time: {datetime.datetime.now()}")
        
        for _ in range(wait_time):
            if not running:
                break
            time.sleep(1)  # Sleep for 1 second, check running status every second

    print("Bot terminated.")

if __name__ == "__main__":
    main()
