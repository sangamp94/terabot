from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

VALID_TOKEN = "12345678"  # your auth token
TOKEN_EXPIRY_SECONDS = 18000  # 5 hours

import time
token_issue_time = time.time()
last_upload_time = {}

def is_token_valid():
    return time.time() - token_issue_time < TOKEN_EXPIRY_SECONDS

def send_message(chat_id, text):
    requests.post(f"{API_URL}sendMessage", json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "👋 Welcome! Send me a TeraBox link to get a direct download link.")
        return "ok"

    if text.startswith("/token"):
        send_message(chat_id, f"✅ Your access token is: `{VALID_TOKEN}`\nValid for 5 hours.", parse_mode="Markdown")
        return "ok"

    # check token
    if VALID_TOKEN not in text:
        send_message(chat_id, "❌ Invalid token. Please use your token to authenticate.")
        return "ok"

    # rate limit 10 mins
    user_id = str(chat_id)
    current_time = time.time()
    if user_id in last_upload_time and current_time - last_upload_time[user_id] < 600:
        wait = int(600 - (current_time - last_upload_time[user_id]))
        send_message(chat_id, f"⏳ Please wait {wait} seconds before uploading again.")
        return "ok"
    last_upload_time[user_id] = current_time

    try:
        send_message(chat_id, "⏳ Fetching the direct link, please wait...")

        # Extract actual URL from message
        for part in text.split():
            if "teraboxapp.com/s/" in part:
                terabox_url = part.strip()
                break
        else:
            send_message(chat_id, "⚠️ No valid TeraBox link found in your message.")
            return "ok"

        # API call to teraboxdownloader.online
        api_response = requests.post(
            "https://teraboxdownloader.online/api.php",
            json={"url": terabox_url},
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        result = api_response.json()

        if "direct_link" not in result:
            send_message(chat_id, f"⚠️ Failed to get direct link.\n\nResponse: `{result}`")
            return "ok"

        # Format the response
        direct_link = result["direct_link"]
        file_name = result.get("file_name", "Unknown file")
        size = result.get("size", "Unknown size")
        thumb = result.get("thumb", None)

        proxy_link = f"https://teraboxdownloader.online/proxy.php?url={direct_link}"

        reply = f"""🎬 *{file_name}*
📦 Size: {size}

🔗 Direct Link Preview:
{proxy_link}
"""

        if thumb:
            requests.post(f"{API_URL}sendPhoto", json={
                "chat_id": chat_id,
                "photo": thumb,
                "caption": reply,
                "parse_mode": "Markdown"
            })
        else:
            send_message(chat_id, reply)

    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")

    return "ok"

# Run with port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
