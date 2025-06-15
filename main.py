from flask import Flask, request
import requests
import jwt
import time
import os

app = Flask(__name__)

# Config
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
SECRET_KEY = "12345678"  # JWT Secret
EXPIRATION_TIME = 5 * 60 * 60  # 5 hours (in seconds)

# Send message to Telegram
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })

# Generate JWT token
def generate_token():
    payload = {
        "exp": time.time() + EXPIRATION_TIME,
        "iat": time.time(),
        "scope": "upload"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Webhook endpoint
@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "👋 *Welcome!*\nSend me a Terabox link to get a direct download link. Devoloped by Streamify Bots")
        elif text == "/token":
            token = generate_token()
            send_message(chat_id, f"🪪 *Your 5-hour token:*\n\n`{token}`\n\n_Use this for upload authentication._")
        elif "terabox" in text:
            link = text.strip()
            proxy_link = f"https://teraboxdownloader.online/proxy.php?url={link}"
            send_message(chat_id, f"🔗 *Direct Link Preview:*\n{proxy_link}")
        else:
            send_message(chat_id, "❗ Unknown command. Try /start or /token.")

    return "ok"

# Run app with proper port binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
