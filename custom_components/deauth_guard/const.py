"""Constants for the Deauth Guard integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "deauth_guard"
PLATFORMS: Final = [Platform.SENSOR]

# Store
STORAGE_KEY: Final = f"{DOMAIN}.history"
STORAGE_VERSION: Final = 1

# Config / options (root keys; see CONF_RADIOS for Wi-Fi sources)
# interface/channels: only read during old migrations, removed at options schema v4
CONF_INTERFACE: Final = "interface"
CONF_CHANNELS: Final = "channels"
CONF_ALERT_RULES: Final = "alert_rules"
CONF_SIMULATION_MODE: Final = "simulation_mode"
CONF_HISTORY_MAX: Final = "history_max_entries"
CONF_SIM_INTERVAL: Final = "simulation_interval_seconds"
CONF_CAPTURE_BACKEND: Final = "capture_backend"
CONF_RADIOS: Final = "radios"

# Config flow: one primary + two optional Wi-Fi sources (single config entry)
CONF_RADIO1_INTERFACE: Final = "radio1_interface"
CONF_RADIO1_CHANNELS: Final = "radio1_channels"
CONF_RADIO2_INTERFACE: Final = "radio2_interface"
CONF_RADIO2_CHANNELS: Final = "radio2_channels"
CONF_RADIO3_INTERFACE: Final = "radio3_interface"
CONF_RADIO3_CHANNELS: Final = "radio3_channels"

SIMULATION_INTERFACE: Final = "simulation"

# 2.4 GHz + common 5/6 GHz (multi-select; empty = listen on all reported channels)
def _build_channel_choices() -> tuple[int, ...]:
    raw: list[int] = list(range(1, 12))
    raw += [
        36, 40, 44, 48, 52, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136,
        140, 144, 149, 153, 157, 161, 165,
    ]
    raw += [
        1, 5, 9, 13, 17, 21, 25, 33, 37, 45, 53, 65, 85, 97, 101, 105, 109,
        113, 121, 129, 137, 145, 153, 161, 169, 177, 185, 193, 201, 213, 225, 233,
    ]
    seen: set[int] = set()
    out: list[int] = []
    for c in raw:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return tuple(out)


ALL_SELECTABLE_CHANNELS_ORDERED: Final = _build_channel_choices()

DEFAULT_INTERFACE: Final = SIMULATION_INTERFACE
DEFAULT_SIMULATION_MODE: Final = True
DEFAULT_HISTORY_MAX: Final = 100
DEFAULT_SIM_INTERVAL: Final = 10
LOWEST_HISTORY_MAX: Final = 10
HIGHEST_HISTORY_MAX: Final = 2000

# Event bus
EVENT_ATTACK: Final = f"{DOMAIN}_attack"

# Event payload keys (deauth_guard_attack) — use these names in capture backends
# band: coarse RF domain (simpler than per-vendor 802.11n/ac labels when unknown)
KEY_CHANNEL: Final = "channel"
KEY_BAND: Final = "band"
KEY_WIFI_PHY: Final = "wifi_phy"
KEY_EMIT_INFO: Final = "emit"
KEY_INTERFACE: Final = "interface"

# Band labels (synthetic + tests)
BAND_2_4_GHZ: Final = "2.4 GHz"
BAND_5_GHZ: Final = "5 GHz"
BAND_6_GHZ: Final = "6 GHz"

# Services
SERVICE_GET_HISTORY: Final = "get_history"
SERVICE_CLEAR_HISTORY: Final = "clear_history"

# Entities
SENSOR_LAST_EVENT: Final = "last_event"

# Capture
CAPTURE_SIMULATION: Final = "simulation"
CAPTURE_STUB: Final = "stub"
