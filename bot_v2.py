"""
GOLD (XAU/USD), SILVER (XAG/USD) & BITCOIN (BTC/USD) — 200 EMA Alert Bot
- CROSS alert: jab price EMA ko cross kare (upar se neeche ya neeche se upar)
- TOUCH alert: jab price EMA ke bahut paas aaye (cross kiye bina bhi)
Cloud-ready version: saari secret keys environment variables se aati hain.
"""

import requests
import time
import json
import os
from datetime import datetime

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

SYMBOLS = {
    "GOLD (XAUUSD)": "XAU/USD",
    "SILVER (XAGUSD)": "XAG/USD",
    "BITCOIN (BTCUSD)": "BTC/USD",
}

INTERVAL = "5min"
EMA_PERIOD = 200
CHECK_EVERY_SECONDS = 300
STATE_FILE = "ema_alert_state.json"

# Price EMA ke kitna % paas aaye to "touch" mana jaaye
TOUCH_THRESHOLD_PERCENT = 0.15
# Touch flag reset karne ke liye price ko itna door jaana zaroori hai
# (taaki ek hi touch pe baar baar alert na aaye)
TOUCH_RESET_PERCENT = 0.35
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

    diff_percent = abs(close - ema) / ema * 100
    current_position = "above" if close > ema else "below"

    sym_state = state.get(symbol, {})
    previous_position = sym_state.get("position")
    touched = sym_state.get("touched", False)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {name}: price={close}, "
          f"EMA200={round(ema,2)}, diff%={round(diff_percent,3)}, position={current_position}")

    # ---- CROSS ALERT ----
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
        print(">> CROSS ALERT SENT:", msg.replace("\n", " | "))
        touched = False  # cross ke baad touch state reset

    # ---- TOUCH ALERT ----
    if diff_percent <= TOUCH_THRESHOLD_PERCENT and not touched:
        msg = (f"⚪ <b>{name} — TOUCHING 200 EMA</b>\n"
               f"Price ({close}) 200 EMA ({round(ema,2)}) ke bahut paas hai.\n"
               f"Timeframe: {INTERVAL}")
        send_telegram_message(msg)
        print(">> TOUCH ALERT SENT:", msg.replace("\n", " | "))
        touched = True
    elif diff_percent >= TOUCH_RESET_PERCENT:
        touched = False

    state[symbol] = {"position": current_position, "touched": touched}


def main():
    missing = [k for k, v in {
        "BOT_TOKEN": BOT_TOKEN,
        "CHAT_ID": CHAT_ID,
        "TWELVE_DATA_API_KEY": TWELVE_DATA_API_KEY,
    }.items() if not v]

    if missing:
        print("ERROR: Ye environment variables set nahi hain:", ", ".join(missing))
        return

    print("Gold, Silver & Bitcoin 200 EMA Alert Bot start ho gaya...")
    send_telegram_message("✅ Gold, Silver & Bitcoin 200 EMA Alert Bot start ho gaya hai (touch + cross alerts).")
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
