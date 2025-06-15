from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Replace this with your actual BotFather token
BOT_TOKEN = "7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the TeraBox Link Helper Bot!\n\n"
        "📥 Just send me a TeraBox link and I’ll guide you on how to open/download it safely."
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Help Guide*\n\n"
        "Paste a TeraBox link, and I’ll help you open or download it.\n\n"
        "*Examples:*\n"
        "`https://terabox.com/s/...`\n"
        "`https://www.1024tera.com/file/...`",
        parse_mode="Markdown"
    )

# Handle plain text messages (potential links)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()

    if "terabox.com" in message or "1024tera.com" in message:
        await update.message.reply_text(
            f"✅ *Detected TeraBox Link:*\n{message}\n\n"
            "📌 Please open the link in your browser.\n"
            "🖥️ For best results, use a desktop browser and log in to your TeraBox account.\n\n"
            "⚠️ _This bot does not automatically download or process files for safety._",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ That doesn’t look like a valid TeraBox link.")

# Build and run the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
