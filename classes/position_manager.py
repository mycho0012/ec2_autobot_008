# classes/position_manager.py
import logging

logger = logging.getLogger(__name__)

class PositionManager:
    def __init__(self, initial_balance, kelly_fraction=0.5):
        """
        Initializes the PositionManager.
        :param initial_balance: Starting KRW balance.
        :param kelly_fraction: Fraction of balance to use per trade.
        """
        self.balance = initial_balance
        self.kelly_fraction = kelly_fraction
        self.position = "neutral"
        self.entry_price = 0.0
        self.current_position_size = 0.0

        logger.info(f"PositionManager initialized with balance: {self.balance} KRW and Kelly fraction: {self.kelly_fraction}")

    def enter_position(self, current_price):
        """
        Enters a long position based on the Kelly fraction.
        :param current_price: Current price of the asset.
        :return: Size of the position entered.
        """
        try:
            position_size = (self.balance * self.kelly_fraction) / current_price
            self.position = "long"
            self.entry_price = current_price
            self.current_position_size = position_size
            self.balance -= self.current_position_size * current_price  # Deduct the invested amount
            logger.info(f"Entered long position: {self.current_position_size} BTC at {current_price} KRW. New balance: {self.balance} KRW.")
            return position_size
        except Exception as e:
            logger.error(f"Failed to enter position: {e}")
            raise

    def exit_position(self, current_price, reason="sell"):
        """
        Exits the current position.
        :param current_price: Current price of the asset.
        :param reason: Reason for exiting the position.
        :return: Profit or loss from the position.
        """
        try:
            if self.position == "long":
                profit_loss = (current_price - self.entry_price) * self.current_position_size
                self.balance += self.current_position_size * current_price  # Update balance after selling
                logger.info(f"Exited long position: {self.current_position_size} BTC at {current_price} KRW. P/L: {profit_loss} KRW. Reason: {reason}")
                # Reset position
                self.position = "neutral"
                self.entry_price = 0.0
                self.current_position_size = 0.0
                return profit_loss
            else:
                logger.warning("Attempted to exit a position when no position is held.")
                return 0.0
        except Exception as e:
            logger.error(f"Failed to exit position: {e}")
            raise

    def check_risk_management(self, current_price):
        """
        Checks if risk management conditions are met to exit the position.
        :param current_price: Current price of the asset.
        :return: Reason for exit if conditions are met, else None.
        """
        try:
            # Example condition: Stop-loss at 5% below entry price
            if self.position == "long":
                loss_threshold = 0.05  # 5%
                if (current_price - self.entry_price) / self.entry_price <= -loss_threshold:
                    self.exit_position(current_price, reason="stop_loss")
                    logger.info(f"Stop-loss triggered at {current_price} KRW.")
                    return "stop_loss"
                # Example condition: Take-profit at 10% above entry price
                profit_threshold = 0.10  # 10%
                if (current_price - self.entry_price) / self.entry_price >= profit_threshold:
                    self.exit_position(current_price, reason="take_profit")
                    logger.info(f"Take-profit triggered at {current_price} KRW.")
                    return "take_profit"
            return None
        except Exception as e:
            logger.error(f"Failed to perform risk management check: {e}")
            raise
