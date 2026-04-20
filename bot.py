import os
import time
import requests
import numpy as np

# =========================
# TELEGRAM CONFIG
# =========================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# TELEGRAM SEND
# =========================
def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# LOAD COINS
# =========================
def load_coins():
    try:
        with open("coins.txt", "r") as f:
            return [c.strip().upper() for c in f if c.strip()]
    except:
        return []


# =========================
# GET BINANCE M5 DATA
# =========================
def get_m5_data(symbol):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 100
    }

    r = requests.get(url, params=params)
    data = r.json()

    closes = [float(c[4]) for c in data]  # close price
    return np.array(closes)


# =========================
# EMA / MACD
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
# SWING DETECTION
# =========================
def get_swings(data):
    last = data[-20:]

    low1 = np.min(last[:10])
    low2 = np.min(last[10:])

    high1 = np.max(last[:10])
    high2 = np.max(last[10:])

    return low1, low2, high1, high2


# =========================
# DIVERGENCE CHECK
# =========================
def check_div(price, macd_line):
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
# MAIN LOOP
# =========================
def run():
    send_telegram("🚀 MACD M5 BOT (BINANCE) STARTED")

    while True:
        coins = load_coins()

        for coin in coins:
            try:
                print("Scanning:", coin)

                price = get_m5_data(coin)
                macd_line = macd(price)

                result = check_div(price, macd_line)

                if result:
                    send_telegram(
                        f"📊 {coin}\nTF: M5\nMACD Divergence: {result}"
                    )

                time.sleep(1)

            except Exception as e:
                print("Error:", coin, e)

        print("Cycle done...")
        time.sleep(60)


run()
