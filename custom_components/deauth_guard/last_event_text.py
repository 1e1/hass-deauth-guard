"""Human-readable last-event line (stdlib; used by sensor and tests)."""

from __future__ import annotations

from typing import Any


def last_event_summary(last: dict[str, Any]) -> str:
    """Build the same one-line summary as `DeauthLastEventSensor.native_value`."""
    reason = last.get("reason")
    src = last.get("source", "?")
    ch = last.get("channel")
    band = last.get("band")
    phy = last.get("wifi_phy")
    rf_bits: list[str] = []
    if ch is not None:
        rf_bits.append(f"ch{ch}")
    if band:
        rf_bits.append(str(band))
    if phy:
        rf_bits.append(f"phy={phy}")
    rf_prefix = f"{' '.join(rf_bits)} " if rf_bits else ""
    sim = "sim " if last.get("simulation") else ""
    return f"{sim}{rf_prefix}reason={reason} from={src}"
