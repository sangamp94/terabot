import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Your bot token (keep it secret in production)
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"[✅] Message sent to {chat_id}: {text}")
        print(f"[ℹ️] Telegram API response: {resp.text}")
    except Exception as e:
        print(f"[❌] Failed to send message to {chat_id}: {e}")

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

        print(f"[DEBUG] Response HTML:\n{response.text[:2000]}")  # Debug first 2000 chars

        # Regex to find direct download link in anchor tags
        download_link_pattern = r'<a[^>]+href=["\'](https?://[^"\']+?)(?:["\'][^>]*>.*?(?:Download|Direct Link).*?</a>)'
        match = re.search(download_link_pattern, response.text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)

        # Fallback: JS variable link pattern
        js_link_pattern = r'(?:var|const|let)\s+downloadLink\s*=\s*["\'](https?://[^"\']+)["\']'
        js_match = re.search(js_link_pattern, response.text, re.IGNORECASE)
        if js_match:
            return js_match.group(1)

        print(f"[⚠️] No direct link found in response HTML for {tera_url}")
        return None
    except Exception as e:
        print(f"[❌] Error fetching direct link for {tera_url}: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    return "✅ TeraBox Bot is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)  # force=True to be sure to parse JSON
    print(f"[📩] Incoming update: {data}")

    if not data or "message" not in data:
        return jsonify({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    try:
        if text.startswith("/start"):
            send_message(chat_id, "👋 Welcome! Send me a Terabox link to get a direct download link.")
        elif any(domain in text for domain in ["terabox.com", "teraboxapp.com", "1024terabox.com"]):
            send_message(chat_id, "⏳ Processing your link, please wait...")
            link = get_direct_link(text)
            if link:
                send_message(chat_id, f"✅ Direct Download Link:\n{link}")
            else:
                send_message(chat_id, "❌ Failed to extract the download link. Try another link or try later.")
        else:
            send_message(chat_id, "⚠️ Please send a valid Terabox sharing link.")
    except Exception as e:
        print(f"[❌] Error processing message: {e}")

    return jsonify({"ok": True})

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{request.host}/{BOT_TOKEN}"  # auto-generate webhook URL
    res = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    return jsonify(res.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
