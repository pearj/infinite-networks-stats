"""DataUpdateCoordinator for integration_infinitenetworks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    InfinteNetworksApiClientAuthenticationError,
    InfinteNetworksApiClientError,
)

if TYPE_CHECKING:
    from .data import InfinteNetworksConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class InfinteNetworksDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: InfinteNetworksConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_service()
        except InfinteNetworksApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except InfinteNetworksApiClientError as exception:
            raise UpdateFailed(exception) from exception
