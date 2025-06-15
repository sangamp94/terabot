from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"  # Replace this with your actual bot token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me a TeraBox link and I’ll help you get started.\n\n"
        "📌 Just paste the link and I’ll reply with instructions!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Help Guide*\n\n"
        "Just paste a TeraBox link, and I’ll help you open it properly.\n"
        "No need to use commands — just send the link!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    if "terabox.com" in user_input or "1024tera.com" in user_input:
        await update.message.reply_text(
            f"🔗 *Your Link:*\n{user_input}\n\n"
            "➡️ Open the link in your browser.\n"
            "📥 Log in to TeraBox (if needed) and download the file.\n\n"
            "_Tip: Use desktop browser for best results._",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ That doesn’t look like a valid TeraBox link. Please try again.")

# Build and run the app
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
