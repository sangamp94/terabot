from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send me a TeraBox link and I’ll help you get started."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if "terabox.com" in user_input:
        await update.message.reply_text(
            f"To download from TeraBox, open this in your browser: {user_input}\n\n"
            "For best results, open it on a desktop and use your TeraBox account."
        )
    else:
        await update.message.reply_text("That doesn’t look like a valid TeraBox link.")

app = ApplicationBuilder().token("7978862914:AAE9YgkLOTMsynLVquZEESWbvYglJbfNWHc").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", start))
app.add_handler(CommandHandler("download", handle_link))  # Optional command
app.add_handler(CommandHandler(None, handle_link))        # Text messages

app.run_polling()

