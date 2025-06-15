from flask import Flask, request
import requests
import os

BOT_TOKEN = "PLACEHOLDER"  # Replace with your Telegram bot token
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)

def get_direct_link_from_terabox(url):
    # Dummy placeholder logic — replace with real TeraBox scraping
    if "terabox.com" not in url:
        return None
    # Simulate a parsed download link
    return "https://download-link-from-terabox.com/example"

def send_message(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    requests.post(f"{API_URL}sendMessage", data=data)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if "terabox.com" in text:
            send_message(chat_id, "🔍 Processing your TeraBox link...")
            direct_link = get_direct_link_from_terabox(text)
            if direct_link:
                send_message(chat_id, f"✅ Direct Link:\n{direct_link}")
            else:
                send_message(chat_id, "❌ Could not extract link.")
        else:
            send_message(chat_id, "❌ Please send a valid TeraBox link.")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
