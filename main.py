from flask import Flask, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Telegram & Auth
BOT_TOKEN = "e1ee8114a3msh6aa90362eb62b31p1913f1jsne6671eb9046d"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
VALID_TOKEN = "12345678"

# TeraBox API via RapidAPI
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"
RAPIDAPI_HOST = "terabox-downloader-direct-download-link-generator2.p.rapidapi.com"
RAPIDAPI_BASE = f"https://{RAPIDAPI_HOST}/url"

# In-memory session control
user_tokens = {}
last_upload_time = {}

# Config
TOKEN_EXPIRY_HOURS = 5
UPLOAD_COOLDOWN_MINUTES = 2

def send_message(chat_id, text):
    url = API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False}
    requests.post(url, json=data)

def is_user_verified(chat_id):
    expiry = user_tokens.get(chat_id)
    return expiry and datetime.now() < expiry

def is_upload_allowed(chat_id):
    last_time = last_upload_time.get(chat_id)
    if not last_time:
        return True
    return datetime.now() >= last_time + timedelta(minutes=UPLOAD_COOLDOWN_MINUTES)

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "No update received"

    message = update.get("message")
    if not message:
        return "No message"

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "👋 *Welcome to TeraBox Direct Download Bot!*\nUse `/token <your_token>` to get started.")
        return "ok"

    if text.startswith("/token"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/token <your_token>`")
            return "ok"

        input_token = parts[1].strip()
        if input_token == VALID_TOKEN:
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            user_tokens[chat_id] = expiry
            send_message(chat_id, "✅ *Access granted for 5 hours!*")
        else:
            send_message(chat_id, "⛔ *Invalid token.*")
        return "ok"

    if text.startswith("/uploadurl"):
        if not is_user_verified(chat_id):
            send_message(chat_id, "⛔ *Token not verified.* Use `/token <your_token>`.")
            return "ok"

        if not is_upload_allowed(chat_id):
            send_message(chat_id, f"⏳ Please wait {UPLOAD_COOLDOWN_MINUTES} minutes between requests.")
            return "ok"

        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/uploadurl <terabox_url>`")
            return "ok"

        terabox_url = parts[1].strip()

        if "terabox" not in terabox_url:
            send_message(chat_id, "❗ Only *Terabox* links are supported.")
            return "ok"

        send_message(chat_id, "🔍 *Extracting download link...*")

        try:
            params = {"url": terabox_url}
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": RAPIDAPI_HOST
            }

            response = requests.get(RAPIDAPI_BASE, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if data.get("link"):
                filename = data.get("file_name", "file.mp4")
                size = data.get("size", "Unknown size")
                link = data["link"]

                message = (
                    f"✅ *Direct Link Generated!*\n"
                    f"🎬 *File:* `{filename}`\n"
                    f"📦 *Size:* {size}\n"
                    f"🔗 [Click to Download]({link})"
                )
                send_message(chat_id, message)
                last_upload_time[chat_id] = datetime.now()
            else:
                send_message(chat_id, "❌ Failed to extract link.")
        except Exception as e:
            send_message(chat_id, f"⚠️ Error: `{str(e)}`")

        return "ok"

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
