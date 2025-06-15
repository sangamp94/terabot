import requests
from flask import Flask, request
import re # Import re for regular expression parsing of HTML

app = Flask(__name__)

# Directly use your bot token
BOT_TOKEN = "8182816847:AAGcetpSXP0gpNgYj8CJAryxnH5_nRYW2gM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_direct_link(tera_url):
    """
    Attempts to retrieve a direct download link from teraboxdownloader.online
    by simulating a form submission using the requests library.

    Args:
        tera_url (str): The original Terabox sharing URL.

    Returns:
        str: The direct download link if found, otherwise None.
    """
    terabox_downloader_url = "https://teraboxdownloader.online/"
    
    # Headers to mimic a web browser request, crucial for avoiding basic bot detection.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://teraboxdownloader.online/", # Acts as if the request came from the downloader site itself.
        "Content-Type": "application/x-www-form-urlencoded", # Standard content type for HTML form submissions.
        "Origin": "https://teraboxdownloader.online/" # Essential for CORS and some server-side checks.
    }

    # The payload (data) for the POST request.
    # It assumes the input field on teraboxdownloader.online is named 'link'.
    payload = {
        "link": tera_url
    }

    try:
        # Send a POST request to the downloader website with the Terabox URL.
        # allow_redirects=True ensures we follow any redirects after submission.
        # timeout=30 sets a maximum waiting time for the response.
        response = requests.post(terabox_downloader_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
        
        # Raise an HTTPError for bad responses (4xx or 5xx status codes).
        response.raise_for_status() 

        # --- HTML Parsing to Find the Download Link ---
        # The response.text contains the HTML content of the page after the submission.
        # We need to extract the direct download link from this HTML.

        # Regex to find an <a> tag that contains a direct download link.
        # It looks for href attributes starting with http/https and ending with common file extensions.
        # It also checks if the link text contains "Download" or "Direct Link" (case-insensitive).
        # re.DOTALL ensures '.' matches newlines as well, useful for multi-line HTML.
        download_link_pattern = r'<a[^>]*href=["\'](https?://[^"\']*\.(?:zip|rar|mp4|avi|mkv|pdf|doc|docx|xlsx|pptx|gz|7z|exe|txt|jpg|png|gif|webp)[^"\']*)["\'][^>]*>(?:.*?Download|.*?Direct Link).*?</a>'
        match = re.search(download_link_pattern, response.text, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1) # Return the captured URL from the href attribute
        else:
            # If the primary pattern doesn't match, sometimes links are embedded in JavaScript variables.
            # This is a speculative pattern to catch a JS variable like `downloadLink = "http://..."`
            js_link_pattern = r'(?:var|const|let)\s+downloadLink\s*=\s*["\'](https?://[^"\']*)["\']'
            js_match = re.search(js_link_pattern, response.text, re.IGNORECASE)
            if js_match:
                return js_match.group(1)

            # If no link is found by either pattern, print a warning for debugging.
            print(f"[⚠️] Could not find a recognizable download link in the response HTML for {tera_url}")
            return None

    except requests.exceptions.RequestException as e:
        # Catch specific request-related errors (e.g., network issues, timeouts, bad HTTP status).
        print(f"[❌] Request Error while processing {tera_url}: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the process.
        print(f"[❌] General Error in get_direct_link for {tera_url}: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    """Simple homepage to confirm the bot is running."""
    return "✅ TeraBox Bot is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """
    Receives incoming updates from Telegram and processes messages.
    This endpoint should be set as the webhook URL for your Telegram bot.
    """
    data = request.get_json()
    
    # Ensure the received data is valid and contains a message.
    if not data or "message" not in data:
        return {"ok": True} # Acknowledge the update even if it's not a message we care about

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "") # Get the text of the message, default to empty string

    # Check if the message is a Terabox link based on common domain names.
    # This acts as a preliminary filter before attempting to process the link.
    is_terabox_link = "terabox.com" in text or "teraboxapp.com" in text

    if text.startswith("/start"):
        # Handle the /start command, usually sent when a user first interacts with the bot.
        send_message(chat_id, "👋 Welcome! Send me a Terabox link to get a direct download link.")
    elif is_terabox_link:
        # Process the Terabox link.
        send_message(chat_id, "⏳ Processing your link, please wait...")
        link = get_direct_link(text) # Call the function to get the direct link
        if link:
            send_message(chat_id, f"✅ Direct Download Link:\n{link}")
        else:
            # Inform the user if the link extraction failed, with possible reasons.
            send_message(chat_id, "❌ Failed to extract the download link. This might be due to an invalid link, the downloader website changing its structure, or bot detection. Please try again later or with a different link.")
    else:
        # For any other message, prompt the user for a valid link.
        send_message(chat_id, "⚠️ Please send a valid Terabox sharing link.")

    return {"ok": True} # Important to return success to Telegram

def send_message(chat_id, text):
    """
    Sends a message to a specified chat ID via the Telegram Bot API.

    Args:
        chat_id (int): The ID of the Telegram chat to send the message to.
        text (str): The text content of the message.
    """
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True # Prevents Telegram from generating a preview for URLs in the message.
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[❌] Failed to send message to chat {chat_id}: {e}")

if __name__ == "__main__":
    # This runs the Flask development server.
    # For production deployment, you would typically use a WSGI server like Gunicorn or uWSGI.
    app.run(host="0.0.0.0", port=5000)
