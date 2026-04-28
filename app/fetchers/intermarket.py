from __future__ import annotations

import pandas as pd

from app.fetchers.http_utils import get_json

SYMBOLS = {
    "xau": "XAUUSD=X",
    "dxy": "DX-Y.NYB",
    "us10y": "^TNX",
    "spx": "^GSPC",
    "crude": "CL=F",
    "usdjpy": "JPY=X",
}


async def fetch_intermarket(client) -> tuple[dict, float, str]:
    closes = {}
    lats = []
    for key, sym in SYMBOLS.items():
        raw, lat = await get_json(client, f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1h&range=1mo")
        lats.append(lat)
        c = raw["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes[key] = pd.Series([x for x in c if x is not None]).pct_change().dropna().tail(120)

    xau = closes.pop("xau")
    corr = {k: float(xau.corr(v)) for k, v in closes.items() if len(v) > 20}
    regime = "risk-off" if corr.get("spx", 0) < -0.2 and corr.get("dxy", 0) < -0.2 else "risk-on"
    div = [k for k, v in corr.items() if abs(v) < 0.1]
    return {
        "correlations": corr,
        "divergences": div,
        "regime": regime,
        "source": "Yahoo Finance",
    }, sum(lats) / len(lats), "https://query1.finance.yahoo.com"
