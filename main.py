# main.py
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.sync_api import sync_playwright

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"  # Replace with your real Telegram bot token

def get_direct_link(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        try:
            # Wait for a direct download button with URL containing "https://d"
            page.wait_for_selector('a[href*="https://d"].download-button', timeout=20000)
            link = page.get_attribute('a[href*="https://d"]', 'href')
        except:
            browser.close()
            raise Exception("❌ Direct download link not found. The file may be private or expired.")

        browser.close()
        if not link:
            raise Exception("❌ Could not extract download link.")
        return link

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "terabox.com" not in url and "teraboxapp.com" not in url:
        await update.message.reply_text("❌ Please send a valid TeraBox link.")
        return

    await update.message.reply_text("🔍 Fetching direct download link...")
    try:
        direct_link = get_direct_link(url)
        await update.message.reply_text(f"✅ Direct Download Link:\n{direct_link}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 Bot is running...")
    app.run_polling()
