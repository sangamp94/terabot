from flask import Flask, request
import requests
import time
import re

app = Flask(__name__)

# ✅ Your Telegram Bot Token
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ✅ Token for user access verification
VALID_TOKEN = "12345678"

# ✅ Store the last upload time per user to limit frequency (in-memory)
last_upload_time = {}

# ✅ TeraBox parsing function using unofficial downloader
def get_direct_link(terabox_url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = session.get("https://teraboxdownloader.online/", headers=headers)
    
    # Simulate form submission
    payload = {
        "url": terabox_url
    }
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    post_response = session.post("https://teraboxdownloader.online/api/ajaxSearch", data=payload, headers=headers)

    try:
        result = post_response.json()
        if result.get("status") and result.get("links"):
            return result["links"][0]["link"]
        else:
            return None
    except Exception as e:
        print("Error parsing JSON:", e)
        return None

# ✅ Safe message sender with optional Markdown formatting
def send_message(chat_id, text, parse_mode=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    requests.post(f"{API_URL}sendMessage", json=payload)

# ✅ Main webhook route for Telegram bot
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "No message", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "👋 Welcome to TeraBox Downloader Bot!\nSend your access token to begin.")
        return "OK", 200

    # 🔐 Token Verification
    if text.strip() == VALID_TOKEN:
        send_message(chat_id, f"✅ Your access token is: `{VALID_TOKEN}`\nValid for 5 hours.", parse_mode="Markdown")
        return "OK", 200

    # ❌ If user hasn't verified token
    if VALID_TOKEN not in text:
        send_message(chat_id, "❌ Your token is not verified.\nPlease send the correct token to proceed.")
        return "OK", 200

    # ⏳ Enforce upload limit (1 request every 10 minutes per user)
    now = time.time()
    if chat_id in last_upload_time and now - last_upload_time[chat_id] < 600:
        remaining = int(600 - (now - last_upload_time[chat_id]))
        send_message(chat_id, f"⏳ Please wait {remaining} seconds before uploading another link.")
        return "OK", 200

    # ✅ Process TeraBox URL
    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        send_message(chat_id, "⚠️ No valid URL found in your message.")
        return "OK", 200

    tera_url = urls[0]
    send_message(chat_id, "⏳ Processing your TeraBox link, please wait...")

    direct_link = get_direct_link(tera_url)
    if direct_link:
        send_message(chat_id, f"✅ Direct Download Link:\n{direct_link}")
        last_upload_time[chat_id] = now
    else:
        send_message(chat_id, "❌ Failed to generate direct link. Please try again later.")

    return "OK", 200
