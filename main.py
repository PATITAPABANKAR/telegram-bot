import os
import time
import datetime
import threading
import requests
import pandas as pd
from flask import Flask

# ===== KOTAK NEO API =====
from neo_api_client import NeoAPI

app = Flask(__name__)

# ===== ENV VARIABLES =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

NEO_API_KEY = os.getenv("NEO_API_KEY")
NEO_ACCESS_TOKEN = os.getenv("NEO_ACCESS_TOKEN")

# ===== INIT NEO =====
client = NeoAPI(api_key=NEO_API_KEY)
client.set_access_token(NEO_ACCESS_TOKEN)

# ===== TELEGRAM =====
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

# ===== FETCH DATA FROM NEO =====
def get_data(instrument_token):
    try:
        data = client.get_ohlc(
            exchange="NSE",
            tradingsymbol=instrument_token,
            interval="5minute"
        )

        df = pd.DataFrame(data["data"])
        df = df.rename(columns={
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "close_price": "close",
            "volume": "volume"
        })

        df = df.astype(float)
        return df

    except Exception as e:
        print("Neo Data Error:", e)
        return None

# ===== INDICATORS =====
def calculate(df):
    df["wma44"] = df["close"].rolling(44).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df["vol_avg"] = df["volume"].rolling(20).mean()
    return df

# ===== SIGNAL =====
def generate_signal(name, token):
    df = get_data(token)
    if df is None or len(df) < 50:
        return None

    df = calculate(df)
    last = df.iloc[-1]

    if last["close"] > last["wma44"] and last["rsi"] > 55 and last["volume"] > last["vol_avg"]:
        return f"BUY {name}"

    elif last["close"] < last["wma44"] and last["rsi"] < 45 and last["volume"] > last["vol_avg"]:
        return f"SELL {name}"

    return None

# ===== TIME =====
def market_time():
    now = datetime.datetime.now().time()
    return datetime.time(9,20) <= now <= datetime.time(15,15)

# ===== MAIN BOT =====
def run_bot():
    print("Bot Started")

    # 🔴 IMPORTANT: PUT CORRECT TOKENS
    instruments = {
        "NIFTY": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK"
    }

    while True:
        try:
            if market_time():
                for name, token in instruments.items():
                    sig = generate_signal(name, token)
                    if sig:
                        print(sig)
                        send_telegram(sig)

                time.sleep(300)
            else:
                time.sleep(60)

        except Exception as e:
            print("Main Error:", e)
            time.sleep(60)

# ===== FLASK =====
@app.route("/")
def home():
    return "Bot Running"

# ===== START =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=port)
