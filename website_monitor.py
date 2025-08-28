import requests
import time
import json
from requests.exceptions import ProxyError, ConnectionError, SSLError

# 🔗 Your Teams webhook URL
WEBHOOK_URL = "https://oyoenterprise.webhook.office.com/webhookb2/78fc0508-3816-4c6d-9ce3-f78d86d9acb7@04ec3963-dddc-45fb-afb7-85fa38e19b99/IncomingWebhook/3ef025a0f8b84c68b5b0e04b72430eab/e953c7f3-954d-4b3e-97b0-70880660db5f/V2Fapz2yPQJvpyx_I7XQgu7Z3-08j2i60FxLrH4nkS3Aw1"

# 🌐 The site you want to monitor
URL = "https://www.dancenter.com/"

# Retry logic
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
CHECK_INTERVAL = 1800  # 30 minutes


def send_teams_alert(message):
    """Send a formatted alert to Microsoft Teams via webhook"""
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True,
                            "size": "Medium",
                            "weight": "Bolder",
                            "color": "Good" if "✅" in message else "Attention"
                        }
                    ]
                }
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        if response.status_code == 200:
            print("✅ Message sent to Teams.")
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"❌ Error sending to Teams: {e}")


def check_website():
    """Check if the website is up and return the appropriate message"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(URL, timeout=15)
            if response.status_code == 200:
                return f"✅ {URL} is up and running. Status code: {response.status_code}"
            else:
                return f"⚠️ {URL} returned status {response.status_code}. Please check immediately!"

        except (ProxyError, ConnectionError, SSLError, OSError) as e:
            # Ignore network/proxy errors — only log locally, no Teams alert
            print(f"⚠️ Ignored network/proxy error: {e}")
            return f"⚠️ {URL} could not be checked due to network/proxy issue. Will retry next interval."

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return f"🚨 {URL} is NOT reachable.\nError: {str(e)}"


if __name__ == "__main__":
    while True:
        status_message = check_website()
        send_teams_alert(status_message)
        time.sleep(CHECK_INTERVAL)
