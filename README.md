# XAU/USD Intelligence Dashboard

Production-ready FastAPI + Replit dashboard using only live feeds/scrapers. No mock data.

## Modules
- Live market panel (XAUUSD live + multi-timeframe OHLC)
- Fundamentals (FRED + DXY)
- Economic events calendar
- Technical engine
- Price action module
- Volume and fake move risk
- Intermarket correlation
- News intelligence
- COT (official CFTC)
- Regime detector
- Commitment divergence
- Trade intelligence board
- Data integrity panel

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Source behavior
Each widget includes source, timestamp, freshness, and fetch status.
If a feed fails, payload shows `Source Unavailable`.
