import os
import requests
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"[✅] Message sent to {chat_id}: {text}")
        print(f"[ℹ️] Telegram API response: {resp.text}")
    except Exception as e:
        print(f"[❌] Failed to send message to {chat_id}: {e}")

def get_direct_link(tera_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # If ChromeDriver is not in PATH, specify executable_path
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://teraboxdownloader.online/")

        # Wait for input box and enter the Terabox URL
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="link"]'))
        )
        input_field.clear()
        input_field.send_keys(tera_url)

        # Find and click the Download button
        download_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        download_btn.click()

        # Wait for the "Download Video" button (a link with class 'download-btn') to appear
        download_video_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.download-btn'))
        )

        href = download_video_link.get_attribute("href")
        return href

    except Exception as e:
        print(f"[❌] Selenium error: {e}")
        return None

    finally:
        driver.quit()

@app.route("/", methods=["GET"])
def home():
    return "✅ TeraBox Bot is running."

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

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = f"https://{request.host}/{BOT_TOKEN}"
    res = requests.get(f"{TELEGRAM_API}/setWebhook?url={webhook_url}")
    return jsonify(res.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
