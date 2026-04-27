"""Tests for `options_util` (multi-radio options)."""

from __future__ import annotations

from custom_components.deauth_guard.const import (
    CONF_RADIO1_CHANNELS,
    CONF_RADIO1_INTERFACE,
    CONF_RADIO2_CHANNELS,
    CONF_RADIO2_INTERFACE,
    CONF_RADIO3_CHANNELS,
    CONF_RADIO3_INTERFACE,
    CONF_RADIOS,
    SIMULATION_INTERFACE,
)
from custom_components.deauth_guard.options_util import (
    build_radios_from_form,
    form_defaults_from_radios,
    is_simulation_only,
    normalize_radios,
)


def test_normalize_defaults_when_no_radios() -> None:
    r = normalize_radios({})
    assert r == [{"interface": SIMULATION_INTERFACE, "channels": []}]


def test_normalize_from_radios() -> None:
    r = normalize_radios(
        {
            CONF_RADIOS: [
                {"interface": "wlan0", "channels": [1]},
                {"interface": "wlan1", "channels": [36]},
            ],
        }
    )
    assert len(r) == 2
    assert r[1]["interface"] == "wlan1"


def test_is_simulation_only() -> None:
    assert is_simulation_only(
        [{"interface": SIMULATION_INTERFACE, "channels": []}]
    )
    assert not is_simulation_only(
        [
            {"interface": "wlan0", "channels": []},
        ]
    )


def test_build_radios_dedup_second() -> None:
    r = build_radios_from_form(
        {
            CONF_RADIO1_INTERFACE: "wlan0",
            CONF_RADIO1_CHANNELS: [1],
            CONF_RADIO2_INTERFACE: "wlan0",
            CONF_RADIO2_CHANNELS: [6],
        }
    )
    assert len(r) == 1
    assert r[0]["interface"] == "wlan0"


def test_build_radios_stops_at_simulation_primary() -> None:
    r = build_radios_from_form(
        {
            CONF_RADIO1_INTERFACE: SIMULATION_INTERFACE,
            CONF_RADIO1_CHANNELS: [],
            CONF_RADIO2_INTERFACE: "wlan0",
            CONF_RADIO2_CHANNELS: [1],
        }
    )
    assert r == [{"interface": SIMULATION_INTERFACE, "channels": []}]


def test_form_roundtrip() -> None:
    stored = [
        {"interface": "wlan0", "channels": [1, 6]},
        {"interface": "wlan1", "channels": [36]},
    ]
    b = form_defaults_from_radios(stored)
    out = build_radios_from_form(
        {
            CONF_RADIO1_INTERFACE: b[CONF_RADIO1_INTERFACE],
            CONF_RADIO1_CHANNELS: b[CONF_RADIO1_CHANNELS],
            CONF_RADIO2_INTERFACE: b[CONF_RADIO2_INTERFACE],
            CONF_RADIO2_CHANNELS: b[CONF_RADIO2_CHANNELS],
            CONF_RADIO3_INTERFACE: b[CONF_RADIO3_INTERFACE],
            CONF_RADIO3_CHANNELS: b[CONF_RADIO3_CHANNELS],
        }
    )
    assert out == stored
