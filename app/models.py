from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SourceStatus:
    name: str
    source: str
    healthy: bool = False
    status: str = "failing"
    latency_ms: float | None = None
    last_updated: str | None = None
    freshness: str = "stale"
    error: str | None = None

    def mark(self, ok: bool, latency_ms: float | None, error: str | None = None) -> None:
        self.healthy = ok
        self.status = "healthy" if ok else "failing"
        self.latency_ms = latency_ms
        self.last_updated = datetime.now(timezone.utc).isoformat()
        self.freshness = "fresh" if ok else "stale"
        self.error = error


@dataclass
class ModuleData:
    key: str
    title: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    status: SourceStatus | None = None


class DataStore:
    def __init__(self) -> None:
        self.modules: dict[str, ModuleData] = {}
        self.sources: dict[str, SourceStatus] = {}

    def upsert_module(self, module: ModuleData) -> None:
        self.modules[module.key] = module
        if module.status:
            self.sources[module.status.name] = module.status

    def snapshot(self) -> dict[str, Any]:
        return {
            "modules": {k: v.payload | {"meta": self._status_dict(v)} for k, v in self.modules.items()},
            "integrity": {
                "sources": [self._source_dict(s) for s in self.sources.values()],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    @staticmethod
    def _source_dict(source: SourceStatus) -> dict[str, Any]:
        return {
            "name": source.name,
            "source": source.source,
            "status": source.status,
            "healthy": source.healthy,
            "latency_ms": source.latency_ms,
            "last_updated": source.last_updated,
            "freshness": source.freshness,
            "error": source.error,
        }

    def _status_dict(self, module: ModuleData) -> dict[str, Any]:
        if not module.status:
            return {}
        return self._source_dict(module.status)
