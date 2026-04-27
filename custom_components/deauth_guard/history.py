"""Bounded persistent history of detection records."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Final

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import (
    HIGHEST_HISTORY_MAX,
    LOWEST_HISTORY_MAX,
    STORAGE_KEY,
    STORAGE_VERSION,
)

STORE_SCHEMA_VERSION: Final = 1


@dataclass
class DeauthRecord:
    """A single row stored in history (JSON-serializable)."""

    ts: float
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> DeauthRecord:
        return cls(float(raw["ts"]), raw["data"])


class DeauthHistoryStore:
    """Versioned `Store` wrapper with a maximum entry count."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        max_entries: int,
    ) -> None:
        self._hass = hass
        self._max = max(
            LOWEST_HISTORY_MAX, min(int(max_entries), HIGHEST_HISTORY_MAX)
        )
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._entries: list[DeauthRecord] = []

    @property
    def max_entries(self) -> int:
        return self._max

    @callback
    def set_max_entries(self, max_entries: int) -> None:
        self._max = max(
            LOWEST_HISTORY_MAX, min(int(max_entries), HIGHEST_HISTORY_MAX)
        )
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
            # Persist trimmed list asynchronously
            self._hass.async_create_task(self._async_persist())

    @staticmethod
    def _normalize_persisted(raw: dict[str, Any]) -> list[DeauthRecord]:
        if raw.get("version") != STORE_SCHEMA_VERSION:
            return []
        rows: list[DeauthRecord] = []
        for item in raw.get("rows", []):
            try:
                rows.append(DeauthRecord.from_dict(item))
            except (KeyError, TypeError, ValueError):
                continue
        return rows

    def _as_persisted(self) -> dict[str, Any]:
        return {
            "version": STORE_SCHEMA_VERSION,
            "rows": [
                {"ts": r.ts, "data": dict(r.data)} for r in self._entries
            ],
        }

    async def async_load(self) -> None:
        raw = await self._store.async_load() or {}
        if not raw:
            self._entries = []
            return
        if "rows" in raw and raw.get("version") == STORE_SCHEMA_VERSION:
            self._entries = self._normalize_persisted(raw)
        else:
            # Legacy / unknown → start clean
            self._entries = []

    async def _async_persist(self) -> None:
        await self._store.async_save(self._as_persisted())

    async def async_add(self, data: dict[str, Any], *, now: float | None = None) -> DeauthRecord:
        rec = DeauthRecord(ts=now or time.time(), data=dict(data))
        self._entries.append(rec)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
        await self._async_persist()
        return rec

    def as_list(self) -> list[dict[str, Any]]:
        """Return records as plain dicts for service responses."""
        return [{"ts": r.ts, **r.data} for r in self._entries]

    def last(self) -> DeauthRecord | None:
        if not self._entries:
            return None
        return self._entries[-1]

    async def async_clear(self) -> None:
        self._entries = []
        await self._async_persist()
