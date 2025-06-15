# Flask TeraBox Downloader Bot

This bot accepts TeraBox URLs via Telegram and replies with a direct download link using Flask.

## ✅ Features
- Accepts TeraBox file links
- Replies via Telegram with a simulated direct link
- Runs using Flask + gunicorn
- Ready for deployment on Render

## 🛠️ Setup
1. Replace `PLACEHOLDER` in `main.py` with your Telegram bot token
2. Set up webhook with:
   ```
   curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-render-url/
   ```

## 🚀 Deploy to Render
- Upload files to GitHub or ZIP
- Create a Render **Web Service**
- Add a `Procfile` and select Python environment
