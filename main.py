from flask import Flask, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
VALID_TOKEN = "12345678"
user_tokens = {}
last_upload_time = {}

TOKEN_EXPIRY_HOURS = 5
UPLOAD_COOLDOWN_MINUTES = 2


def send_message(chat_id, text):
    url = API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=data)


def is_user_verified(chat_id):
    expiry = user_tokens.get(chat_id)
    return expiry and datetime.now() < expiry


def is_upload_allowed(chat_id):
    last_time = last_upload_time.get(chat_id)
    if not last_time:
        return True
    return datetime.now() >= last_time + timedelta(minutes=UPLOAD_COOLDOWN_MINUTES)


@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return "No update received"

    message = update.get("message")
    if not message:
        return "No message"

    chat_id = message["chat"]["id"]
    text = message.get("text")

    if text and text.startswith("/start"):
        send_message(chat_id, "👋 *Hello, I am a Terabox Direct Download Bot!*")
        return "ok"

    if text and text.startswith("/token"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/token <your_token>`")
            return "ok"

        input_token = parts[1].strip()
        if input_token == VALID_TOKEN:
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            user_tokens[chat_id] = expiry
            send_message(chat_id, f"✅ *Access granted for 5 hours!*")
        else:
            send_message(chat_id, "⛔ *Invalid token.*")
        return "ok"

    elif text and text.startswith("/uploadurl"):
        if not is_user_verified(chat_id):
            send_message(chat_id, "⛔ *Token not verified.* Use `/token <your_token>`.")
            return "ok"

        if not is_upload_allowed(chat_id):
            send_message(chat_id, f"⏳ Please wait {UPLOAD_COOLDOWN_MINUTES} minutes between downloads.")
            return "ok"

        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/uploadurl <terabox_url>`")
            return "ok"

        url = parts[1].strip()
        if "terabox.com" not in url:
            send_message(chat_id, "❗ Only *Terabox* links are supported.")
            return "ok"

        send_message(chat_id, "🔍 Extracting Terabox download link...")

        try:
            # Replace with a real extractor if needed (this is a dummy/fake endpoint for demo)
            res = requests.get(f"https://terabox-to-direct-link-api.vercel.app/api?url={url}", timeout=20).json()

            if res.get("success") and res.get("download_url"):
                download_url = res["download_url"]
                filename = res.get("filename", "video.mp4")
                send_message(chat_id, f"✅ *Direct link generated!*\n🎬 **File**: `{filename}`\n🔗 [Click to Download]({download_url})")
                last_upload_time[chat_id] = datetime.now()
            else:
                send_message(chat_id, f"❌ Failed to extract link.\nDetails: {res.get('message', 'Unknown error')}")
        except Exception as e:
            send_message(chat_id, f"⚠️ Error: `{str(e)}`")
        return "ok"

    return "ok"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
