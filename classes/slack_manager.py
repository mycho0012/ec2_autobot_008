# slack_manager.py
# classes/slack_notifier.py
import requests


class SlackManager:
    def __init__(self, webhook_url):
        """
        Initializes the SlackNotifier class.
        :param webhook_url: Slack Webhook URL
        """
        self.webhook_url = webhook_url
        if not self.webhook_url:
            raise ValueError("Slack webhook URL must be provided.")
       

    def send_message(self, message):
        """
        Sends a message to Slack.
        :param message: Message content to send
        """
        payload = {
            "text": message
        }
        response = requests.post(self.webhook_url, json=payload)
          