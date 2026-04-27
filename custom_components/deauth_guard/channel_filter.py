"""Channel allow-list (empty = all). Simulation bypasses filter by design."""

from __future__ import annotations

import logging
from typing import Any

from .const import KEY_CHANNEL, KEY_INTERFACE

_LOGGER = logging.getLogger(__name__)


def channel_allowed(
    data: dict[str, Any],
    selected_channels: list[int] | None,
    *,
    simulation: bool,
) -> bool:
    """Return True if this event should be processed (history/alert path).

    - Simulation events always pass (user tests with random channels).
    - Empty `selected_channels` = listen on all channels.
    - Otherwise require `channel` in the set; unknown channel: pass through
      and log once at debug (conservative: do not drop unknown).
    """
    if simulation or data.get("simulation"):
        return True
    if not selected_channels:
        return True
    allow = set(int(x) for x in selected_channels)
    ch = data.get(KEY_CHANNEL)
    if ch is None:
        _LOGGER.debug(
            "Deauth event without channel; treating as included (cannot apply channel filter)"
        )
        return True
    try:
        c = int(ch)
    except (TypeError, ValueError):
        return True
    if c in allow:
        return True
    _LOGGER.debug("Ignoring deauth on channel %s (not in selected set %s)", c, sorted(allow))
    return False


def event_passes_radios(
    data: dict[str, Any],
    radios: list[dict[str, Any]],
    *,
    simulation_only: bool,
) -> bool:
    """Apply per-radio channel lists; shared alert rules are unchanged upstream.

    - All-simulation mode: same as `simulation` flag on events (bypass per-radio).
    - One real event: use the matching radio by `KEY_INTERFACE` when present.
    - Unknown interface vs configured list: do not drop (log debug).
    """
    if simulation_only:
        return channel_allowed(data, None, simulation=True)
    if data.get("simulation"):
        return channel_allowed(data, None, simulation=True)
    iface = data.get(KEY_INTERFACE)
    if iface is None:
        return channel_allowed(data, None, simulation=False)
    try:
        siface = str(iface)
    except (TypeError, ValueError):
        return channel_allowed(data, None, simulation=False)
    for row in radios:
        if row.get("interface") == siface:
            ch = row.get("channels") or []
            return channel_allowed(
                data,
                [int(x) for x in ch] if ch else None,
                simulation=False,
            )
    _LOGGER.debug(
        "Event interface %r not in configured radios; not applying channel filter",
        siface,
    )
    return channel_allowed(data, None, simulation=False)
