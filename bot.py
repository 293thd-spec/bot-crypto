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
def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# =========================
# GET BTC M5 FROM OKX
# =========================
def get_btc_closes():
    url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": "BTC-USDT",
        "bar": "5m",
        "limit": "100"
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "data" not in data:
        print("API error:", data)
        return None

    candles = data["data"]

    # OKX trả ngược → đảo lại
    candles = candles[::-1]

    closes = [float(c[4]) for c in candles]
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
    return ema12 - ema26


# =========================
# SWING DETECTION
# =========================
def swings(arr):
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

    p_l1, p_l2, p_h1, p_h2 = swings(price)
    m_l1, m_l2, m_h1, m_h2 = swings(macd_line)

    bullish = (p_l2 < p_l1) and (m_l2 > m_l1)
    bearish = (p_h2 > p_h1) and (m_h2 < m_h1)

    if bullish:
        return "BULLISH"
    if bearish:
        return "BEARISH"

    return None


# =========================
# MAIN LOOP
# =========================
def run():
    send_telegram("🚀 BTC MACD M5 BOT STARTED (OKX VERSION)")

    while True:
        price = get_btc_closes()

        if price is None:
            time.sleep(60)
            continue

        macd_line = macd(price)

        signal = check_div(price, macd_line)

        if signal:
            send_telegram(
                f"📊 BTCUSDT\nTF: M5\nMACD Divergence: {signal}"
            )

        print("Checked BTC")

        time.sleep(300)  # 5 phút = M5 chuẩn


# =========================
# START
# =========================
run()
