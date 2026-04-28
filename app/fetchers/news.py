from __future__ import annotations

from datetime import datetime, timezone
import xml.etree.ElementTree as ET

from app.fetchers.http_utils import get_text

RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=GC%3DF&region=US&lang=en-US"


async def fetch_news(client) -> tuple[dict, float, str]:
    text, lat = await get_text(client, RSS)
    root = ET.fromstring(text)
    items = []
    for item in root.findall("./channel/item")[:30]:
        title = item.findtext("title") or ""
        desc = (item.findtext("description") or "").lower()
        category = _category(title + " " + desc)
        sentiment = _sentiment(title + " " + desc)
        items.append(
            {
                "title": title,
                "link": item.findtext("link"),
                "pub_date": item.findtext("pubDate"),
                "category": category,
                "impact": sentiment,
                "urgency": "high" if "breaking" in desc else "normal",
            }
        )
    return {"items": items, "source": "Yahoo Finance RSS", "updated_at": datetime.now(timezone.utc).isoformat()}, lat, RSS


def _category(text: str) -> str:
    mapping = {
        "inflation": "Inflation",
        "fed": "Fed",
        "geopolit": "Geopolitics",
        "central bank": "Central banks",
        "safe haven": "Safe haven demand",
        "dollar": "Dollar strength",
    }
    for key, val in mapping.items():
        if key in text.lower():
            return val
    return "General"


def _sentiment(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["rate cut", "risk-off", "recession", "war"]):
        return "Bullish Gold"
    if any(x in t for x in ["hawkish", "higher yields", "strong dollar"]):
        return "Bearish Gold"
    return "Neutral"
