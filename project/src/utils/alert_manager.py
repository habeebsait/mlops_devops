import requests
import smtplib
from email.mime.text import MIMEText
import logging
import json
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, slack_webhook_url=None, email_config=None):
        self.slack_webhook_url = slack_webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.email_config = email_config or {}
        self.log_path = 'data/alerts/incident_log.json'
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def send_alert(self, message: str, level: str = 'WARNING'):
        """
        Dispatch alert to all configured channels.
        """
        timestamp = datetime.utcnow().isoformat()
        alert_data = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        
        # 1. Local Logging
        self._log_incident(alert_data)
        
        # 2. Slack
        if self.slack_webhook_url:
            self._send_slack(message, level)
            
        # 3. Email
        if self.email_config:
            self._send_email(message, level)

    def _log_incident(self, alert_data):
        try:
            # Append to JSON log
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []
                
            logs.append(alert_data)
            
            with open(self.log_path, 'w') as f:
                json.dump(logs, f, indent=4)
                
            logger.info(f"Alert logged locally: {alert_data['message']}")
        except Exception as e:
            logger.error(f"Failed to log incident: {e}")

    def _send_slack(self, message, level):
        try:
            color = '#FF0000' if level == 'CRITICAL' else '#FFA500'
            payload = {
                "text": f"*{level}*: {message}",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {"title": "Project", "value": "Phishing Detection Monitor", "short": True},
                            {"title": "Time", "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                        ]
                    }
                ]
            }
            response = requests.post(self.slack_webhook_url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Slack alert: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    def _send_email(self, message, level):
        # Placeholder for email logic
        pass
