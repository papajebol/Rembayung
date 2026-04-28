from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from app.fetchers.http_utils import get_json

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"


def _to_ohlc(raw: dict) -> pd.DataFrame:
    result = raw["chart"]["result"][0]
    ts = result["timestamp"]
    q = result["indicators"]["quote"][0]
    df = pd.DataFrame(
        {
            "ts": pd.to_datetime(ts, unit="s", utc=True),
            "open": q["open"],
            "high": q["high"],
            "low": q["low"],
            "close": q["close"],
            "volume": q.get("volume", [None] * len(ts)),
        }
    ).dropna(subset=["open", "high", "low", "close"])
    return df


def _resample_4h(df_1h: pd.DataFrame) -> list[dict]:
    ts_df = df_1h.set_index("ts")[["open", "high", "low", "close"]]
    agg = ts_df.resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    out = agg.tail(100).reset_index()
    out["ts"] = out["ts"].astype(str)
    return out.to_dict(orient="records")


async def fetch_market(client) -> tuple[dict, float, str]:
    intervals = {
        "1m": "1d",
        "5m": "5d",
        "15m": "5d",
        "1h": "1mo",
        "1d": "1y",
    }
    out: dict[str, list[dict]] = {}
    latencies = []
    for interval, range_ in intervals.items():
        raw, latency = await get_json(client, YAHOO_CHART.format(symbol="XAUUSD=X", interval=interval, range_=range_))
        latencies.append(latency)
        df = _to_ohlc(raw)
        frame = df.tail(200).copy()
        frame["ts"] = frame["ts"].astype(str)
        out[interval] = frame.to_dict(orient="records")
        if interval == "1h":
            out["4h"] = _resample_4h(df)

    close_prices = pd.Series([x["close"] for x in out["1m"] if x.get("close") is not None])
    returns = close_prices.pct_change().dropna()
    momentum = float((close_prices.iloc[-1] - close_prices.iloc[-30]) / close_prices.iloc[-30]) if len(close_prices) > 30 else 0
    spread = float(np.mean(np.abs(np.diff(close_prices.tail(40))))) if len(close_prices) > 10 else 0
    volatility = float(returns.tail(120).std() * np.sqrt(120)) if len(returns) > 10 else 0

    payload = {
        "spot": close_prices.iloc[-1] if len(close_prices) else None,
        "intraday_move_pct": float(returns.tail(60).sum() * 100) if len(returns) else None,
        "volatility": volatility,
        "momentum": momentum,
        "spread_proxy": spread,
        "market_structure": "bullish" if momentum > 0 else "bearish",
        "ohlc": out,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance",
    }
    return payload, sum(latencies) / len(latencies), "https://query1.finance.yahoo.com"
