import os
import time
import datetime
import requests

# ========================
# 🔐 ENV VARIABLES
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ========================
# ⏰ MARKET TIME (IST)
# ========================
START_TIME = datetime.time(9, 20)
END_TIME = datetime.time(15, 15)

# ========================
# 📩 TELEGRAM FUNCTION
# ========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

# ========================
# 📊 DATA FUNCTION
# (TEMP MOCK — replace later)
# ========================
def get_market_data():
    import random
    return random.randint(22000, 22200)

# ========================
# 🧠 SIGNAL LOGIC
# ========================
def generate_signal(price):
    if price > 22100:
        return "BUY CE 📈"
    elif price < 22050:
        return "BUY PE 📉"
    return None

# ========================
# 🕔 TIME CHECK (IST FIX)
# ========================
def get_ist_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)

# ========================
# 🔁 MAIN LOOP (5 MIN GAP)
# ========================
def run_bot():
    last_signal = None

    while True:
        now = get_ist_time().time()

        if START_TIME <= now <= END_TIME:
            print("Market Open - Checking signal...")

            price = get_market_data()
            signal = generate_signal(price)

            if signal and signal != last_signal:
                msg = f"""
📊 NIFTY SIGNAL

Price: {price}
Signal: {signal}
⏰ Time: {get_ist_time().strftime('%H:%M:%S')}
"""
                send_telegram(msg)
                print("Signal Sent:", signal)
                last_signal = signal
            else:
                print("No new signal")

            time.sleep(300)  # ✅ 5 MINUTES

        else:
            print("Market Closed 😴")
            time.sleep(300)

# ========================
# ▶️ START
# ========================
if __name__ == "__main__":
    print("Bot Started 🚀")
    send_telegram("🤖 Bot Started")
    run_bot()
