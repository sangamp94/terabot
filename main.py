from flask import Flask, request
from telegram import Bot
from playwright.sync_api import sync_playwright
import urllib.parse
import os

app = Flask(__name__)

# Replace with your actual Telegram bot token
BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
bot = Bot(BOT_TOKEN)

def send_message(chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

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

@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "Invalid"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/terabox"):
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
            else:
                send_message(chat_id, "❌ Could not find the video link.")
        except Exception as e:
            send_message(chat_id, f"⚠️ Error: `{str(e)}`")

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
