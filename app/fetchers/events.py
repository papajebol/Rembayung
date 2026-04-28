from __future__ import annotations

from datetime import datetime, timezone
import xml.etree.ElementTree as ET

from app.fetchers.http_utils import get_text

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
KEYWORDS = ("CPI", "Non-Farm", "FOMC", "PCE", "Fed", "Powell", "Employment")


async def fetch_events(client) -> tuple[dict, float, str]:
    xml, lat = await get_text(client, URL)
    root = ET.fromstring(xml)
    now = datetime.now(timezone.utc)
    events = []
    for item in root.findall("event"):
        title = (item.findtext("title") or "").strip()
        if not any(k.lower() in title.lower() for k in KEYWORDS):
            continue
        dt_text = item.findtext("dt") or ""
        try:
            dt = datetime.fromisoformat(dt_text.replace("Z", "+00:00"))
        except ValueError:
            continue
        countdown = int((dt - now).total_seconds())
        impact = (item.findtext("impact") or "").lower()
        events.append(
            {
                "title": title,
                "country": item.findtext("country"),
                "datetime": dt.isoformat(),
                "countdown_seconds": countdown,
                "impact": impact,
                "historical_xau_tendency": "high volatility" if impact == "high" else "moderate",
            }
        )
    events.sort(key=lambda x: x["datetime"])
    return {"events": events[:20], "source": "Forex Factory XML", "updated_at": now.isoformat()}, lat, URL
