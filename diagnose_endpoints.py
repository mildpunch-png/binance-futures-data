"""Record HTTP status, content type and short response sample from official Binance endpoints."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOSTS = ["fapi.binance.com", "fapi1.binance.com", "fapi2.binance.com", "fapi3.binance.com", "fapi4.binance.com"]
results = []
for host in HOSTS:
    url = f"https://{host}/fapi/v1/ticker/price?symbol=XNYUSDT"
    item = {"host": host, "url": url}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "xny-data-diagnostic/1.1", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read(2048)
            item.update(http_status=response.status, content_type=response.headers.get("Content-Type", ""), final_url=response.geturl())
        item["response_sample"] = raw[:500].decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
            if payload.get("symbol") == "XNYUSDT" and float(payload.get("price", 0)) > 0:
                item.update(status="ok", price=str(payload["price"]), exchange_time_ms=payload.get("time"))
            else:
                item["status"] = "unexpected_json"
        except (ValueError, TypeError, AttributeError):
            item["status"] = "non_json_response"
    except urllib.error.HTTPError as exc:
        item.update(status="http_error", http_status=exc.code, content_type=exc.headers.get("Content-Type", ""), response_sample=exc.read(500).decode("utf-8", errors="replace"))
    except Exception as exc:
        item.update(status="network_error", detail=str(exc)[:300])
    results.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)

out = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "results": results}
Path("data").mkdir(exist_ok=True)
Path("data/endpoint_diagnostics.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
