import requests
import pandas as pd
import ta
import time
import os

# ======================
# CONFIG
# ======================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ======================
# TELEGRAM FUNCTION
# ======================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ======================
# LOAD COINS
# ======================
def load_coins():
    with open("coins.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# ======================
# GET DATA FROM OKX
# ======================
def get_data(symbol, tf="15m"):
    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={tf}&limit=100"
    data = requests.get(url).json()["data"]

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","vol",
        "volCcy","volCcyQuote","confirm"
    ])

    df = df.astype(float)
    df = df.sort_values("time")
    return df

# ======================
# DETECT DIVERGENCE
# ======================
sent = {}

def check_divergence(df, symbol, tf):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()

    low1 = df["low"].iloc[-10:-5].min()
    low2 = df["low"].iloc[-5:].min()

    try:
        rsi1 = df[df["low"] == low1]["rsi"].values[0]
        rsi2 = df[df["low"] == low2]["rsi"].values[0]
    except:
        return

    if low2 < low1 and rsi2 > rsi1 and rsi2 < 35:
        key = f"{symbol}_{tf}"

        if key not in sent or time.time() - sent[key] > 1800:
            price = df["close"].iloc[-1]

            msg = f"""
🟢 {symbol}
TF: {tf}
Bullish Divergence
Price: {price}
"""
            send_telegram(msg)

            sent[key] = time.time()

# ======================
# MAIN LOOP
# ======================
send_telegram("BOT STARTED")

while True:
    coins = load_coins()

    for c in coins:
        try:
            df15 = get_data(c, "15m")
            check_divergence(df15, c, "M15")

            df5 = get_data(c, "5m")
            check_divergence(df5, c, "M5")

            time.sleep(0.5)

        except Exception as e:
            print("Error:", c, e)

    time.sleep(60)
