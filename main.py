import os
import time
import requests
import pandas as pd
import datetime

NEO_TOKEN = os.getenv("NEO_API_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_price(symbol):
    import random
    return random.randint(22000, 48000)

def calculate_signal(prices):
    df = pd.DataFrame(prices, columns=["close"])
    df["ema"] = df["close"].ewm(span=44).mean()

    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]

    if latest["close"] > latest["ema"] and latest["rsi"] > 60:
        return "CE", latest
    elif latest["close"] < latest["ema"] and latest["rsi"] < 40:
        return "PE", latest
    else:
        return None, latest

def market_open():
    now = datetime.datetime.now()
    start = now.replace(hour=9, minute=30, second=0)
    end = now.replace(hour=15, minute=10, second=0)
    return start <= now <= end

last_signal_time = {"NIFTY": None, "BANKNIFTY": None}

def run_bot():
    nifty_prices = []
    banknifty_prices = []

    while True:
        try:
            if not market_open():
                print("Market closed...")
                time.sleep(60)
                continue

            nifty = get_price("NIFTY")
            banknifty = get_price("BANKNIFTY")

            nifty_prices.append(nifty)
            banknifty_prices.append(banknifty)

            if len(nifty_prices) > 50:
                nifty_prices.pop(0)
                banknifty_prices.pop(0)

            signal, data = calculate_signal(nifty_prices)
            if signal:
                now = time.time()
                if not last_signal_time["NIFTY"] or now - last_signal_time["NIFTY"] > 900:
                    strike = round(data["close"] / 50) * 50
                    msg = f"🚨 NIFTY {signal}\nATM: {strike}\nRSI: {data['rsi']:.1f}"
                    send_telegram(msg)
                    last_signal_time["NIFTY"] = now

            signal, data = calculate_signal(banknifty_prices)
            if signal:
                now = time.time()
                if not last_signal_time["BANKNIFTY"] or now - last_signal_time["BANKNIFTY"] > 900:
                    strike = round(data["close"] / 100) * 100
                    msg = f"🚨 BANKNIFTY {signal}\nATM: {strike}\nRSI: {data['rsi']:.1f}"
                    send_telegram(msg)
                    last_signal_time["BANKNIFTY"] = now

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

if __name__ == "__main__":
    send_telegram("🚀 Bot Started")
    run_bot()
