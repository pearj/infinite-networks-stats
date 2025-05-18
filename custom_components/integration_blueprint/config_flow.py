"""Adds config flow for InfinteNetworks."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    InfinteNetworksApiClient,
    InfinteNetworksApiClientAuthenticationError,
    InfinteNetworksApiClientCommunicationError,
    InfinteNetworksApiClientError,
    InfinteNetworksApiClientMfaError,
)
from .const import CONF_MFA_SHARED_SECRET, DOMAIN, LOGGER


class InfinteNetworksFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for InfinteNetworks."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    mfa_shared_secret=user_input[CONF_MFA_SHARED_SECRET],
                )
            except InfinteNetworksApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except InfinteNetworksApiClientMfaError as exception:
                LOGGER.error(exception)
                _errors["base"] = "mfa"
            except InfinteNetworksApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except InfinteNetworksApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_USERNAME])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Required(CONF_MFA_SHARED_SECRET): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(
        self, username: str, password: str, mfa_shared_secret: str
    ) -> None:
        """Validate credentials."""
        client = InfinteNetworksApiClient(
            username=username,
            password=password,
            mfa_shared_secret=mfa_shared_secret,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
