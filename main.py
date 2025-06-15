import os
import time
import requests
from flask import Flask, request
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

# Set your bot token here or use environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
        return link_element.get_attribute("href")
    except Exception as e:
        print(f"[❌] Error: {e}")
        return None
    finally:
        driver.quit()

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_message(chat_id, "👋 Send me a TeraBox link to get a direct download link.")
        elif "terabox" in text:
            send_message(chat_id, "⏳ Processing your link...")
            link = get_direct_link(text)
            if link:
                send_message(chat_id, f"✅ Direct Download Link:\n{link}")
            else:
                send_message(chat_id, "❌ Failed to extract the download link. Please try again.")
        else:
            send_message(chat_id, "⚠️ Please send a valid TeraBox sharing link.")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
