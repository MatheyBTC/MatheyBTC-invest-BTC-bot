import requests
import json
import re

SHEET_URL = "https://docs.google.com/spreadsheets/d/1AUV0rvijcy7yW3H2IWwlAm2ENHXe6Hfc/export?format=csv&sheet=BTC%20price"
PRICES_FILE = "btc_prices.json"
DASHBOARD_FILE = "dashboard.html"

def fetch_prices():
    r = requests.get(SHEET_URL, timeout=30)
    r.raise_for_status()
    lines = r.text.strip().split("\n")[1:]
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cols = line.split(",")
        if len(cols) < 2:
            continue
        date_str = cols[0].strip().replace('"', '')
        price_str = cols[1].strip().replace('"', '')
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                date_str = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        price_str = price_str.replace(".", "").replace(",", ".")
        try:
            p = float(price_str)
            if p > 0:
                result.append([date_str, p])
        except:
            continue
    result.sort(key=lambda x: x[0])
    return result

def update_dashboard(prices_json):
    with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar el bloque de precios embebidos
    new_data = f"const EMBEDDED_PRICES = {prices_json};"
    content = re.sub(
        r"const EMBEDDED_PRICES = \[.*?\];",
        new_data,
        content,
        flags=re.DOTALL
    )

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("Descargando precios...")
    prices = fetch_prices()
    print(f"{len(prices)} días de precios descargados")
    print(f"Último precio: ${prices[-1][1]:,.2f} ({prices[-1][0]})")

    prices_json = json.dumps(prices)

    with open(PRICES_FILE, "w") as f:
        f.write(prices_json)
    print("btc_prices.json actualizado")

    update_dashboard(prices_json)
    print("dashboard.html actualizado")

if __name__ == "__main__":
    main()
