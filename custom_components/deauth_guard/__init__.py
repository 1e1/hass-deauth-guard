"""Deauth Guard — 802.11 deauthentication awareness for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_ALERT_RULES,
    CONF_CHANNELS,
    CONF_HISTORY_MAX,
    CONF_INTERFACE,
    CONF_RADIOS,
    CONF_SIMULATION_MODE,
    DEFAULT_HISTORY_MAX,
    DOMAIN,
    PLATFORMS,
    SERVICE_CLEAR_HISTORY,
    SERVICE_GET_HISTORY,
    SIMULATION_INTERFACE,
)
from .coordinator import DeauthGuardCoordinator
from .history import DeauthHistoryStore
from .network import get_candidate_interfaces

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema()
SERVICE_GET_HISTORY_SCHEMA = vol.Schema({})
SERVICE_CLEAR_HISTORY_SCHEMA = vol.Schema({})


def _get_coordinator_or_raise(hass: HomeAssistant) -> DeauthGuardCoordinator:
    if DOMAIN not in hass.data:
        msg = f"{DOMAIN} not loaded"
        raise vol.Invalid(msg)
    for key, payload in hass.data[DOMAIN].items():
        if key == "_services":
            continue
        if isinstance(payload, dict) and (coord := payload.get("coordinator")):
            return coord
    msg = f"No {DOMAIN} config entry with coordinator"
    raise vol.Invalid(msg)


def _register_services_if_needed(hass: HomeAssistant) -> None:
    if hass.data[DOMAIN].get("_services"):
        return

    async def handle_get_history(_call: ServiceCall) -> dict[str, Any]:
        coord = _get_coordinator_or_raise(hass)
        return {"entries": coord.history.as_list()}

    async def handle_clear_history(_call: ServiceCall) -> None:
        coord = _get_coordinator_or_raise(hass)
        await coord.history.async_clear()
        coord.async_set_updated_data(
            {
                "last": None,
                "total_recorded_session": 0,
            }
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_HISTORY,
        handle_get_history,
        schema=SERVICE_GET_HISTORY_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_HISTORY,
        handle_clear_history,
        schema=SERVICE_CLEAR_HISTORY_SCHEMA,
    )
    hass.data[DOMAIN]["_services"] = True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ver = entry.version
    current = hass.config_entries.async_get_entry(entry.entry_id) or entry
    opts = dict(current.options)

    if ver < 2:
        if CONF_INTERFACE not in opts:
            if opts.get(CONF_SIMULATION_MODE, True):
                opts[CONF_INTERFACE] = SIMULATION_INTERFACE
            else:
                nifs = await hass.async_add_executor_job(get_candidate_interfaces)
                opts[CONF_INTERFACE] = nifs[0] if nifs else SIMULATION_INTERFACE
        if CONF_CHANNELS not in opts:
            opts[CONF_CHANNELS] = []
        if CONF_ALERT_RULES not in opts:
            opts[CONF_ALERT_RULES] = []
        opts[CONF_SIMULATION_MODE] = (
            opts.get(CONF_INTERFACE, SIMULATION_INTERFACE) == SIMULATION_INTERFACE
        )
        ver = 2
        hass.config_entries.async_update_entry(entry, options=opts, version=2)
        current = hass.config_entries.async_get_entry(entry.entry_id) or entry
        opts = dict(current.options)

    if ver < 3:
        if not opts.get(CONF_RADIOS):
            opts[CONF_RADIOS] = [
                {
                    "interface": str(
                        opts.get(CONF_INTERFACE, SIMULATION_INTERFACE)
                    ),
                    "channels": list(opts.get(CONF_CHANNELS) or []),
                }
            ]
        hass.config_entries.async_update_entry(entry, options=opts, version=3)

    if ver < 4:
        en = hass.config_entries.async_get_entry(entry.entry_id) or entry
        opts4 = dict(en.options)
        opts4.pop(CONF_INTERFACE, None)
        opts4.pop(CONF_CHANNELS, None)
        hass.config_entries.async_update_entry(entry, options=opts4, version=4)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    max_entries = int(
        entry.options.get(CONF_HISTORY_MAX, DEFAULT_HISTORY_MAX)
    )
    history = DeauthHistoryStore(hass, max_entries=max_entries)
    await history.async_load()
    options = dict(entry.options)
    coordinator = DeauthGuardCoordinator(
        hass,
        history=history,
        options=options,
    )
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_start_sources()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "history": history,
    }
    _register_services_if_needed(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    return True


async def _async_update_options(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    payload = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if isinstance(payload, dict) and (coord := payload.get("coordinator")):
        await coord.async_stop_sources()
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
