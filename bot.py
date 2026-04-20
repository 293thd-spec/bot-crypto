import requests
import os
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ======================
# PHẢI CÓ HÀM NÀY TRƯỚC
# ======================
def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ======================
# TEST
# ======================
send_telegram("🚀 BOT OK")

# ======================
# LOOP (giữ bot sống)
# ======================
while True:
    time.sleep(60)
