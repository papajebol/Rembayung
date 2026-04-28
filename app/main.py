from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.engines.analysis import (
    divergence_engine,
    price_action_engine,
    regime_engine,
    technical_engine,
    trade_board,
    volume_engine,
)
from app.fetchers.cot import fetch_cot
from app.fetchers.events import fetch_events
from app.fetchers.fundamentals import fetch_fundamentals
from app.fetchers.intermarket import fetch_intermarket
from app.fetchers.market import fetch_market
from app.fetchers.news import fetch_news
from app.models import DataStore, ModuleData, SourceStatus

app = FastAPI(title="XAUUSD Intelligence Dashboard")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
store = DataStore()
scheduler = AsyncIOScheduler(timezone="UTC")
clients: set[WebSocket] = set()


async def run_fetch(name: str, source: str, fn):
    status = SourceStatus(name=name, source=source)
    async with httpx.AsyncClient(headers={"User-Agent": "Rembayung/1.0"}) as client:
        try:
            payload, latency, src = await fn(client)
            status.source = src
            status.mark(True, latency)
            return payload, status
        except Exception as exc:  # noqa: BLE001
            status.mark(False, None, str(exc))
            return {"message": "Source Unavailable", "updated_at": datetime.now(timezone.utc).isoformat(), "source": source}, status


async def refresh_all() -> None:
    market_payload, market_status = await run_fetch("market", "Yahoo Finance", fetch_market)
    store.upsert_module(ModuleData("market", "Live Market", market_payload.get("source", ""), market_payload, market_status))

    fundamentals_payload, fundamentals_status = await run_fetch("fundamentals", "FRED", fetch_fundamentals)
    events_payload, events_status = await run_fetch("events", "Forex Factory", fetch_events)
    news_payload, news_status = await run_fetch("news", "Yahoo RSS", fetch_news)
    inter_payload, inter_status = await run_fetch("intermarket", "Yahoo Finance", fetch_intermarket)
    cot_payload, cot_status = await run_fetch("cot", "CFTC", fetch_cot)

    for key, title, payload, status in [
        ("fundamentals", "Fundamental Intelligence", fundamentals_payload, fundamentals_status),
        ("events", "Economic Event Risk", events_payload, events_status),
        ("news", "News & Catalyst", news_payload, news_status),
        ("intermarket", "Intermarket Correlation", inter_payload, inter_status),
        ("cot", "COT Analysis", cot_payload, cot_status),
    ]:
        store.upsert_module(ModuleData(key, title, payload.get("source", ""), payload, status))

    technical = technical_engine(market_payload)
    price_action = price_action_engine(market_payload)
    volume = volume_engine(market_payload)
    regime = regime_engine(technical, inter_payload)
    divergence = divergence_engine(market_payload, cot_payload, volume)
    board = trade_board(technical, fundamentals_payload, divergence, volume)

    derived = {
        "technical": technical,
        "price_action": price_action,
        "volume": volume,
        "regime": {"active_regime": regime},
        "commitment_divergence": divergence,
        "trade_board": board,
    }
    for key, payload in derived.items():
        s = SourceStatus(name=key, source="Internal Signal Engine")
        s.mark(True, 0.1)
        store.upsert_module(ModuleData(key, key, "Internal", payload, s))

    await broadcast_snapshot()


async def broadcast_snapshot() -> None:
    dead = []
    for ws in clients:
        try:
            await ws.send_json(store.snapshot())
        except Exception:  # noqa: BLE001
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


@app.on_event("startup")
async def on_startup() -> None:
    await refresh_all()
    scheduler.add_job(refresh_all, "interval", minutes=1, id="core_refresh")
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    scheduler.shutdown(wait=False)


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")


@app.get("/api/snapshot")
async def snapshot():
    return store.snapshot()


@app.websocket("/ws")
async def ws_feed(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_json(store.snapshot())
    try:
        while True:
            await websocket.receive_text()
    except Exception:  # noqa: BLE001
        clients.discard(websocket)


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}
