// Connectivity-only diagnostic. Does not trade, store credentials, or bypass restrictions.
const URL = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=XNYUSDT";
export default {
  async fetch() {
    const checkedAt = new Date().toISOString();
    try {
      const response = await fetch(URL, {headers: {"Accept": "application/json"}});
      const body = await response.text();
      let data = null;
      try { data = JSON.parse(body); } catch {}
      const ok = response.ok && data?.symbol === "XNYUSDT" && Number(data?.price) > 0;
      return Response.json({
        checked_at_utc: checkedAt,
        endpoint: URL,
        http_status: response.status,
        status: ok ? "ok" : "unavailable",
        ...(ok ? {symbol: data.symbol, price: data.price} : {response_sample: body.slice(0, 300)})
      }, {headers: {"Cache-Control": "no-store"}});
    } catch (error) {
      return Response.json({checked_at_utc: checkedAt, endpoint: URL, status: "network_error", detail: String(error)}, {status: 502});
    }
  }
};
