from __future__ import annotations

import time
from typing import Any

import httpx


async def get_json(client: httpx.AsyncClient, url: str) -> tuple[Any, float]:
    start = time.perf_counter()
    resp = await client.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json(), (time.perf_counter() - start) * 1000


async def get_text(client: httpx.AsyncClient, url: str) -> tuple[str, float]:
    start = time.perf_counter()
    resp = await client.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text, (time.perf_counter() - start) * 1000
