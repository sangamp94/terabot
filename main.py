from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"  # Replace with your bot token
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Function to send messages
def send_message(chat_id, text, parse_mode="Markdown"):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

# Root route to receive Telegram updates
@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Start command
        if text.startswith("/start"):
            send_message(chat_id, "👋 Welcome! Send me a *Terabox* link to get a direct download link.")
        
        # Terabox link handler
        elif "terabox.com" in text or "teraboxapp.com" in text:
            try:
                api_response = requests.post(
                    "https://teraboxdownloader.online/api.php",
                    json={"link": text},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                result = api_response.json()

                if "direct_link" in result:
                    real_link = result["direct_link"]
                    file_name = result.get("file_name", "Unknown File")
                    file_size = result.get("size", "Unknown Size")
                    thumb = result.get("thumb", "")

                    proxy_link = f"https://teraboxdownloader.online/proxy.php?url={real_link}"

                    msg = f"""🎬 *{file_name}*
📦 Size: {file_size}

🔗 [Download Now]({proxy_link})
"""
                    send_message(chat_id, msg)
                else:
                    send_message(chat_id, f"⚠️ Failed to get direct link.\n\nResponse: `{result}`", parse_mode="Markdown")

            except Exception as e:
                send_message(chat_id, f"❌ Error: `{str(e)}`", parse_mode="Markdown")

        # Other text
        else:
            send_message(chat_id, "❗ Please send a valid Terabox link.")
    
    return "OK"

# Required for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
