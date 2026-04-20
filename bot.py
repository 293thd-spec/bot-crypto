import requests
import time
import os

# =========================
# CONFIG (Railway Variables)
# =========================
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

# =========================
# TELEGRAM FUNCTION
# =========================
def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)

# =========================
# START TEST
# =========================
send_telegram("🚀 BOT STARTED")

print("Bot is running...")

# =========================
# MAIN LOOP
# =========================
while True:
    try:
        # test heartbeat mỗi 5 phút (có thể tắt sau)
        send_telegram("⏳ BOT STILL RUNNING")
        time.sleep(300)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
