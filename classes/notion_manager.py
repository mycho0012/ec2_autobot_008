# notion_manager.py
import os
import logging
from turtle import position
from notion_client import Client
from datetime import datetime
import pandas as pd

class NotionManager:
    def __init__(self):
        
        self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
        self.account_balance_db = os.getenv("NOTION_ACCOUNT_BALANCE_DB_ID")
        self.coin_balance_db = os.getenv("NOTION_COIN_BALANCE_DB_ID")
        self.trade_log_db = os.getenv("NOTION_TRADE_LOG_DB_ID")
        self.position_log_db = os.getenv("NOTION_POSITION_LOG_DB_ID")
        
    def record_account_balance(self, krw_balance, symbol, coin_balance, current_price):
        
        #KRW balance fetch
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
                }
               
            }
        )
        balance_page_id = response['id']
         
    # Record coin balance
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
                    "number": coin_balance
                },
                "Current Price": {
                    "number": current_price
                },
                "Related Balance Record": {
                    "relation": [{"id": balance_page_id}]
                }
            }
        )

    def create_trade_log(self, trade_data):
        if isinstance(trade_data, pd.DataFrame):
            trade_data = trade_data.to_dict('records')[0]

        timestamp = trade_data.get('timestamp', datetime.now())
        if not isinstance(timestamp, datetime):
            timestamp = pd.to_datetime(timestamp)

        properties = {
            "Trade ID": {
                "title": [{"text": {"content": trade_data.get('trade_id', '')}}]
            },
            "Type": {
                "select": {"name": trade_data.get('type', 'Unknown')}
            },
            "Timestamp": {
                "date": {"start": timestamp.isoformat()}
            },
            "Symbol": {
                "rich_text": [{"text": {"content": trade_data.get('symbol', 'Unknown')}}]
            },
            "Price": {
                "number": trade_data.get('price', 0)
            },
            "YYL":{
                "number": trade_data.get('yyl', 0)
            },
            "YYL Slow": {
                "number": trade_data.get('yyl_slow',0)        
            },
            "Quantity": {
                "number": trade_data.get('quantity', 0)
            },
            "Total Amount": {
                "number": trade_data.get('total_value', 0)
            },
            "Fee": {
                "number": trade_data.get('fee', 0)
            },
            "Status": {
                "select": {"name": trade_data.get('status', 'Unknown')}
            },
            "Stop Loss":{
                "number": trade_data.get('stop_loss', 0)    
            },
            "Take Profit":{
                "number": trade_data.get('take_profit', 0)
            },
            "Strategy": {
                "select": {"name": trade_data.get('strategy', 'Unknown')}
            },
            "Notes": {
                "rich_text": [{"text": {"content": trade_data.get('notes', '')}}]
            }
        }

        # Add optional fields if they exist in trade_data
        if 'related_trade_id' in trade_data:
            properties["Related Trade ID"] = {
                "relation": [{"id": trade_data['related_trade_id']}]
            }

        if 'profit_loss' in trade_data:
            properties["Profit/Loss"] = {
                "number": trade_data['profit_loss']
            }

        self.notion.pages.create(
            parent={"database_id": self.trade_log_db},
            properties=properties
        )


    def create_position_log(self, position_data):
        if isinstance(position_data, pd.DataFrame):
            position_data = position_data.to_dict('records')[0]

        timestamp = position_data.get('timestamp', datetime.now())
        if not isinstance(timestamp, datetime):
            timestamp = pd.to_datetime(timestamp)

        properties = {
            "Position ID": {
                "title": [{"text": {"content": position_data.get('position_id', '')}}]
            },
            "Symbol": {
                "rich_text": [{"text": {"content": position_data.get('symbol', 'Unknown')}}]
            },
             "Type": {
                "select": {"name": position_data.get('status', 'Unknown')}
            },
            "Entry Price": {
                "number": position_data.get('entry_price', 0)
            },
            "Initial Quantity": {
                "number": position_data.get('initial_quantity', 0)
            },
            "Current Quantity": {
                "number": position_data.get('current_quantity', 0)        
            },
            "Realized P/L": {
                "number": position_data.get('realized_pl', 0)
            },
            "Status": {
                "select": {"name": position_data.get('status', 'Unknown')}
            },
            "Timestamp": {
                "date": {"start": timestamp.isoformat()}
            },
              "Related Trade ID": {
                    "relation": {"id": position_data['related_trade_id']}
        }}

        # Add optional fields if they exist in position_data
        if 'related_trade_id' in position_data:
            properties["Related Trade ID"] = {
                "relation": [{"id": position_data['related_trade_id']}]
            }

        if 'unrealized_pl' in position_data:
            properties["Unrealized P/L"] = {
                "number": position_data['unrealized_pl']
            }

        self.notion.pages.create(
            parent={"database_id": self.position_log_db},
            properties=properties
        )

    def read_position_data(self, symbol):
        """
        Read the current balance for the given symbol from the Notion database.
        
        :param symbol: The symbol of the coin (e.g., 'KRW-BTC')
        :return: The current balance of the specified coin
        """
        query = {
            "database_id": self.coin_balance_db,
            "filter": {
                "property": "Coin Symbol",
                "title": {
                    "equals": symbol
                }
            },
            "sorts": [
                {
                    "property": "Related Balance Record",
                    "direction": "descending"
                }
            ],
            "page_size": 1
        }

        response = self.notion.databases.query(**query)

        if response['results']:
            latest_record = response['results'][0]
            return latest_record['properties']['Balance']['number']
        else:
            return 0  # Return 0 if no record found for the symbol
