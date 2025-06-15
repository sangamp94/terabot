from flask import Flask, request
import requests
from telegram import Bot
from playwright.sync_api import sync_playwright
import urllib.parse
from datetime import datetime, timedelta
import os

app = Flask(__name__)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
bot = Bot(BOT_TOKEN)

VALID_TOKEN = "12345678"
user_tokens = {}         # chat_id: expiry time
last_request_time = {}   # chat_id: last used time
TOKEN_EXPIRY_HOURS = 5
REQUEST_COOLDOWN_MINUTES = 2


def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


def is_user_verified(chat_id):
    expiry = user_tokens.get(chat_id)
    return expiry and datetime.now() < expiry


def is_request_allowed(chat_id):
    last_time = last_request_time.get(chat_id)
    if not last_time:
        return True
    return datetime.now() >= last_time + timedelta(minutes=REQUEST_COOLDOWN_MINUTES)


def extract_direct_link(share_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(share_url, timeout=60000)
        page.wait_for_timeout(3000)
        frame = page.query_selector("iframe")
        if frame:
            page = frame.content_frame()
            page.wait_for_timeout(3000)
        video_tag = page.query_selector("video source")
        direct_url = video_tag.get_attribute("src") if video_tag else None
        browser.close()
        return urllib.parse.unquote(direct_url) if direct_url else None


@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "No update received"

    message = update.get("message")
    if not message:
        return "No message"

    chat_id = message["chat"]["id"]
    text = message.get("text")

    # /start
    if text and text.startswith("/start"):
        send_message(chat_id, "👋 *Welcome to the TeraBox Video Link Extractor Bot!*")
        return "ok"

    # /token <your_token>
    if text and text.startswith("/token"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/token <your_token>`")
            return "ok"

        input_token = parts[1].strip()
        if input_token == VALID_TOKEN:
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            user_tokens[chat_id] = expiry
            send_message(chat_id, f"✅ *Access granted for {TOKEN_EXPIRY_HOURS} hours!*")
        else:
            send_message(chat_id, "⛔ *Invalid token.*")
        return "ok"

    # /terabox <link>
    if text and text.startswith("/terabox"):
        if not is_user_verified(chat_id):
            send_message(chat_id, "⛔ *Token not verified.*\nUse `/token <your_token>` to activate access.")
            return "ok"

        if not is_request_allowed(chat_id):
            send_message(chat_id, f"⏳ Please wait before sending another request.")
            return "ok"

        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/terabox <TeraBox_Share_Link>`")
            return "ok"

        link = parts[1].strip()
        if not link.startswith("https://teraboxapp.com/s/"):
            send_message(chat_id, "⛔ Invalid TeraBox share link.")
            return "ok"

        send_message(chat_id, "🔍 Extracting video link...")

        try:
            direct_url = extract_direct_link(link)
            if direct_url:
                send_message(chat_id, f"✅ *Direct Link:*\n{direct_url}")
                last_request_time[chat_id] = datetime.now()
            else:
                send_message(chat_id, "❌ Could not find the video link.")
        except Exception as e:
            send_message(chat_id, f"⚠️ Error: `{str(e)}`")

        return "ok"

    return "ok"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
