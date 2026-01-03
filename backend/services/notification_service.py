
import os
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.n8n_webhook_url = os.getenv("N8N_TELEGRAM_WEBHOOK_URL")

    async def send_telegram_message(self, message: str, level: str = "info"):
        """
        Send a notification message via n8n Telegram Webhook.
        
        Args:
            message (str): The content of the notification
            level (str): Alert level (info, warning, error, success)
        """
        if not self.n8n_webhook_url:
            logger.warning("N8N_TELEGRAM_WEBHOOK_URL is not set. Skipping notification.")
            return False

        payload = {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.n8n_webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Notification sent successfully: {message[:20]}...")
                        return True
                    else:
                        logger.error(f"Failed to send notification. Status: {response.status}, Text: {await response.text()}")
                        return False
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False

notification_service = NotificationService()
