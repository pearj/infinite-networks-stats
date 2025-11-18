"""Sensor platform for integration_infinitenetworks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfDataRate

from .entity import InfinteNetworksEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InfinteNetworksDataUpdateCoordinator
    from .data import InfinteNetworksConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="service_state",  #: "Up",
        name="Service state",
    ),
    SensorEntityDescription(
        key="last_status_change",  #: "2025-06-19T12:44:32.000+00:00",
        name="Last status change",
    ),
    SensorEntityDescription(
        key="router_cpe_mac",  #: "60:22:32:9c:4e:20",
        name="Router CPE MAC",
    ),
    SensorEntityDescription(
        key="ntu_cpe_mac",  #: "Not Found",
        name="NTU CPE MAC",
    ),
    SensorEntityDescription(
        key="ntu_cpe_make",  #: "ZYXE",
        name="NTU CPE Make",
    ),
    SensorEntityDescription(
        key="ntu_cpe_model",  #: "4100B0",
        name="NTU CPE Model",
    ),
    SensorEntityDescription(
        key="ntu_cpe_serial",  #: "S230Y28123901",
        name="NTU CPE Serial",
    ),
    SensorEntityDescription(
        key="ntu_cpe_firmware",  #: "ACCL0b8_D0",
        name="NTU CPE Firmware",
    ),
    SensorEntityDescription(
        key="actual_line_rate_up",  #: 95351,
        name="Actual line rate up",
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
    ),
    SensorEntityDescription(
        key="attainable_line_rate_up",  #: 98071,
        name="Attainable line rate up",
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
    ),
    SensorEntityDescription(
        key="actual_line_rate_down",  #: 764172,
        name="Actual line rate down",
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
    ),
    SensorEntityDescription(
        key="attainable_line_rate_down",  #: 765685,
        name="Attainable line rate down",
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: InfinteNetworksConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        InfinteNetworksSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class InfinteNetworksSensor(InfinteNetworksEntity, SensorEntity):
    """integration_infinitenetworks Sensor class."""

    def __init__(
        self,
        coordinator: InfinteNetworksDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        if self._attr_unique_id and entity_description.key:
            self._attr_unique_id += f"_{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.data.get("details").get(self.entity_description.key)  # pyright: ignore[reportOptionalMemberAccess]
