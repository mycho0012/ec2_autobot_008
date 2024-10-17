# main.py
import os
import logging
import time
import schedule
from dotenv import load_dotenv
from classes.data_manager import DataManager
from classes.indicator import YingYangIndicator
from classes.strategy import TradingStrategy
from classes.position_manager import PositionManager
from classes.notion_manager import NotionManager
from classes.slack_notifier import SlackNotifier

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/trading_bot.log"),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Ying Yang Trading Bot...")

    # Load environment variables
    load_dotenv(dotenv_path=os.path.join('config', '.env'))

    # Initialize classes
    data_manager = DataManager(
        access_key=os.getenv("ACCESS_KEY"),
        secret_key=os.getenv("SECRET_KEY")
    )
    indicator = YingYangIndicator(
        window=20,
        span=10,
        pan_band_multiplier=2
    )
    strategy = TradingStrategy()
    initial_balance = data_manager.get_balance("KRW")  # Get KRW balance
    if initial_balance is None:
        logger.error("Failed to retrieve initial KRW balance.")
        return
    position_manager = PositionManager(initial_balance=initial_balance)
    notion_manager = NotionManager()
    slack_notifier = SlackNotifier(
        webhook_url=os.getenv("SLACK_WEBHOOK_URL")
    )

    # Update initial account balance and coin balances to Notion
    try:
        logger.info("Updating initial account balance to Notion...")
        krw_balance = data_manager.get_balance("KRW")
        total_coin_value = data_manager.calculate_total_coin_value()  # Calculate total coin value
        if krw_balance is not None:
            # Fetch each coin's balance and current price
            coin_balances = data_manager.get_balances()
            coins = {}
            for coin in coin_balances:
                if coin['currency'] == 'KRW':
                    continue
                symbol = f"KRW-{coin['currency']}"
                balance = float(coin['balance'])
                current_price = data_manager.get_current_price(symbol)
                coins[coin['currency']] = {'balance': balance, 'current_price': current_price}
            # Log the collected coins data for debugging
            logger.info(f"Collected coins data: {coins}")
            notion_manager.record_account_balance(krw_balance, total_coin_value, coins)
            logger.info("Initial KRW balance and coin balances updated to Notion.")
        else:
            logger.error("Failed to retrieve KRW balance from Upbit.")
    except Exception as e:
        logger.error(f"Error updating Notion with initial balance: {e}")
        slack_notifier.send_message(f"ERROR: {e}")

    # Define trading execution function
    def run_trading():
        try:
            logger.info("Running trading strategy...")
            # Fetch historical data
            price_data = data_manager.get_historical_data()
            if price_data is None or price_data.empty:
                logger.warning("No price data fetched. Skipping this cycle.")
                return

            # Calculate indicators
            indicators = indicator.calculate(price_data)

            # Generate signals
            signals = strategy.generate_signals(indicators, price_data)

            # Process the latest signal
            latest_signal = signals.iloc[-1]['Signal']
            current_price = price_data['close'].iloc[-1]
            logger.info(f"Latest signal: {latest_signal}, Current price: {current_price} KRW.")

            if latest_signal == 1 and position_manager.position == "neutral":
                # Buy signal and no current position
                position_size = position_manager.enter_position(current_price)
                # Execute buy order (actual order logic required)
                data_manager.upbit.buy_market_order('KRW-BTC', position_size)
                logger.info(f"Executing Buy Order at {current_price} KRW for {position_size} BTC.")
                # Record trade log
                notion_manager.create_trade_log({
                    'trade_id': f"buy_{int(time.time())}",  # Replace with actual trade ID
                    'type': 'Buy',
                    'timestamp': price_data.index[-1],
                    'symbol': 'KRW-BTC',
                    'price': current_price,
                    'quantity': position_size,
                    'fee': 0.0,  # Reflect actual fees
                    'status': 'Completed',
                    'strategy': 'YingYangVolatility',
                    'notes': 'Buy signal triggered.'
                })
                slack_notifier.send_message(f"Buy order executed at {current_price} KRW for {position_size} BTC.")

            elif latest_signal == -1 and position_manager.position == "long":
                # Sell signal and current long position
                position_size = position_manager.current_position_size  # Ensure this attribute exists
                profit_loss = position_manager.exit_position(current_price, reason="sell")
                # Execute sell order (actual order logic required)
                data_manager.upbit.sell_market_order('KRW-BTC', position_size)
                logger.info(f"Executing Sell Order at {current_price} KRW for {position_size} BTC.")
                # Record trade log
                notion_manager.create_trade_log({
                    'trade_id': f"sell_{int(time.time())}",  # Replace with actual trade ID
                    'type': 'Sell',
                    'timestamp': price_data.index[-1],
                    'symbol': 'KRW-BTC',
                    'price': current_price,
                    'quantity': position_size,
                    'fee': 0.0,  # Reflect actual fees
                    'status': 'Completed',
                    'strategy': 'YingYangVolatility',
                    'notes': 'Sell signal triggered.',
                    'profit_loss': profit_loss
                })
                slack_notifier.send_message(f"Sell order executed at {current_price} KRW for {position_size} BTC.")

            # Risk management check
            exit_reason = position_manager.check_risk_management(current_price)
            if exit_reason:
                # Additional logic needed when exiting due to risk management
                # Trade log already handled in position_manager
                slack_notifier.send_message(f"Position exited due to {exit_reason} at {current_price} KRW.")

        except Exception as e:
            logger.error(f"Error during trading execution: {e}")
            slack_notifier.send_message(f"ERROR: {e}")

    # Schedule trading execution: every hour at :00 and :30 minutes
    schedule.every().hour.at(":00").do(run_trading)
    schedule.every().hour.at(":30").do(run_trading)

    logger.info("Bot is scheduled to run every hour at :00 and :30 minutes.")

    # Send bot start message to Slack
    initial_message = "YingYang Trading Bot has started successfully. Next run in 30 minutes."
    logger.info("Sending start message to Slack...")
    slack_notifier.send_message(initial_message)
    logger.info("Start message sent.")

    # Execute scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
