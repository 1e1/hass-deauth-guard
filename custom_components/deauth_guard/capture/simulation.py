"""Periodic fake events for development and automations without WiFi stack."""

from __future__ import annotations

import random
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval

from ..rf_synthetic import synthetic_channel_band_phy
from .base import DeauthEventSource


def _fake_mac() -> str:
    parts = [f"{random.randint(0, 255):02x}" for _ in range(6)]
    return ":".join(parts).upper()


class SimulationSource(DeauthEventSource):
    """Emits synthetic `deauth`-shaped events on a timer (async)."""

    def __init__(self, hass: HomeAssistant, interval_seconds: int) -> None:
        self._hass = hass
        self._interval = max(5, int(interval_seconds))
        self._unsub: Callable[[], None] | None = None
        self._on_event: (
            Callable[[dict[str, Any]], Awaitable[None] | None] | None
        ) = None

    async def async_start(
        self,
        on_event: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> None:
        self._on_event = on_event
        if self._unsub is not None:
            return

        @callback
        def _tick(_now: Any) -> None:
            if self._on_event is None:
                return
            data = {
                "source": _fake_mac(),
                "destination": _fake_mac(),
                "bssid": _fake_mac(),
                "reason": random.choice([1, 3, 4, 6, 7, 8, 9]),
                "rssi": random.randint(-90, -40),
                "interface": "sim0",
                "simulation": True,
                **synthetic_channel_band_phy(),
            }
            self._hass.async_create_task(self._async_emit(data))

        async def _async_emit(data: dict[str, Any]) -> None:
            cb = self._on_event
            if cb is None:
                return
            res = cb(data)
            if res is not None:
                await res

        self._unsub = async_track_time_interval(
            self._hass, _tick, timedelta(seconds=self._interval)
        )
        # One immediate sample for quick verification
        _tick(None)

    async def async_stop(self) -> None:
        if self._unsub is not None:
            self._unsub()
            self._unsub = None
        self._on_event = None
