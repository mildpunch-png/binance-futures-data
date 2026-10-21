#!/usr/bin/env python3
"""Fetch XNYUSDT USDT-M futures last traded price from Binance's official API."""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYMBOL = "XNYUSDT"
URL = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={SYMBOL}"

request = urllib.request.Request(URL, headers={"User-Agent": "binance-futures-data/1.0", "Accept": "application/json"})
with urllib.request.urlopen(request, timeout=20) as response:
    payload = json.load(response)

if payload.get("symbol") != SYMBOL or float(payload["price"]) <= 0:
    raise ValueError(f"Unexpected Binance response: {payload}")

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
data = {
    "exchange": "BINANCE",
    "market": "USDT-M perpetual futures",
    "symbol": SYMBOL,
    "price_type": "last_trade",
    "price": str(payload["price"]),
    "exchange_time_ms": payload.get("time"),
    "collected_at_utc": now,
    "source": URL
}
Path("data").mkdir(exist_ok=True)
Path("data/latest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(data, ensure_ascii=False))
