import os
import json
import requests
from datetime import datetime, timezone

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# T3-CCI Parameters (igual al indicador TradingView)
CCI_PERIOD = 35
T3_PERIOD = 7
B = 0.618

STATE_FILE = "signal_state.json"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, timeout=10)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_btc_prices():
    """Descarga precios diarios de BTC desde Google Sheets"""
    url = "https://docs.google.com/spreadsheets/d/1AUV0rvijcy7yW3H2IWwlAm2ENHXe6Hfc/export?format=csv&sheet=BTC%20price"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    lines = r.text.strip().split("\n")[1:]  # saltar encabezado
    prices = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cols = line.split(",")
        if len(cols) < 2:
            continue
        date_str = cols[0].strip().replace('"', '')
        price_str = cols[1].strip().replace('"', '')
        # Fecha DD/MM/YYYY → YYYY-MM-DD
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                date_str = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        # Precio formato argentino: "70.522,16" → 70522.16
        price_str = price_str.replace(".", "").replace(",", ".")
        try:
            price = float(price_str)
            if price > 0:
                prices.append({"date": date_str, "price": price})
        except:
            continue
    return sorted(prices, key=lambda x: x["date"])

def calc_cci(prices, period):
    n = len(prices)
    cci = [0.0] * n
    for i in range(period - 1, n):
        slice_p = prices[i - period + 1: i + 1]
        mean = sum(slice_p) / period
        mean_dev = sum(abs(p - mean) for p in slice_p) / period
        cci[i] = (prices[i] - mean) / (0.015 * mean_dev) if mean_dev != 0 else 0
    return cci

def calc_t3cci(prices, cci_period=35, t3_period=7, b=0.618):
    b2 = b * b
    b3 = b2 * b
    c1 = -b3
    c2 = 3 * (b2 + b3)
    c3 = -3 * (2 * b2 + b + b3)
    c4 = 1 + 3 * b + b3 + 3 * b2
    nn = max(1, t3_period)
    nr = 1 + 0.5 * (nn - 1)
    w1 = 2 / (nr + 1)
    w2 = 1 - w1

    xcci = calc_cci(prices, cci_period)
    n = len(prices)
    e1 = e2 = e3 = e4 = e5 = e6 = [0.0] * n
    e1 = list(e1); e2 = list(e2); e3 = list(e3)
    e4 = list(e4); e5 = list(e5); e6 = list(e6)

    for i in range(n):
        prev = lambda arr, i: arr[i-1] if i > 0 else 0
        e1[i] = w1 * xcci[i] + w2 * prev(e1, i)
        e2[i] = w1 * e1[i] + w2 * prev(e2, i)
        e3[i] = w1 * e2[i] + w2 * prev(e3, i)
        e4[i] = w1 * e3[i] + w2 * prev(e4, i)
        e5[i] = w1 * e4[i] + w2 * prev(e5, i)
        e6[i] = w1 * e5[i] + w2 * prev(e6, i)

    return [c1*e6[i] + c2*e5[i] + c3*e4[i] + c4*e3[i] for i in range(n)]

def main():
    print("=== T3-CCI Signal Bot ===")
    state = load_state()

    print("Descargando precios BTC...")
    data = get_btc_prices()
    if len(data) < CCI_PERIOD + 10:
        print("[ERROR] Pocos datos")
        return

    prices = [d["price"] for d in data]
    dates = [d["date"] for d in data]

    print(f"Calculando T3-CCI ({len(prices)} días)...")
    xccir = calc_t3cci(prices, CCI_PERIOD, T3_PERIOD, B)

    # Últimos 2 valores para detectar cruce
    prev_val = xccir[-2]
    curr_val = xccir[-1]
    curr_date = dates[-1]
    curr_price = prices[-1]

    last_signal = state.get("last_signal", "")
    last_date = state.get("last_date", "")

    print(f"T3-CCI prev: {prev_val:.2f} | curr: {curr_val:.2f}")
    print(f"Precio BTC: ${curr_price:,.2f} | Fecha: {curr_date}")

    signal = None
    if prev_val <= 0 and curr_val > 0:
        signal = "COMPRA"
    elif prev_val >= 0 and curr_val < 0:
        signal = "VENTA"

    if signal and curr_date != last_date:
        emoji = "🟢" if signal == "COMPRA" else "🔴"
        msg = (
            f"{emoji} <b>SEÑAL — {signal}</b>\n"
            f"Par: BTCUSDT Diario\n"
            f"Precio: <b>${curr_price:,.2f}</b>\n"
            f"Fecha: {curr_date}"
        )
        send_telegram(msg)
        state["last_signal"] = signal
        state["last_date"] = curr_date
        print(f"[ENVIADO] {signal} @ ${curr_price:,.2f}")
    else:
        # Reporte diario de estado
        trend = "📈 Alcista" if curr_val > 0 else "📉 Bajista"
        msg = (
            f"📊 <b>Señal Diaria — Estado</b>\n"
            f"Precio BTC: <b>${curr_price:,.2f}</b>\n"
            f"Tendencia: {trend}\n"
            f"Última señal: {last_signal or '—'} ({last_date or '—'})"
        )
        send_telegram(msg)
        print(f"[OK] Sin señal nueva — {trend}")

    save_state(state)
    print("=== Listo ===")

if __name__ == "__main__":
    main()
