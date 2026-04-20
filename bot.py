import requests
import os
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# PHẢI CÓ HÀM NÀY
# =========================
def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# TEST (đặt SAU hàm)
# =========================
send_telegram("🚀 BOT OK")

# =========================
# GIỮ BOT CHẠY
# =========================
while True:
    time.sleep(60)
