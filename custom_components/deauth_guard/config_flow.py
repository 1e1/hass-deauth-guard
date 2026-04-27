"""Config flow for Deauth Guard."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    ALL_SELECTABLE_CHANNELS_ORDERED,
    CONF_ALERT_RULES,
    CONF_HISTORY_MAX,
    CONF_RADIO1_CHANNELS,
    CONF_RADIO1_INTERFACE,
    CONF_RADIO2_CHANNELS,
    CONF_RADIO2_INTERFACE,
    CONF_RADIO3_CHANNELS,
    CONF_RADIO3_INTERFACE,
    CONF_RADIOS,
    CONF_SIM_INTERVAL,
    CONF_SIMULATION_MODE,
    DEFAULT_HISTORY_MAX,
    DEFAULT_SIM_INTERVAL,
    DOMAIN,
    HIGHEST_HISTORY_MAX,
    LOWEST_HISTORY_MAX,
    SIMULATION_INTERFACE,
)
from .network import get_candidate_interfaces
from .options_util import build_radios_from_form, form_defaults_from_radios, is_simulation_only, normalize_radios


def _rules_from_form(data: dict[str, Any]) -> list[dict[str, int]]:
    rules: list[dict[str, int]] = []
    for mkey, wkey in (("ar1_min", "ar1_sec"), ("ar2_min", "ar2_sec")):
        try:
            mc = int(data.get(mkey) or 0)
            ws = int(data.get(wkey) or 0)
        except (TypeError, ValueError):
            continue
        if mc >= 1 and ws >= 1:
            rules.append({"min_count": mc, "window_seconds": ws})
    return rules


def _form_from_rules(rules: list[dict[str, Any]] | None) -> dict[str, int]:
    r = rules or []
    o: dict[str, int] = {"ar1_min": 0, "ar1_sec": 0, "ar2_min": 0, "ar2_sec": 0}
    if len(r) > 0:
        o["ar1_min"] = int(r[0].get("min_count", 0))
        o["ar1_sec"] = int(r[0].get("window_seconds", 0))
    if len(r) > 1:
        o["ar2_min"] = int(r[1].get("min_count", 0))
        o["ar2_sec"] = int(r[1].get("window_seconds", 0))
    return o


async def _build_schema(
    hass: Any,
    base: dict[str, Any],
) -> vol.Schema:
    """Form: up to 3 Wi-Fi sources (per-radio channels), shared history & alert rules."""
    names = await hass.async_add_executor_job(get_candidate_interfaces)
    iface_r1: list[dict[str, str]] = [
        {"value": SIMULATION_INTERFACE, "label": "Simulation (no radio)"}
    ]
    for n in names:
        iface_r1.append({"value": n, "label": n})
    opt_extra: list[dict[str, str]] = [
        {"value": "", "label": "—"},
    ]
    for n in names:
        opt_extra.append({"value": n, "label": n})

    ch_options: list[dict[str, str]] = [
        {"value": str(c), "label": f"CH {c}"} for c in ALL_SELECTABLE_CHANNELS_ORDERED
    ]

    def ch_default(k: str) -> list[str]:
        raw_ch: list[Any] = list(base.get(k) or [])
        return [c if isinstance(c, str) else str(int(c)) for c in raw_ch]

    return vol.Schema(
        {
            vol.Required(
                CONF_RADIO1_INTERFACE,
                default=base.get(CONF_RADIO1_INTERFACE, SIMULATION_INTERFACE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=iface_r1,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_RADIO1_CHANNELS, default=ch_default(CONF_RADIO1_CHANNELS)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=ch_options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_RADIO2_INTERFACE,
                default=base.get(CONF_RADIO2_INTERFACE, "") or "",
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=opt_extra,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_RADIO2_CHANNELS, default=ch_default(CONF_RADIO2_CHANNELS)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=ch_options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_RADIO3_INTERFACE,
                default=base.get(CONF_RADIO3_INTERFACE, "") or "",
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=opt_extra,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_RADIO3_CHANNELS, default=ch_default(CONF_RADIO3_CHANNELS)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=ch_options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_SIM_INTERVAL, default=base.get(CONF_SIM_INTERVAL, DEFAULT_SIM_INTERVAL)
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=5, max=86400),
            ),
            vol.Optional(
                CONF_HISTORY_MAX, default=base.get(CONF_HISTORY_MAX, DEFAULT_HISTORY_MAX)
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=LOWEST_HISTORY_MAX, max=HIGHEST_HISTORY_MAX),
            ),
            vol.Optional("ar1_min", default=base.get("ar1_min", 0)): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=10000)
            ),
            vol.Optional("ar1_sec", default=base.get("ar1_sec", 0)): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=86400)
            ),
            vol.Optional("ar2_min", default=base.get("ar2_min", 0)): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=10000)
            ),
            vol.Optional("ar2_sec", default=base.get("ar2_sec", 0)): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=86400)
            ),
        }
    )


def _finalize_options(user_input: dict[str, Any]) -> dict[str, Any]:
    """Build stored options from raw form (radios, channel lists, alert rules)."""
    rules = _rules_from_form(user_input)
    radios = build_radios_from_form(user_input)
    return {
        CONF_RADIOS: radios,
        CONF_SIM_INTERVAL: int(user_input[CONF_SIM_INTERVAL]),
        CONF_HISTORY_MAX: int(user_input[CONF_HISTORY_MAX]),
        CONF_ALERT_RULES: rules,
        CONF_SIMULATION_MODE: is_simulation_only(radios),
    }


class DeauthGuardConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 4

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            options = _finalize_options(user_input)
            return self.async_create_entry(
                title="Deauth Guard",
                data={},
                options=options,
            )

        base = {
            CONF_SIM_INTERVAL: DEFAULT_SIM_INTERVAL,
            CONF_HISTORY_MAX: DEFAULT_HISTORY_MAX,
            **_form_from_rules([]),
            **form_defaults_from_radios(
                [{"interface": SIMULATION_INTERFACE, "channels": []}]
            ),
        }
        return self.async_show_form(
            step_id="user",
            data_schema=await _build_schema(self.hass, base),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowWithConfigEntry:
        return DeauthGuardOptionsFlow(config_entry)


class DeauthGuardOptionsFlow(OptionsFlowWithConfigEntry):
    """Options: interface, channels, rules, history, sim interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(data=_finalize_options(user_input))

        opt = self.config_entry.options
        r_norm = normalize_radios(opt)
        base = {
            CONF_SIM_INTERVAL: opt.get(CONF_SIM_INTERVAL, DEFAULT_SIM_INTERVAL),
            CONF_HISTORY_MAX: opt.get(CONF_HISTORY_MAX, DEFAULT_HISTORY_MAX),
            **_form_from_rules(opt.get(CONF_ALERT_RULES)),
            **form_defaults_from_radios(r_norm),
        }
        return self.async_show_form(
            step_id="init",
            data_schema=await _build_schema(self.hass, base),
        )
