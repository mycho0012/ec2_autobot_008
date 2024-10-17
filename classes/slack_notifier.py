# classes/slack_notifier.py
import requests
import logging

logger = logging.getLogger(__name__)

class SlackNotifier:
    def __init__(self, webhook_url):
        """
        Initializes the SlackNotifier class.
        :param webhook_url: Slack Webhook URL
        """
        self.webhook_url = webhook_url
        if not self.webhook_url:
            logger.error("Slack webhook URL is not provided.")
            raise ValueError("Slack webhook URL must be provided.")
        logger.info("SlackNotifier initialized successfully.")

    def send_message(self, message):
        """
        Sends a message to Slack.
        :param message: Message content to send
        """
        payload = {
            "text": message
        }
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code != 200:
                logger.error(f"Slack notification failed: {response.text}")
            else:
                logger.info("Slack notification sent successfully.")
        except Exception as e:
            logger.error(f"Exception occurred while sending Slack message: {e}")
