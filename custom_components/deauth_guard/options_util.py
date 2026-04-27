"""Normalize config entry options (`CONF_RADIOS`)."""

from __future__ import annotations

from typing import Any

from .const import (
    CONF_RADIOS,
    CONF_RADIO1_CHANNELS,
    CONF_RADIO1_INTERFACE,
    CONF_RADIO2_CHANNELS,
    CONF_RADIO2_INTERFACE,
    CONF_RADIO3_CHANNELS,
    CONF_RADIO3_INTERFACE,
    SIMULATION_INTERFACE,
)


def _coerce_channels(value: Any) -> list[int]:
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        out: list[int] = []
        for x in value:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                continue
        return out
    return []


def normalize_radios(options: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of `{"interface": str, "channels": list[int]}`."""
    raw = options.get(CONF_RADIOS)
    if isinstance(raw, list) and raw:
        out: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            try:
                iface = str(item.get("interface", "")).strip()
            except (TypeError, ValueError):
                continue
            if not iface:
                continue
            out.append(
                {
                    "interface": iface,
                    "channels": _coerce_channels(item.get("channels")),
                }
            )
        if out:
            return out
    return [{"interface": SIMULATION_INTERFACE, "channels": []}]


def is_simulation_only(radios: list[dict[str, Any]]) -> bool:
    return bool(
        len(radios) == 1
        and radios[0].get("interface") == SIMULATION_INTERFACE
    )


def build_radios_from_form(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build `CONF_RADIOS` from config-flow keys `radio1_*` … `radio3_*`."""
    r1 = str((data.get(CONF_RADIO1_INTERFACE) or "")).strip()
    if not r1:
        r1 = SIMULATION_INTERFACE
    ch1 = _coerce_channels(data.get(CONF_RADIO1_CHANNELS))
    out: list[dict[str, Any]] = [{"interface": r1, "channels": ch1}]
    if r1 == SIMULATION_INTERFACE:
        return out
    ifaces: set[str] = {r1}
    ro: list[tuple[str, str]] = [
        (CONF_RADIO2_INTERFACE, CONF_RADIO2_CHANNELS),
        (CONF_RADIO3_INTERFACE, CONF_RADIO3_CHANNELS),
    ]
    for k_if, k_ch in ro:
        raw_if = (data.get(k_if) or "")
        sif = str(raw_if).strip()
        if not sif or sif == SIMULATION_INTERFACE:
            continue
        if sif in ifaces:
            continue
        ifaces.add(sif)
        ch = _coerce_channels(data.get(k_ch))
        out.append({"interface": sif, "channels": ch})
    return out


def form_defaults_from_radios(radios: list[dict[str, Any]]) -> dict[str, Any]:
    """Map stored radios (max 3) to form `radio*` fields."""
    r = radios if radios else [
        {"interface": SIMULATION_INTERFACE, "channels": []}
    ]
    def _row(i: int) -> tuple[str, list[int]]:
        if i < len(r) and isinstance(r[i], dict):
            iface = str(r[i].get("interface", "") or "")
            if not iface:
                iface = SIMULATION_INTERFACE
            ch = _coerce_channels(r[i].get("channels"))
            return iface, ch
        return "", []

    a0, c0 = _row(0)
    a1, c1 = _row(1)
    a2, c2 = _row(2)
    return {
        CONF_RADIO1_INTERFACE: a0,
        CONF_RADIO1_CHANNELS: c0,
        CONF_RADIO2_INTERFACE: a1,
        CONF_RADIO2_CHANNELS: c1,
        CONF_RADIO3_INTERFACE: a2,
        CONF_RADIO3_CHANNELS: c2,
    }
