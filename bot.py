import os
import time
import requests
import numpy as np

# =========================
# TELEGRAM
# =========================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# GIÁ BTC HIỆN TẠI
# =========================
def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url).json()
    return float(r["price"])


# =========================
# LẤY CANDLE
# =========================
def get_klines(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": 100}

    r = requests.get(url, params=params).json()

    if not isinstance(r, list):
        return None

    return np.array([float(x[4]) for x in r])


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
    return macd_line, signal


# =========================
# TREND M15
# =========================
def get_m15_trend(symbol):
    price = get_klines(symbol, "15m")

    if price is None:
        return None

    macd_line, signal = macd(price)

    return "TĂNG" if macd_line[-1] > signal[-1] else "GIẢM"


# =========================
# SWING
# =========================
def swings(data):
    return (
        np.min(data[-20:-10]),
        np.min(data[-10:]),
        np.max(data[-20:-10]),
        np.max(data[-10:])
    )


# =========================
# DIVERGENCE
# =========================
def check_div(price, macd_line):
    p1, p2, h1, h2 = swings(price)
    m1, m2, mh1, mh2 = swings(macd_line)

    bullish = (p2 < p1) and (m2 > m1)
    bearish = (p2 > p1) and (m2 < m1)

    if bullish:
        return "TĂNG"
    if bearish:
        return "GIẢM"
    return None


# =========================
# SCAN BTC
# =========================
def scan():
    symbol = "BTCUSDT"

    price_now = get_btc_price()
    trend_m15 = get_m15_trend(symbol)

    timeframes = {
        "M1": "1m",
        "M3": "3m",
        "M5": "5m"
    }

    result_list = []

    for tf_name, tf in timeframes.items():

        price = get_klines(symbol, tf)
        if price is None:
            continue

        macd_line, signal = macd(price)
        div = check_div(price, macd_line)

        if div:
            # lọc theo trend M15
            if trend_m15 == div:
                result_list.append(f"{tf_name}: {div}")

    if result_list:
        msg = (
            f"📊 BTCUSDT\n"
            f"💰 Giá hiện tại: {price_now:.2f}$\n"
            f"📈 Trend M15: {trend_m15}\n\n"
            + "\n".join(result_list)
        )

        send_telegram(msg)


# =========================
# RUN LOOP
# =========================
def run():
    send_telegram("🚀 BOT BTC M1/M3/M5 + M15 STARTED")

    while True:
        try:
            scan()
        except Exception as e:
            print("Error:", e)

        time.sleep(60)


run()
