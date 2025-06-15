import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me your TeraBox link and I'll get the direct download link.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tera_link = update.message.text
    await update.message.reply_text("⏳ Processing your link...")

    try:
        download_link = get_direct_link(tera_link)
        if download_link:
            await update.message.reply_text(f"✅ Direct Download Link:\n{download_link}")
        else:
            await update.message.reply_text("❌ Failed to extract the download link. Try again later.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

def get_direct_link(tera_url):
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://teraboxdownloader.online/")
        time.sleep(2)

        input_box = driver.find_element(By.ID, "link")
        input_box.send_keys(tera_url)
        input_box.send_keys(Keys.RETURN)

        time.sleep(6)

        link_element = driver.find_element(By.XPATH, '//a[contains(text(), "Download")]')
        download_link = link_element.get_attribute("href")
        return download_link

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    asyncio.run(app.run_polling())
