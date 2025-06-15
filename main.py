from flask import Flask, request
from telegram import Bot
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"
bot = Bot(BOT_TOKEN)

@app.route('/', methods=["POST"])
def webhook():
    update = request.get_json()
    chat_id = update["message"]["chat"]["id"]
    bot.send_message(chat_id=chat_id, text="✅ Bot is working on Python 3.12!")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
