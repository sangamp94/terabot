from flask import Flask, request
from telegram import Bot
import requests
import urllib.parse
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
bot = Bot(BOT_TOKEN)

# Token & cooldown system
VALID_TOKEN = "12345678"
user_tokens = {}         # chat_id: expiry time
last_use_time = {}       # chat_id: last use
TOKEN_EXPIRY_HOURS = 5
COOLDOWN_MINUTES = 2


def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


def is_user_verified(chat_id):
    expiry = user_tokens.get(chat_id)
    return expiry and datetime.now() < expiry


def is_cooldown_over(chat_id):
    last_time = last_use_time.get(chat_id)
    return not last_time or datetime.now() >= last_time + timedelta(minutes=COOLDOWN_MINUTES)


def extract_direct_link(terabox_url):
    try:
        with requests.Session() as session:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = session.get(terabox_url, headers=headers, allow_redirects=True)
            if "data.terabox" in res.url:
                return res.url
            return None
    except Exception as e:
        return None


@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "No update"

    message = update.get("message")
    if not message:
        return "No message"

    chat_id = message["chat"]["id"]
    text = message.get("text")

    if text and text.startswith("/start"):
        send_message(chat_id, "👋 *Welcome to TeraBox Downloader Bot!*\nSend `/token YOUR_TOKEN` to activate.")
        return "ok"

    if text and text.startswith("/token"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/token YOUR_TOKEN`")
            return "ok"

        if parts[1].strip() == VALID_TOKEN:
            user_tokens[chat_id] = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            send_message(chat_id, "✅ *Token verified! You can now use the bot for 5 hours.*")
        else:
            send_message(chat_id, "⛔ *Invalid token.*")
        return "ok"

    if text and text.startswith("/getlink"):
        if not is_user_verified(chat_id):
            send_message(chat_id, "🔒 *Unauthorized!*\nUse `/token YOUR_TOKEN` first.")
            return "ok"

        if not is_cooldown_over(chat_id):
            send_message(chat_id, "⏳ *Please wait before using again.*")
            return "ok"

        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/getlink <terabox_url>`")
            return "ok"

        link = parts[1].strip()
        send_message(chat_id, "🔍 Extracting direct link...")

        direct_link = extract_direct_link(link)
        if direct_link:
            send_message(chat_id, f"✅ *Here is your direct link:*\n[Download Now]({direct_link})")
            last_use_time[chat_id] = datetime.now()
        else:
            send_message(chat_id, "❌ *Failed to extract download link.* Please check the URL.")

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
