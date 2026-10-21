"""Diagnose reachability of official Binance USDT-M Futures endpoints."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

hosts = ["fapi.binance.com", "fapi1.binance.com", "fapi2.binance.com", "fapi3.binance.com", "fapi4.binance.com"]
results = []
for host in hosts:
    url = f"https://{host}/fapi/v1/ticker/price?symbol=XNYUSDT"
    item = {"host": host, "url": url}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "xny-data-diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.load(response)
        if payload.get("symbol") != "XNYUSDT" or not payload.get("price"):
            raise ValueError("Unexpected symbol or missing price")
        item.update(status="ok", price=str(payload["price"]), exchange_time_ms=payload.get("time"))
    except urllib.error.HTTPError as e:
        item.update(status="http_error", http_status=e.code, detail=e.read(300).decode("utf-8", errors="replace"))
    except Exception as e:
        item.update(status="error", detail=str(e)[:300])
    results.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)
out = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "results": results}
Path("data").mkdir(exist_ok=True)
Path("data/endpoint_diagnostics.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
