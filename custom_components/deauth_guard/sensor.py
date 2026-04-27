"""Sensor platform: last detection summary."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_LAST_EVENT
from .coordinator import DeauthGuardCoordinator
from .last_event_text import last_event_summary


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: DeauthGuardCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    desc = SensorEntityDescription(
        key=SENSOR_LAST_EVENT,
        name="Last deauth event",
        translation_key="last_event",
    )
    async_add_entities(
        [DeauthLastEventSensor(entry, coordinator, desc)],
        update_before_add=False,
    )


class DeauthLastEventSensor(
    CoordinatorEntity[DeauthGuardCoordinator], SensorEntity
):
    """Human-readable summary of the most recent stored detection."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: DeauthGuardCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="Deauth Guard",
            manufacturer="Deauth Guard",
        )
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        if not data or not data.get("last"):
            return None
        return last_event_summary(data["last"])

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        data = self.coordinator.data
        if not data:
            return {}
        return {
            "last_raw": data.get("last"),
            "total_recorded_session": data.get("total_recorded_session", 0),
        }
