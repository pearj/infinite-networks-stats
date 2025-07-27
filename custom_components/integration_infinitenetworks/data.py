"""Custom types for integration_infinitenetworks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import InfinteNetworksApiClient
    from .coordinator import InfinteNetworksDataUpdateCoordinator


type InfinteNetworksConfigEntry = ConfigEntry[InfinteNetworksData]


@dataclass
class InfinteNetworksData:
    """Data for the InfinteNetworks integration."""

    client: InfinteNetworksApiClient
    coordinator: InfinteNetworksDataUpdateCoordinator
    integration: Integration
