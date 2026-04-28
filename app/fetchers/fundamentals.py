from __future__ import annotations

import io
from datetime import datetime, timezone

import pandas as pd

from app.fetchers.http_utils import get_json, get_text

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
SERIES = {
    "fed_funds": "DFF",
    "us2y": "DGS2",
    "us10y": "DGS10",
    "tips10y": "DFII10",
    "inflation_breakeven": "T10YIE",
    "cpi": "CPIAUCSL",
}


async def _fred_latest(client, series: str) -> tuple[float | None, float]:
    text, lat = await get_text(client, FRED.format(series=series))
    df = pd.read_csv(io.StringIO(text)).dropna()
    if df.empty:
        return None, lat
    return float(df.iloc[-1, 1]), lat


async def fetch_fundamentals(client) -> tuple[dict, float, str]:
    data = {}
    latencies = []
    for k, s in SERIES.items():
        value, lat = await _fred_latest(client, s)
        data[k] = value
        latencies.append(lat)

    dxy, ylat = await get_json(client, "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=5m&range=1d")
    latencies.append(ylat)
    dxy_close = dxy["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    data["dxy"] = [x for x in dxy_close if x is not None][-1]

    data["impact_score"] = _impact(data)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["source"] = "FRED + Yahoo Finance"
    return data, sum(latencies) / len(latencies), "https://fred.stlouisfed.org"


def _impact(data: dict) -> dict:
    score = 0
    if data.get("dxy") and data["dxy"] > 104:
        score -= 1
    if data.get("us10y") and data["us10y"] > 4.5:
        score -= 1
    if data.get("tips10y") and data["tips10y"] > 2.0:
        score -= 1
    if data.get("inflation_breakeven") and data["inflation_breakeven"] > 2.2:
        score += 1
    label = "Neutral"
    if score >= 1:
        label = "Bullish"
    elif score <= -1:
        label = "Bearish"
    return {"score": score, "gold": label}
