# classes/notion_manager.py
import os
import logging
from notion_client import Client
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class NotionManager:
    def __init__(self):
        """
        Initializes the NotionManager class.
        """
        try:
            self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
            self.account_balance_db = os.getenv("NOTION_ACCOUNT_BALANCE_DB_ID")
            self.coin_balance_db = os.getenv("NOTION_COIN_BALANCE_DB_ID")
            self.trade_log_db = os.getenv("NOTION_TRADE_LOG_DB_ID")
            logger.info("Notion client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            raise

    def record_account_balance(self, krw_balance, total_coin_value, coins=None):
        """
        Records KRW balance and total coin value to Notion.
        :param krw_balance: KRW balance
        :param total_coin_value: Total coin value in KRW
        :param coins: Dictionary of coin balances and current prices
        """
        try:
            logger.info(f"Recording KRW Balance: {krw_balance}, Total Coin Value: {total_coin_value}")
            if coins:
                logger.info(f"Recording Coin Balances: {coins}")
            else:
                logger.info("No coin balances to record.")

            # Record account balance
            response = self.notion.pages.create(
                parent={"database_id": self.account_balance_db},
                properties={
                    "Timestamp": {
                        "title": [
                            {
                                "text": {
                                    "content": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                            }
                        ]
                    },
                    "KRW Balance": {
                        "number": krw_balance
                    },
                    "Total Coin Value in KRW": {
                        "number": total_coin_value
                    },
                    "Total Portfolio Value": {
                        "number": krw_balance + total_coin_value
                    }
                }
            )
            balance_page_id = response['id']
            logger.info(f"Account balance recorded with page ID: {balance_page_id}")

            # Record each coin balance
            if coins:
                for symbol, data in coins.items():
                    self.notion.pages.create(
                        parent={"database_id": self.coin_balance_db},
                        properties={
                            "Coin Symbol": {
                                "title": [
                                    {
                                        "text": {
                                            "content": symbol
                                        }
                                    }
                                ]
                            },
                            "Balance": {
                                "number": data['balance']
                            },
                            "Current Price": {
                                "number": data['current_price']
                            },
                            "Related Balance Record": {
                                "relation": [{"id": balance_page_id}]
                            }
                        }
                    )
                    logger.info(f"Recorded balance for {symbol} in Notion.")
            logger.info("KRW balance and coin balances recorded to Notion successfully.")
        except Exception as e:
            logger.error(f"Failed to record account balance to Notion: {e}")
            # Optionally, send Slack notification here if desired

    def create_trade_log(self, trade_data):
        """
        Records a trade log to Notion.
        :param trade_data: Dictionary containing trade details
        """
        try:
            timestamp = trade_data['timestamp']
            if not isinstance(timestamp, datetime):
                timestamp = pd.to_datetime(timestamp)

            self.notion.pages.create(
                parent={"database_id": self.trade_log_db},
                properties={
                    "Trade ID": {
                        "title": [{"text": {"content": trade_data['trade_id']}}]
                    },
                    "Type": {
                        "select": {"name": trade_data['type']}
                    },
                    "Timestamp": {
                        "date": {"start": timestamp.isoformat()}
                    },
                    "Symbol": {
                        "select": {"name": trade_data['symbol']}
                    },
                    "Price": {
                        "number": trade_data['price']
                    },
                    "Quantity": {
                        "number": trade_data['quantity']
                    },
                    "Fee": {
                        "number": trade_data['fee']
                    },
                    "Status": {
                        "select": {"name": trade_data['status']}
                    },
                    "Related Trade ID": {
                        "relation": [{"id": trade_data.get('related_trade_id', '')}]
                    },
                    "Profit/Loss": {
                        "number": trade_data.get('profit_loss', 0)
                    },
                    "Strategy": {
                        "select": {"name": trade_data['strategy']}
                    },
                    "Notes": {
                        "rich_text": [{"text": {"content": trade_data['notes']}}]
                    }
                }
            )
            logger.info("Trade log recorded to Notion successfully.")
        except Exception as e:
            logger.error(f"Failed to record trade log to Notion: {e}")
            # Optionally, send Slack notification here if desired
