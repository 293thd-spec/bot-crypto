import os
import time
import requests
import numpy as np

# =========================
# CONFIG TELEGRAM
# =========================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# =========================
# SEND TELEGRAM
# =========================
def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram error:", e)


# =========================
# LOAD COINS
# =========================
def load_coins():
    try:
        with open("coins.txt", "r") as f:
            return [x.strip().upper().replace("-", "") for x in f if x.strip()]
    except:
        return []


# =========================
# GET BINANCE M5 DATA
# =========================
def get_closes(symbol):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 100
    }

    r = requests.get(url, params=params)
    data = r.json()

    # 🔥 FIX ERROR: check valid data
    if not isinstance(data, list):
        print("API error:", symbol, data)
        return None

    closes = [float(c[4]) for c in data]  # CLOSE PRICE
    return np.array(closes)


# =========================
# EMA + MACD
# =========================
def ema(data, period):
    alpha = 2 / (period + 1)
    out = []

    for i, v in enumerate(data):
        if i == 0:
            out.append(v)
        else:
            out.append(alpha * v + (1 - alpha) * out[-1])

    return np.array(out)


def macd(data):
    ema12 = ema(data, 12)
    ema26 = ema(data, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    return macd_line


# =========================
# SWING DETECTION (SIMPLE BUT SAFE)
# =========================
def get_swings(arr):
    last = arr[-20:]

    low1 = np.min(last[:10])
    low2 = np.min(last[10:])

    high1 = np.max(last[:10])
    high2 = np.max(last[10:])

    return low1, low2, high1, high2


# =========================
# DIVERGENCE CHECK
# =========================
def check_div(price, macd_line):
    if price is None or len(price) < 50:
        return None

    p_low1, p_low2, p_high1, p_high2 = get_swings(price)
    m_low1, m_low2, m_high1, m_high2 = get_swings(macd_line)

    bullish = (p_low2 < p_low1) and (m_low2 > m_low1)
    bearish = (p_high2 > p_high1) and (m_high2 < m_high1)

    if bullish:
        return "BULLISH"
    if bearish:
        return "BEARISH"

    return None


# =========================
# MAIN BOT
# =========================
def run():
    send_telegram("🚀 MACD M5 BOT STARTED (FIXED VERSION)")

    while True:
        coins = load_coins()

        if not coins:
            print("No coins")
            time.sleep(30)
            continue

        for coin in coins:
            print("Scanning:", coin)

            price = get_closes(coin)

            if price is None:
                continue

            macd_line = macd(price)

            signal = check_div(price, macd_line)

            if signal:
                send_telegram(
                    f"📊 {coin}\nTF: M5\nMACD Divergence: {signal}"
                )

            time.sleep(1)

        print("Cycle done")
        time.sleep(300)  # 5 phút chuẩn M5


# =========================
# START
# =========================
run()
