from flask import Flask
import requests
import os
import threading
import time
import json

app = Flask(__name__)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or "YOUR_TEAMS_WEBHOOK_URL"
URL = "https://www.dancenter.com/"

def send_teams_alert(message):
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
        response = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload)
        if response.status_code == 200:
            print("✅ Message sent to Teams.")
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"❌ Exception sending Teams alert: {e}")

def check_website_loop():
    while True:
        try:
            response = requests.get(URL, timeout=15)
            if response.status_code == 200:
                message = f"✅ {URL} is up and running. Status code: {response.status_code}"
            else:
                message = f"⚠️ {URL} returned status {response.status_code}. Please check immediately!"
        except Exception as e:
            message = f"🚨 {URL} is NOT reachable.\nError: {str(e)}"

        # Send alert every time
        send_teams_alert(message)

        time.sleep(1800)  # wait 30 minutes before next check

@app.route("/")
def home():
    return "Website monitor is running."

if __name__ == "__main__":
    # Start the background thread for checking the website
    threading.Thread(target=check_website_loop, daemon=True).start()

    # Run Flask app on Render's assigned port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
