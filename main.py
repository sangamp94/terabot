from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from terabox import get_direct_link

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"  # Replace with your real bot token

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "terabox.com" not in url:
        await update.message.reply_text("❌ Please send a valid TeraBox URL.")
        return

    await update.message.reply_text("🔍 Fetching direct link...")
    try:
        direct_link = get_direct_link(url)
        await update.message.reply_text(f"✅ Direct Download Link:\n{direct_link}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🤖 Bot is running...")
    app.run_polling()
