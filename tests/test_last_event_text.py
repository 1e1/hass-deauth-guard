"""Tests for `last_event_summary` (stdlib, no Home Assistant)."""

from __future__ import annotations

from custom_components.deauth_guard.const import BAND_2_4_GHZ
from custom_components.deauth_guard.last_event_text import last_event_summary


def test_last_event_simulation_with_rf() -> None:
    s = last_event_summary(
        {
            "source": "AA:BB:CC:DD:EE:FF",
            "reason": 7,
            "simulation": True,
            "channel": 6,
            "band": BAND_2_4_GHZ,
            "wifi_phy": "n",
        }
    )
    assert "sim" in s
    assert "ch6" in s
    assert BAND_2_4_GHZ in s
    assert "phy=n" in s
    assert "reason=7" in s
    assert "AA:BB:CC:DD:EE:FF" in s


def test_last_event_production_minimal() -> None:
    s = last_event_summary(
        {
            "source": "11:22:33:44:55:66",
            "reason": 3,
            "simulation": False,
        }
    )
    assert not s.startswith("sim ")
    assert "reason=3" in s
