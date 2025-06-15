from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Replace with your actual bot token
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Handle incoming webhook requests from Telegram
@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    chat_id = data['message']['chat']['id']
    text = data['message'].get('text', '')

    if 'http' in text and "terabox" in text:
        response_message = handle_terabox_link(text)
    else:
        response_message = "❌ Please send a valid TeraBox link."

    send_message(chat_id, response_message)
    return '', 200

# Call the teraboxdownloader.online API with corrected JSON
def handle_terabox_link(link):
    try:
        api_response = requests.post(
            "https://teraboxdownloader.online/api.php",
            headers={"Content-Type": "application/json"},
            json={"url": link}  # ✅ fixed key
        )

        data = api_response.json()

        if "direct_link" in data:
            return (
                f"🎬 *{data.get('file_name', 'File')}*\n"
                f"💾 Size: {data.get('size', 'Unknown')}\n\n"
                f"🔗 [Download Now]({data['direct_link']})"
            )
        else:
            return "⚠️ Failed to retrieve direct link.\nResponse: " + str(data)

    except Exception as e:
        return f"❌ Error fetching link: {e}"

# Send message to Telegram
def send_message(chat_id, text):
    requests.post(TELEGRAM_API, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
