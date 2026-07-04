"""
GOLD (XAU/USD) & SILVER (XAG/USD) — 200 EMA Crossover Alert Bot
Cloud-ready version: saari secret keys environment variables se aati hain
(Railway/Render jaise platform pe ye "Variables" section me daali jaati hain).
"""

import requests
import time
import json
import os
from datetime import datetime

# ================= CONFIG (env variables se aayega) =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

SYMBOLS = {
    "GOLD (XAUUSD)": "XAU/USD",
    "SILVER (XAGUSD)": "XAG/USD",
}

INTERVAL = "5min"
EMA_PERIOD = 200
CHECK_EVERY_SECONDS = 300
STATE_FILE = "ema_alert_state.json"
# ======================================================================


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print("Telegram send error:", r.text)
    except Exception as e:
        print("Telegram send exception:", e)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_latest_close(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "outputsize": 2,
        "apikey": TWELVE_DATA_API_KEY,
    }
    r = requests.get(url, params=params, timeout=15).json()
    if "values" not in r:
        print("Price fetch error:", r)
        return None
    return float(r["values"][0]["close"])


def get_latest_ema(symbol):
    url = "https://api.twelvedata.com/ema"
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "time_period": EMA_PERIOD,
        "outputsize": 1,
        "apikey": TWELVE_DATA_API_KEY,
    }
    r = requests.get(url, params=params, timeout=15).json()
    if "values" not in r:
        print("EMA fetch error:", r)
        return None
    return float(r["values"][0]["ema"])


def check_symbol(name, symbol, state):
    close = get_latest_close(symbol)
    ema = get_latest_ema(symbol)

    if close is None or ema is None:
        return

    current_position = "above" if close > ema else "below"
    previous_position = state.get(symbol)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {name}: price={close}, "
          f"EMA200={round(ema,2)}, position={current_position}")

    if previous_position is not None and previous_position != current_position:
        if current_position == "above":
            msg = (f"🟢 <b>{name} — BULLISH CROSS</b>\n"
                   f"Price ({close}) ne 200 EMA ({round(ema,2)}) ko upar cross kiya!\n"
                   f"Timeframe: {INTERVAL}")
        else:
            msg = (f"🔴 <b>{name} — BEARISH CROSS</b>\n"
                   f"Price ({close}) ne 200 EMA ({round(ema,2)}) ko neeche cross kiya!\n"
                   f"Timeframe: {INTERVAL}")
        send_telegram_message(msg)
        print(">> ALERT SENT:", msg.replace("\n", " | "))

    state[symbol] = current_position


def main():
    missing = [k for k, v in {
        "BOT_TOKEN": BOT_TOKEN,
        "CHAT_ID": CHAT_ID,
        "TWELVE_DATA_API_KEY": TWELVE_DATA_API_KEY,
    }.items() if not v]

    if missing:
        print("ERROR: Ye environment variables set nahi hain:", ", ".join(missing))
        print("Railway/Render ke 'Variables' section me inhe add karo aur restart karo.")
        return

    print("Gold & Silver 200 EMA Alert Bot start ho gaya...")
    send_telegram_message("✅ Gold & Silver 200 EMA Alert Bot start ho gaya hai.")
    state = load_state()

    while True:
        for name, symbol in SYMBOLS.items():
            try:
                check_symbol(name, symbol, state)
            except Exception as e:
                print(f"Error checking {name}: {e}")
            time.sleep(2)

        save_state(state)
        time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    main()
