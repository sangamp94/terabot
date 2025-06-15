from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.sync_api import sync_playwright
import threading

BOT_TOKEN = "PLACEHOLDER"  # Replace with your real Telegram bot token

app = Flask(__name__)

@app.route("/")
def home():
    return "TeraBox Downloader Bot is running!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("https://teraboxapp.com/s/"):
        await update.message.reply_text("Please send a valid TeraBox share link.")
        return

    await update.message.reply_text("Processing your link...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector('a[href*="https://d"].download-button', timeout=20000)
            download_button = page.query_selector('a[href*="https://d"].download-button')
            direct_link = download_button.get_attribute("href")
            browser.close()

        if direct_link:
            await update.message.reply_text(f"Direct download link: {direct_link}")
        else:
            await update.message.reply_text("Failed to extract the direct download link.")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def start_telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

# Start Telegram bot in separate thread
threading.Thread(target=start_telegram_bot).start()
