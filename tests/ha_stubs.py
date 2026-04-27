"""Minimal `homeassistant` package shims for unit tests (no PyPI `homeassistant` required)."""

from __future__ import annotations

import sys
import types
from typing import Any, Generic, TypeVar

import voluptuous as vol

_T = TypeVar("_T")


def register_minimal_homeassistant() -> None:
    if "homeassistant.helpers.update_coordinator" in sys.modules:
        return

    root = types.ModuleType("homeassistant")
    sys.modules["homeassistant"] = root

    const = types.ModuleType("homeassistant.const")

    class Platform:
        SENSOR = "sensor"

    const.Platform = Platform
    sys.modules["homeassistant.const"] = const

    core = types.ModuleType("homeassistant.core")

    def callback(fn):
        return fn

    class ServiceCall:  # noqa: D101
        pass

    class SupportsResponse:  # noqa: D101
        ONLY = object()

    class _EventBus:
        def async_fire(self, _event_type: str, _event_data: Any = None) -> None:
            return None

    class HomeAssistant:  # noqa: D101
        def __init__(self) -> None:
            self.bus = _EventBus()

    core.callback = callback
    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall
    core.SupportsResponse = SupportsResponse
    sys.modules["homeassistant.core"] = core

    config_entries = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:  # noqa: D101
        pass

    config_entries.ConfigEntry = ConfigEntry
    sys.modules["homeassistant.config_entries"] = config_entries

    cv_mod = types.ModuleType("homeassistant.helpers.config_validation")

    def config_entry_only_config_schema() -> vol.Schema:
        return vol.Schema({})

    cv_mod.config_entry_only_config_schema = config_entry_only_config_schema
    sys.modules["homeassistant.helpers.config_validation"] = cv_mod

    typing_mod = types.ModuleType("homeassistant.helpers.typing")
    typing_mod.ConfigType = dict[str, Any]
    sys.modules["homeassistant.helpers.typing"] = typing_mod

    uc_mod = types.ModuleType("homeassistant.helpers.update_coordinator")

    class DataUpdateCoordinator(Generic[_T]):  # noqa: D101
        def __init__(
            self,
            hass: Any,
            logger: Any,
            *,
            name: str | None = None,
            update_interval: Any = None,
        ) -> None:
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval
            self.data: _T | None = None

        def async_set_updated_data(self, data: _T) -> None:
            self.data = data

    uc_mod.DataUpdateCoordinator = DataUpdateCoordinator
    sys.modules["homeassistant.helpers.update_coordinator"] = uc_mod

    event_mod = types.ModuleType("homeassistant.helpers.event")

    def async_track_time_interval(
        _hass: Any, action: Any, _interval: Any
    ) -> Any:
        def _unsub() -> None:
            return None

        return _unsub

    event_mod.async_track_time_interval = async_track_time_interval
    sys.modules["homeassistant.helpers.event"] = event_mod

    storage_mod = types.ModuleType("homeassistant.helpers.storage")

    class Store:  # noqa: D101
        def __init__(self, hass: Any, version: int, key: str) -> None:
            self.hass = hass
            self.version = version
            self.key = key

    storage_mod.Store = Store
    sys.modules["homeassistant.helpers.storage"] = storage_mod

    helpers = types.ModuleType("homeassistant.helpers")
    sys.modules["homeassistant.helpers"] = helpers
