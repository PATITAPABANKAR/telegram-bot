import pandas as pd
import requests
import schedule
import time
import os
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from neo_api_client import NeoAPI

# -------- ENV VARIABLES --------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# -------- TELEGRAM FUNCTION --------
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram Error:", e)

# -------- NEO API SETUP --------
client = NeoAPI(api_key=API_KEY)
client.set_access_token(ACCESS_TOKEN)

# -------- FETCH DATA --------
def get_data():
    try:
        data = client.get_historical_data(
            instrument_token="26009",   # BANKNIFTY (change if needed)
            interval="5minute",
            from_date=datetime.now().strftime("%Y-%m-%d") + " 09:15:00",
            to_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        df = pd.DataFrame(data)

        if df.empty:
            return None

        df = df[["open", "high", "low", "close", "volume"]]
        df = df.astype(float)

        return df

    except Exception as e:
        print("Neo API Error:", e)
        return None

# -------- STRATEGY --------
def check_signal():
    df = get_data()

    if df is None or len(df) < 50:
        print("Not enough data")
        return

    # Indicators
    df["wma44"] = df["close"].rolling(44).mean()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14)
    df["atr"] = atr.average_true_range()

    df["vol_avg"] = df["volume"].rolling(20).mean()

    latest = df.iloc[-1]

    buy = (
        latest["close"] > latest["wma44"] and
        latest["rsi"] > 55 and
        latest["volume"] > 1.5 * latest["vol_avg"]
    )

    sell = (
        latest["close"] < latest["wma44"] and
        latest["rsi"] < 45 and
        latest["volume"] > 1.5 * latest["vol_avg"]
    )

    if buy:
        msg = f"📈 BUY BANKNIFTY\nPrice: {latest['close']}\nRSI: {latest['rsi']:.2f}"
        print(msg)
        send_telegram(msg)

    elif sell:
        msg = f"📉 SELL BANKNIFTY\nPrice: {latest['close']}\nRSI: {latest['rsi']:.2f}"
        print(msg)
        send_telegram(msg)

    else:
        print("No signal")

# -------- TIME FILTER --------
def run_bot():
    now = datetime.now().time()

    start = datetime.strptime("09:20", "%H:%M").time()
    end = datetime.strptime("15:30", "%H:%M").time()

    if start <= now <= end:
        print("Running strategy...")
        check_signal()
    else:
        print("Outside trading hours")

# -------- SCHEDULER --------
schedule.every(5).minutes.do(run_bot)

print("Bot Started...")

# -------- LOOP --------
while True:
    schedule.run_pending()
    time.sleep(1)
