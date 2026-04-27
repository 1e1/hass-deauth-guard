"""Coordinator: capture, channel filter, alert policy, history, bus events."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .alert_policy import AlertEmissionController, parse_alert_rules
from .capture import SimulationSource
from .channel_filter import event_passes_radios
from .const import (
    CONF_ALERT_RULES,
    CONF_SIM_INTERVAL,
    DOMAIN,
    EVENT_ATTACK,
    KEY_EMIT_INFO,
    SIMULATION_INTERFACE,
)
from .history import DeauthHistoryStore
from .options_util import is_simulation_only, normalize_radios

_LOGGER = logging.getLogger(__name__)


class DeauthGuardCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Holds last payload and total count; drives entity updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        history: DeauthHistoryStore,
        options: dict[str, Any],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self._history = history
        self._options = options
        self._sources: list[SimulationSource] = []
        self._alerts = self._new_alert_controller(options)

    @staticmethod
    def _new_alert_controller(
        options: dict[str, Any],
    ) -> AlertEmissionController:
        sim = is_simulation_only(normalize_radios(options))
        rules = parse_alert_rules(options.get(CONF_ALERT_RULES))
        return AlertEmissionController(rules, simulation_mode=sim)

    @property
    def history(self) -> DeauthHistoryStore:
        return self._history

    def set_options(self, options: dict[str, Any]) -> None:
        self._options = options
        self._alerts = self._new_alert_controller(options)

    async def _async_update_data(self) -> dict[str, Any]:
        return self.data or self._empty_state()

    @staticmethod
    def _empty_state() -> dict[str, Any]:
        return {
            "last": None,
            "total_recorded_session": 0,
        }

    def _is_simulation(self) -> bool:
        return is_simulation_only(normalize_radios(self._options))

    async def async_start_sources(self) -> None:
        self._sources = []
        if self._is_simulation():
            interval = int(self._options.get(CONF_SIM_INTERVAL, 10))
            src = SimulationSource(self.hass, interval)
            self._sources.append(src)
            await src.async_start(self._on_capture_event)
            return
        radios = normalize_radios(self._options)
        for row in radios:
            if (iface := row.get("interface")) == SIMULATION_INTERFACE:
                continue
            _LOGGER.info(
                "Interface %r selected; real capture not yet implemented "
                "(see docs/DECISIONS.md) — no frames until a backend exists",
                iface,
            )

    async def async_stop_sources(self) -> None:
        for s in self._sources:
            await s.async_stop()
        self._sources = []

    async def _on_capture_event(self, data: dict[str, Any]) -> None:
        await self.async_note_detection(data)

    @callback
    def _passes_channel_filter(self, data: dict[str, Any]) -> bool:
        radios = normalize_radios(self._options)
        return event_passes_radios(
            data,
            radios,
            simulation_only=is_simulation_only(radios),
        )

    async def async_note_detection(self, data: dict[str, Any]) -> None:
        if not self._passes_channel_filter(data):
            return
        await self._history.async_add(data)
        n_seen = (self.data or {}).get("total_recorded_session", 0) + 1
        if self._alerts.should_emit():
            out = {**data, KEY_EMIT_INFO: "alert"}
            self.hass.bus.async_fire(EVENT_ATTACK, out)
        self.async_set_updated_data(
            {
                "last": data,
                "total_recorded_session": n_seen,
            }
        )
