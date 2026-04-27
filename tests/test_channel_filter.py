"""Tests for `channel_allowed`."""

from __future__ import annotations

from custom_components.deauth_guard.channel_filter import (
    channel_allowed,
    event_passes_radios,
)
from custom_components.deauth_guard.const import BAND_2_4_GHZ, KEY_CHANNEL, KEY_INTERFACE


def test_simulation_bypasses_selection() -> None:
    d = {KEY_CHANNEL: 99, "simulation": True}
    assert channel_allowed(d, [1, 6, 11], simulation=True) is True


def test_empty_selection_means_all() -> None:
    d = {KEY_CHANNEL: 3}
    assert channel_allowed(d, [], simulation=False) is True
    assert channel_allowed(d, None, simulation=False) is True


def test_selected_includes_channel() -> None:
    d = {KEY_CHANNEL: 6}
    assert channel_allowed(d, [1, 6, 11], simulation=False) is True


def test_selected_excludes_channel() -> None:
    d = {KEY_CHANNEL: 3}
    assert channel_allowed(d, [1, 6, 11], simulation=False) is False


def test_missing_channel_is_included() -> None:
    d: dict = {"band": BAND_2_4_GHZ}
    assert channel_allowed(d, [6], simulation=False) is True


def test_event_passes_radios_per_interface() -> None:
    radios = [
        {"interface": "wlan0", "channels": [1, 6, 11]},
        {"interface": "wlan1", "channels": [36]},
    ]
    a = {KEY_CHANNEL: 6, KEY_INTERFACE: "wlan0"}
    b = {KEY_CHANNEL: 6, KEY_INTERFACE: "wlan1"}
    assert event_passes_radios(a, radios, simulation_only=False) is True
    assert event_passes_radios(b, radios, simulation_only=False) is False


def test_event_passes_radios_simulation_mode() -> None:
    assert event_passes_radios(
        {KEY_CHANNEL: 99, "simulation": True},
        [],
        simulation_only=True,
    ) is True
