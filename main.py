import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# ✅ Telegram Bot Token
BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ✅ RapidAPI credentials
RAPIDAPI_KEY = "e1ee8114a3msh6aa90362eb62b31p1913f1jsne6671eb9046d"
RAPIDAPI_HOST = "terabox-downloader-direct-download-link-generator2.p.rapidapi.com"
TERABOX_API_URL = f"https://{RAPIDAPI_HOST}/url"

# Send message to Telegram user
def send_message(chat_id, text, parse_mode="Markdown"):
    url = TELEGRAM_API + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    requests.post(url, json=payload)


@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("/start") or text.startswith("/help"):
        send_message(chat_id, "👋 *Welcome!*\nUse `/download <terabox_link>` to get the direct link.")
        return "ok"

    elif text.startswith("/download"):
        parts = text.split(" ", 1)
        if len(parts) != 2:
            send_message(chat_id, "❗ Usage:\n/download https://terabox.com/s/...")
            return "ok"

        link = parts[1].strip()
        if "terabox.com" not in link:
            send_message(chat_id, "❗ Please provide a valid Terabox link.")
            return "ok"

        send_message(chat_id, "🔄 Fetching download link...")

        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        try:
            response = requests.get(TERABOX_API_URL, headers=headers, params={"url": link}, timeout=30)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and data:
                file = data[0]
                filename = file.get("file_name")
                size = file.get("size")
                dl_link = file.get("direct_link")

                reply = (
                    f"✅ *Download Ready!*\n\n"
                    f"📁 File: `{filename}`\n"
                    f"📦 Size: {size}\n"
                    f"🔗 [Click to Download]({dl_link})"
                )
                send_message(chat_id, reply)
            else:
                send_message(chat_id, "⚠️ No file found or invalid response.")
        except Exception as e:
            send_message(chat_id, f"❌ Error:\n`{str(e)}`")

        return "ok"

    return "ok"


if __name__ == "__main__":
    # For local testing, use a tool like ngrok to expose your port
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
