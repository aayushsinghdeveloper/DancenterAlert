from flask import Flask
import requests
import os
import threading
import time
import json

app = Flask(__name__)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or "YOUR_TEAMS_WEBHOOK_URL"
URL = "https://www.dancenter.com/"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
MAX_RETRIES = 3
RETRY_DELAY = 5
CHECK_INTERVAL = 1800  # 30 minutes

def send_teams_alert(message):
    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [{
                    "type": "TextBlock",
                    "text": message,
                    "wrap": True,
                    "size": "Medium",
                    "weight": "Bolder",
                    "color": "Good" if "✅" in message else "Attention"
                }]
            }
        }]
    }
    try:
        response = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload)
        if response.status_code == 200:
            print("✅ Message sent to Teams.")
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception sending Teams alert: {e}")

def check_website():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(URL, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return f"✅ {URL} is live. Status code: {response.status_code}"
            else:
                return f"⚠️ {URL} returned status {response.status_code}. Please check immediately!"
        except requests.exceptions.RequestException as e:
            # Ignore ProxyError / Connection errors caused by cloud network
            if "ProxyError" in str(e) or "Tunnel connection failed" in str(e):
                print(f"⚠️ Ignored network/proxy error: {e}")
                return f"⚠️ {URL} could not be checked due to network/proxy issue. Will retry next interval."
            elif attempt == MAX_RETRIES:
                return f"🚨 {URL} is NOT reachable after {MAX_RETRIES} attempts.\nError: {e}"
            else:
                time.sleep(RETRY_DELAY)

def check_website_loop():
    while True:
        message = check_website()
        if message:
            send_teams_alert(message)
        time.sleep(CHECK_INTERVAL)

@app.route("/")
def home():
    return "Website monitor is running."

if __name__ == "__main__":
    threading.Thread(target=check_website_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
