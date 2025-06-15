from flask import Flask, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"  # Replace with your actual bot token
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
VALID_TOKEN = "jai shree ram"
last_upload_time = {}

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if not chat_id or not text:
        return '', 200

    if text.startswith('/start'):
        send_message(chat_id, "👋 Welcome! Send me a Terabox link to get a direct download link.")
    elif text.startswith('/token'):
        token_expiry = datetime.utcnow() + timedelta(hours=5)
        send_message(chat_id, f"🔑 Token: `{VALID_TOKEN}`\n⏳ Valid for 5 hours (until {token_expiry.strftime('%H:%M')} UTC)")
    elif 'terabox' in text and 'http' in text:
        response_text, button = handle_terabox_link(text.strip())
        send_message(chat_id, response_text, button)
    else:
        send_message(chat_id, "❌ Please send a valid TeraBox link.")

    return '', 200

def handle_terabox_link(link):
    try:
        api_response = requests.post(
            "https://teraboxdownloader.online/api.php",
            headers={"Content-Type": "application/json"},
            json={"url": link}
        )
        data = api_response.json()

        if "direct_link" in data:
            response_text = (
                f"🎬 *{data.get('file_name', 'File')}*\n"
                f"💾 Size: {data.get('size', 'Unknown')}\n"
                f"🖼 [Thumbnail]({data.get('thumb', '')})"
            )
            button = {
                "inline_keyboard": [[
                    {"text": "⬇️ Download Now", "url": data["direct_link"]}
                ]]
            }
            return response_text, button
        else:
            return f"⚠️ Failed to get direct link.\n\nResponse: `{data}`", None
    except Exception as e:
        return f"❌ Error: `{str(e)}`", None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(TELEGRAM_API, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
