import requests
import pandas as pd
import ta
import time
import os

TOKEN = os.getenv("8696322142:AAFGjb94MNzYsQkKVHdNLcdkYfmbjLUlIF8")
CHAT_ID = os.getenv("264209707")
send_telegram("BOT OK")
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def load_coins():
    with open("coins.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

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

sent = {}

def check(df, symbol, tf):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()

    low1 = df["low"].iloc[-10:-5].min()
    low2 = df["low"].iloc[-5:].min()

    rsi1 = df[df["low"] == low1]["rsi"].values[0]
    rsi2 = df[df["low"] == low2]["rsi"].values[0]

    if low2 < low1 and rsi2 > rsi1 and rsi2 < 35:
        key = f"{symbol}_{tf}"

        if key not in sent or time.time() - sent[key] > 1800:
            price = df["close"].iloc[-1]

            msg = f"🟢 {symbol} | {tf}\nBullish Divergence\nPrice: {price}"
            send_telegram(msg)

            sent[key] = time.time()

while True:
    coins = load_coins()

    for c in coins:
        try:
            check(get_data(c, "15m"), c, "M15")
            check(get_data(c, "5m"), c, "M5")
            time.sleep(0.5)
        except:
            pass

    time.sleep(60)
