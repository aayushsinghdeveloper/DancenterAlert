import requests
import time
import json

WEBHOOK_URL = "https://oyoenterprise.webhook.office.com/webhookb2/78fc0508-3816-4c6d-9ce3-f78d86d9acb7@04ec3963-dddc-45fb-afb7-85fa38e19b99/IncomingWebhook/3ef025a0f8b84c68b5b0e04b72430eab/e953c7f3-954d-4b3e-97b0-70880660db5f/V2Fapz2yPQJvpyx_I7XQgu7Z3-08j2i60FxLrH4nkS3Aw1"

url = "https://www.dancenter.com/"

def send_teams_alert(message):
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

    response = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    if response.status_code == 200:
        print("✅ Message sent to Teams.")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}, response: {response.text}")

def check_website():
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            send_teams_alert(f"✅ {url} is up and running. Status code: {response.status_code}")
        else:
            send_teams_alert(f"⚠️ {url} returned status {response.status_code}. Please check immediately!")
    except Exception as e:
        send_teams_alert(f"🚨 {url} is NOT reachable.\nError: {str(e)}")

if __name__ == "__main__":
    while True:
        check_website()
        time.sleep(1800)  # every 30 minutes
