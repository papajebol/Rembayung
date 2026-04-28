from __future__ import annotations

import io
from datetime import datetime, timezone

import pandas as pd

from app.fetchers.http_utils import get_text

CFTC_URL = "https://www.cftc.gov/dea/newcot/f_disagg.txt"


async def fetch_cot(client) -> tuple[dict, float, str]:
    text, lat = await get_text(client, CFTC_URL)
    df = pd.read_csv(io.StringIO(text))
    market_col = "Market_and_Exchange_Names"
    gold = df[df[market_col].str.contains("GOLD", case=False, na=False)].copy()
    if gold.empty:
        raise ValueError("No GOLD contract found in CFTC disaggregated report")
    gold["Report_Date_as_YYYY-MM-DD"] = pd.to_datetime(gold["Report_Date_as_YYYY-MM-DD"])
    gold = gold.sort_values("Report_Date_as_YYYY-MM-DD")
    latest = gold.iloc[-1]
    prev = gold.iloc[-2] if len(gold) > 1 else latest

    mm_long = int(latest["M_Money_Positions_Long_All"])
    mm_short = int(latest["M_Money_Positions_Short_All"])
    comm_long = int(latest["Prod_Merc_Positions_Long_All"])
    comm_short = int(latest["Prod_Merc_Positions_Short_All"])
    oi = int(latest["Open_Interest_All"])
    net = mm_long - mm_short
    prev_net = int(prev["M_Money_Positions_Long_All"]) - int(prev["M_Money_Positions_Short_All"])

    percentile = float((gold["M_Money_Positions_Long_All"] - gold["M_Money_Positions_Short_All"]).rank(pct=True).iloc[-1] * 100)
    implication = "Bullish" if net > 0 else "Bearish"

    return {
        "report_date": latest["Report_Date_as_YYYY-MM-DD"].date().isoformat(),
        "managed_money": {"long": mm_long, "short": mm_short, "net": net, "weekly_change": net - prev_net},
        "commercials": {"long": comm_long, "short": comm_short, "net": comm_long - comm_short},
        "open_interest": oi,
        "positioning_extreme_pct_52w": percentile,
        "interpretation": implication,
        "divergence_warning": "elevated" if percentile > 90 or percentile < 10 else "normal",
        "source": "CFTC Disaggregated COT",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }, lat, CFTC_URL
