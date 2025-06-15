import os
import re
import requests
from flask import Flask, request

app = Flask(__name__)

# Your bot token
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Function to send message to Telegram
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload)
        print(f"[✅] Message sent to {chat_id}: {text}")
        print(f"[ℹ️] Telegram API response: {resp.text}")
    except Exception as e:
        print(f"[❌] Failed to send message to {chat_id}: {e}")

# Function to extract the direct download link
def get_direct_link(tera_url):
    terabox_downloader_url = "https://teraboxdownloader.online/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Referer": terabox_downloader_url,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": terabox_downloader_url
    }
    payload = {
        "link": tera_url
    }

    try:
        response = requests.post(terabox_downloader_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()

        # Try to find link in HTML
        download_link_pattern = r'<a[^>]*href=["\'](https?://[^"\']*\.(?:zip|rar|mp4|avi|mkv|pdf|doc|docx|xlsx|pptx|gz|7z|exe|txt|jpg|png|gif|webp)[^"\']*)["\'][^>]*>(?:.*?Download|.*?Direct Link).*?</a>'
        match = re.search(download_link_pattern, response.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)

        # Try to find JS-based link
        js_link_pattern = r'(?:var|const|let)\s+downloadLink\s*=\s*["\'](https?://[^"\']*)["\']'
        js_match = re.search(js_link_pattern, response.text, re.IGNORECASE)
        if js_match:
            return js_match.group(1)

        print(f"[⚠️] No direct link found in HTML for {tera_url}")
        return None
    except Exception as e:
        print(f"[❌] Error fetching direct link for {tera_url}: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    return "✅ TeraBox Bot is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"[📩] Incoming update: {data}")

    if not data or "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "👋 Welcome! Send me a Terabox link to get a direct download link.")
    elif "terabox.com" in text or "teraboxapp.com" in text:
        send_message(chat_id, "⏳ Processing your link, please wait...")
        link = get_direct_link(text)
        if link:
            send_message(chat_id, f"✅ Direct Download Link:\n{link}")
        else:
            send_message(chat_id, "❌ Failed to extract the download link. Try another link or try later.")
    else:
        send_message(chat_id, "⚠️ Please send a valid Terabox sharing link.")

    return {"ok": True}

# Helper route to set webhook manually
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{request.host}/{BOT_TOKEN}"  # auto-generates correct domain
    res = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    return res.json()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
