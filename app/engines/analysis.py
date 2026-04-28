from __future__ import annotations

import numpy as np


def _ema(values, period=20):
    if len(values) < period:
        return values[-1] if len(values) else None
    alpha = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]:
        ema = alpha * v + (1 - alpha) * ema
    return float(ema)


def technical_engine(market: dict) -> dict:
    candles = market.get("ohlc", {}).get("1h", [])
    closes = np.array([c["close"] for c in candles if c.get("close") is not None])
    highs = np.array([c["high"] for c in candles if c.get("high") is not None])
    lows = np.array([c["low"] for c in candles if c.get("low") is not None])
    if len(closes) < 30:
        return {"status": "insufficient_data"}

    ema20 = _ema(closes[-80:].tolist(), 20)
    ema50 = _ema(closes[-120:].tolist(), 50)
    trend = "bullish" if ema20 and ema50 and ema20 > ema50 else "bearish"

    support = float(np.percentile(lows[-120:], 20))
    resistance = float(np.percentile(highs[-120:], 80))
    fvg = {"low": float(np.percentile(lows[-60:], 35)), "high": float(np.percentile(highs[-60:], 65))}
    breakout = closes[-1] > resistance
    mr = closes[-1] < support
    invalidation = support if trend == "bullish" else resistance

    return {
        "trend_bias": trend,
        "support": support,
        "resistance": resistance,
        "supply_demand_zone": {"demand": support, "supply": resistance},
        "liquidity_pools": {"buy_side": resistance, "sell_side": support},
        "fvg_zone": fvg,
        "breakout_condition": bool(breakout),
        "mean_reversion_condition": bool(mr),
        "higher_tf_level": float(np.median(closes[-200:])),
        "session_high_low": {"high": float(highs[-24:].max()), "low": float(lows[-24:].min())},
        "bullish_scenario": f"Hold above {support:.2f} and clear {resistance:.2f}",
        "bearish_scenario": f"Fail below {support:.2f} with momentum rejection",
        "invalidation": float(invalidation),
    }


def price_action_engine(market: dict) -> dict:
    candles = market.get("ohlc", {}).get("15m", [])
    closes = np.array([c["close"] for c in candles if c.get("close") is not None])
    highs = np.array([c["high"] for c in candles if c.get("high") is not None])
    lows = np.array([c["low"] for c in candles if c.get("low") is not None])
    if len(closes) < 40:
        return {"status": "insufficient_data"}
    bos = bool(closes[-1] > highs[-20:-1].max() or closes[-1] < lows[-20:-1].min())
    sweep = bool(highs[-1] > highs[-10:-1].max() and closes[-1] < highs[-2])
    return {
        "structure_break": bos,
        "liquidity_sweep": sweep,
        "stop_hunt": sweep,
        "rejection_zone": float((highs[-1] + lows[-1]) / 2),
        "breakout_quality": "strong" if bos and not sweep else "weak",
        "smart_money_interpretation": "possible distribution" if sweep else "orderly continuation",
    }


def volume_engine(market: dict) -> dict:
    candles = market.get("ohlc", {}).get("1m", [])
    vols = np.array([c.get("volume", 0) or 0 for c in candles])
    closes = np.array([c["close"] for c in candles if c.get("close") is not None])
    if len(vols) < 30:
        return {"status": "insufficient_data"}
    spike = vols[-1] > np.mean(vols[-30:]) * 1.8 if np.mean(vols[-30:]) else False
    fake = bool(spike and len(closes) > 3 and abs(closes[-1] - closes[-3]) < np.std(closes[-30:]) * 0.2)
    return {
        "volume_spike": bool(spike),
        "absorption_clue": bool(spike and fake),
        "fake_breakout_detection": fake,
        "weak_participation_breakout": bool(not spike and np.ptp(closes[-20:]) > np.std(closes[-50:])),
        "liquidity_grab": fake,
        "manipulation_signature": "possible" if fake else "low",
        "potential_fake_move_risk": "high" if fake else "normal",
    }


def regime_engine(technical: dict, intermarket: dict) -> str:
    if technical.get("breakout_condition"):
        return "Breakout"
    if technical.get("mean_reversion_condition"):
        return "Mean reversion"
    if intermarket.get("regime") == "risk-off":
        return "Risk-off"
    return "Trending" if technical.get("trend_bias") in {"bullish", "bearish"} else "Range-bound"


def divergence_engine(market: dict, cot: dict, volume: dict) -> dict:
    momentum = market.get("momentum", 0)
    cot_net = cot.get("managed_money", {}).get("net", 0)
    fake = volume.get("fake_breakout_detection", False)
    divergence = momentum > 0 and cot_net < 0
    label = "accumulation" if divergence and fake else "distribution" if divergence else "none"
    return {
        "divergence": divergence,
        "smart_money_trap": bool(divergence and fake),
        "distribution": label == "distribution",
        "accumulation": label == "accumulation",
    }


def trade_board(technical: dict, fundamentals: dict, divergence: dict, volume: dict) -> dict:
    score = 0
    score += 1 if technical.get("trend_bias") == "bullish" else -1
    score += 1 if fundamentals.get("impact_score", {}).get("gold") == "Bullish" else -1 if fundamentals.get("impact_score", {}).get("gold") == "Bearish" else 0
    score -= 1 if divergence.get("divergence") else 0
    score -= 1 if volume.get("potential_fake_move_risk") == "high" else 0
    bias = "Bullish" if score > 0 else "Bearish" if score < 0 else "Neutral"
    return {
        "directional_bias": bias,
        "confidence_score": max(5, min(95, 50 + score * 15)),
        "bullish_case": technical.get("bullish_scenario"),
        "bearish_case": technical.get("bearish_scenario"),
        "key_invalidation": technical.get("invalidation"),
        "risk_warnings": [
            "Source conflict detected" if divergence.get("divergence") else None,
            "Potential fake move risk high" if volume.get("potential_fake_move_risk") == "high" else None,
        ],
    }
