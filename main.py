from flask import Flask, request
import os
import requests
from datetime import datetime, timedelta
from telegram import Bot
from playwright.sync_api import sync_playwright

app = Flask(__name__)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
VALID_TOKEN = "12345678"  # Replace with a secure token
COOLDOWN_MINUTES = 2
TOKEN_EXPIRY_HOURS = 5

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
bot = Bot(BOT_TOKEN)

user_tokens = {}         # chat_id: expiry time
last_usage = {}          # chat_id: last use time


def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")


def extract_direct_link(share_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(share_url, timeout=60000)
        page.wait_for_timeout(5000)

        try:
            play_button = page.query_selector("video")
            if not play_button:
                return None
            src = play_button.get_attribute("src")
            return src if src.startswith("http") else None
        finally:
            browser.close()


def is_user_verified(chat_id):
    expiry = user_tokens.get(chat_id)
    return expiry and datetime.now() < expiry


def is_on_cooldown(chat_id):
    last = last_usage.get(chat_id)
    if not last:
        return False
    return datetime.now() < last + timedelta(minutes=COOLDOWN_MINUTES)


@app.route('/', methods=['POST'])
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
        send_message(chat_id, "👋 *Welcome to the TeraBox Downloader Bot!*\nUse `/token <your_token>` to begin.")
        return "ok"

    if text and text.startswith("/token"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/token <your_token>`")
            return "ok"

        input_token = parts[1].strip()
        if input_token == VALID_TOKEN:
            user_tokens[chat_id] = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            send_message(chat_id, "✅ *Token verified! You have 5 hours access.*")
        else:
            send_message(chat_id, "⛔ *Invalid token.*")
        return "ok"

    if text and text.startswith("/getlink"):
        if not is_user_verified(chat_id):
            send_message(chat_id, "🔒 *Access Denied.* Use `/token <your_token>` to verify.")
            return "ok"

        if is_on_cooldown(chat_id):
            send_message(chat_id, f"🕒 *Please wait {COOLDOWN_MINUTES} minutes between requests.*")
            return "ok"

        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "❗ Usage: `/getlink <terabox_share_url>`")
            return "ok"

        share_url = parts[1].strip()
        if not share_url.startswith("http"):
            send_message(chat_id, "❗ *Invalid URL provided.*")
            return "ok"

        send_message(chat_id, "🔍 *Fetching direct link from TeraBox...*")

        try:
            direct_link = extract_direct_link(share_url)
            if direct_link:
                send_message(chat_id, f"✅ *Direct Link:*\n`{direct_link}`")
                last_usage[chat_id] = datetime.now()
            else:
                send_message(chat_id, "❌ *Failed to extract the link.*")
        except Exception as e:
            send_message(chat_id, f"⚠️ *Error:* `{str(e)}`")

        return "ok"

    return "ok"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
