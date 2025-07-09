import sys import subprocess import requests import re import os from datetime import datetime from urllib.parse import urlparse from flask import Flask, request, jsonify import telebot import threading

--- Configuration ---

M3U_URL = "https://raw.githubusercontent.com/alex4528/m3u/main/jstar.m3u" PIXELDRAIN_API_KEY = "60022898-39c5-4a3c-a3c4-bbbccbde20ad" BOT_TOKEN = "7386617987:AAGounvetKHtmtqCxEbY_Idc5M2IfUNSst4" PORT = 5000

app = Flask(name) bot = telebot.TeleBot(BOT_TOKEN)

def fetch_channels_from_m3u(): r = requests.get(M3U_URL) r.raise_for_status() lines = r.text.splitlines()

channels = {}
i = 0
while i < len(lines):
    if lines[i].startswith("#EXTINF"):
        channel_id = None
        name = "Unknown"
        license_key = ""
        user_agent = ""
        cookie = ""
        url = ""

        name_match = re.search(r",(.+)", lines[i])
        if name_match:
            name = name_match.group(1).strip()

        id_match = re.search(r'tvg-id="(\d+)"', lines[i])
        if id_match:
            channel_id = id_match.group(1)

        j = i + 1
        while j < len(lines) and lines[j].startswith("#"):
            if "license_key=" in lines[j]:
                license_key = lines[j].split("license_key=")[-1].strip()
            elif "user-agent=" in lines[j].lower():
                ua = re.search(r"user-agent=([^\"\n]+)", lines[j].lower())
                if ua:
                    user_agent = ua.group(1)
            elif "EXTHTTP" in lines[j]:
                cookie_match = re.search(r'"cookie":"([^"]+)"', lines[j])
                if cookie_match:
                    cookie = cookie_match.group(1)
            j += 1

        if j < len(lines):
            url = lines[j].strip()

        if channel_id and url and license_key:
            channels[channel_id] = {
                "name": name,
                "url": url,
                "license_key": license_key,
                "headers": {
                    "User-Agent": user_agent or "plaYtv/7.1.3",
                    "cookie": cookie
                }
            }
    i += 1
return channels

def upload_to_pixeldrain(filepath): print(f"[+] Uploading {filepath} to Pixeldrain...") with open(filepath, 'rb') as f: response = requests.post( "https://pixeldrain.com/api/file", headers={"Authorization": f"Bearer {PIXELDRAIN_API_KEY}"}, files={"file": (os.path.basename(filepath), f)} ) if response.status_code == 200: file_id = response.json().get("id") link = f"https://pixeldrain.com/u/{file_id}" print(f"[✓] Uploaded: {link}") return link else: print(f"[!] Upload failed: {response.text}") return None

def run_grab(channel_id, date_str, time_str, duration, output_ext, channels): channel = channels.get(channel_id) if not channel: print(f"[!] Channel ID {channel_id} not found.") return

dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
timestamp = dt.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{channel['name'].replace(' ', '_')}_{timestamp}{output_ext}"

parsed = urlparse(channel["url"])
port = parsed.port or (443 if parsed.scheme == 'https' else 80)
print(f"[i] Using port: {port}")

cmd = [
    "yt-dlp",
    "--allow-unplayable-formats",
    "--fixup", "never",
    "--user-agent", channel['headers']['User-Agent'],
    "--add-header", f"cookie: {channel['headers']['cookie']}",
    "--decryption-key", channel["license_key"],
    "--download-sections", f"*00:00:00-{int(duration)}",
    "-o", filename,
    channel["url"]
]

print(f"[+] Ripping {channel['name']} for {duration}s to {filename}")
subprocess.run(cmd)

if os.path.exists(filename):
    link = upload_to_pixeldrain(filename)
    os.remove(filename)
    print(f"[✓] Deleted local file: {filename}")
    if link:
        print(f"[🔗] Download Link: {link}")
    return link
else:
    print(f"[!] File not created: {filename}")
    return None

--- Flask API ---

@app.route("/grab") def grab_endpoint(): args = request.args channel_id = args.get("channel_id") date = args.get("date") time = args.get("time") duration = args.get("duration") ext = args.get("ext", ".mp4")

if not all([channel_id, date, time, duration]):
    return jsonify({"error": "Missing required parameters"}), 400

try:
    channels = fetch_channels_from_m3u()
    link = run_grab(channel_id, date, time, duration, ext, channels)
    if link:
        return jsonify({"status": "Success", "link": link})
    else:
        return jsonify({"status": "Failed to upload"}), 500
except Exception as e:
    return jsonify({"error": str(e)}), 500

--- Telegram Bot ---

@bot.message_handler(commands=['start']) def welcome(msg): bot.reply_to(msg, "👋 Welcome to the Channel Ripper Bot!\nSend: /grab <id> <date> <time> <duration> <ext>\nExample: /grab 1089 2025-07-08 23:00:00 3600 .mp4", parse_mode='Markdown')

@bot.message_handler(commands=['grab']) def grab_command(msg): try: parts = msg.text.strip().split() if len(parts) != 6: bot.reply_to(msg, "❌ Invalid format!\nUse: /grab <id> <date> <time> <duration> <.ext>", parse_mode='Markdown') return

_, channel_id, date, time_str, duration, ext = parts
    bot.reply_to(msg, f"⏳ Starting rip for channel `{channel_id}`...", parse_mode='Markdown')

    def process():
        try:
            channels = fetch_channels_from_m3u()
            link = run_grab(channel_id, date, time_str, duration, ext, channels)
            if link:
                bot.send_message(msg.chat.id, f"✅ Done!\n🔗 [Download Link]({link})", parse_mode='Markdown')
            else:
                bot.send_message(msg.chat.id, "❌ Rip failed or no file uploaded.")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ Error: {str(e)}")

    threading.Thread(target=process).start()

except Exception as e:
    bot.reply_to(msg, f"⚠️ Unexpected Error: {e}")

--- CLI or App Runner ---

if name == "main": if len(sys.argv) == 1: threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start() bot.infinity_polling() elif len(sys.argv) == 6: channels = fetch_channels_from_m3u() channel_id, date_str, time_str, duration_str, output_ext = sys.argv[1:] run_grab(channel_id, date_str, time_str, duration_str, output_ext, channels) else: print("Usage:\n - Web: run with no args\n - CLI: python grab.py <channel_id> <date> <time> <duration_sec> <output_ext>")
