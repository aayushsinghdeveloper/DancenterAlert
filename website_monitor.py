import os
import time
import threading
import requests
import json
from flask import Flask
from requests.exceptions import ProxyError, ConnectionError, SSLError

# 🔗 Teams Webhook URL from Railway env var
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 🌐 Website to monitor
URL = "https://www.dancenter.com/"

# Configs
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries
CHECK_INTERVAL = 1800  # 30 minutes


def send_teams_alert(message):
    """Send formatted alert to Teams"""
    if not WEBHOOK_URL:
        print("❌ No WEBHOOK_URL found in environment variables.")
        return

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
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
    """Check if website is live and return status"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(URL, timeout=15)
            if response.status_code == 200:
                return f"✅ {URL} is up and running. Status code: {response.status_code}"
            else:
                return f"⚠️ {URL} returned status {response.status_code}. Please check immediately!"

        except (ProxyError, ConnectionError, SSLError, OSError) as e:
            # ❌ Ignore network/proxy errors (won’t send to Teams)
            print(f"⚠️ Ignored network/proxy error: {e}")
            return None

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            else:
                return f"⚠️ Unexpected error while checking {URL}: {str(e)}"


def monitor_loop():
    """Background loop to check site every X minutes"""
    while True:
        status_message = check_website()
        if status_message:  # Only send if not ignored
            send_teams_alert(status_message)
        time.sleep(CHECK_INTERVAL)


# 🚀 Flask app for Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "Website Monitor is running ✅", 200


if __name__ == "__main__":
    # Start monitoring in background
    threading.Thread(target=monitor_loop, daemon=True).start()

    # Railway requires binding to 0.0.0.0:$PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
