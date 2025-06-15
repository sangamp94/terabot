import os
import re
import time
import requests
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Function to send messages
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"[✅] Message sent to {chat_id}: {text}")
    except Exception as e:
        print(f"[❌] Failed to send message to {chat_id}: {e}")

# Function to get direct download link using Selenium
def get_direct_link(tera_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://teraboxdownloader.online/")
        print("[🌐] Opened teraboxdownloader.online")

        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "link"))
        )
        input_box.send_keys(tera_url)

        download_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Download')]")
        download_button.click()
        print("[👆] Clicked download button")

        # Wait for final download link button to appear
        final_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Download Video')]"))
        )
        href = final_link.get_attribute("href")
        print(f"[✅] Found download link: {href}")
        driver.quit()
        return href
    except Exception as e:
        print(f"[❌] Error in Selenium: {e}")
        return None

# Home route
@app.route("/", methods=["GET"])
def home():
    return "✅ TeraBox Bot is running."

# Webhook handler
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print(f"[📩] Incoming update: {data}")

    if not data or "message" not in data:
        return jsonify({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    try:
        if text.startswith("/start"):
            send_message(chat_id, "👋 Welcome! Send me a Terabox link to get a direct download link.")
        elif "terabox.com" in text or "teraboxapp.com" in text:
            send_message(chat_id, "⏳ Processing your link, please wait...")
            direct_link = get_direct_link(text)
            if direct_link:
                send_message(chat_id, f"✅ Direct Download Link:\n{direct_link}")
            else:
                send_message(chat_id, "❌ Failed to extract the download link. Try another link or try later.")
        else:
            send_message(chat_id, "⚠️ Please send a valid Terabox sharing link.")
    except Exception as e:
        print(f"[❌] Error processing message: {e}")

    return jsonify({"ok": True})

# Manual webhook setup route (optional)
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{request.host}/{BOT_TOKEN}"
    res = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    return jsonify(res.json())

# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
