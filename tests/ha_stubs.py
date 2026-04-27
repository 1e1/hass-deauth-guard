"""Minimal `homeassistant` package shims for unit tests (no PyPI `homeassistant` required)."""

from __future__ import annotations

import sys
import types


def register_minimal_homeassistant() -> None:
    if "homeassistant.const" in sys.modules:
        return

    const = types.ModuleType("homeassistant.const")

    class Platform:
        SENSOR = "sensor"

    const.Platform = Platform
    sys.modules["homeassistant.const"] = const

    core = types.ModuleType("homeassistant.core")

    def callback(fn):
        return fn

    class HomeAssistant:  # noqa: D101
        pass

    core.callback = callback
    core.HomeAssistant = HomeAssistant
    sys.modules["homeassistant.core"] = core

    root = types.ModuleType("homeassistant")
    sys.modules["homeassistant"] = root

    storage_mod = types.ModuleType("homeassistant.helpers.storage")

    class Store:  # noqa: D101
        def __init__(self, hass, version, key) -> None:  # noqa: ANN001
            self.hass = hass
            self.version = version
            self.key = key

    storage_mod.Store = Store
    sys.modules["homeassistant.helpers.storage"] = storage_mod

    helpers = types.ModuleType("homeassistant.helpers")
    sys.modules["homeassistant.helpers"] = helpers
