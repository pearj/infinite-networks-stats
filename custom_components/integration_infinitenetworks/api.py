"""Sample API Client."""

from __future__ import annotations

import socket
from datetime import datetime
from typing import Any, TypedDict

import aiohttp
import async_timeout
from attr import dataclass

from custom_components.integration_infinitenetworks.const import LOGGER


class InfinteHmac(TypedDict):
    """Represents an Infinite Networks HMAC."""

    expires: str
    user: str
    hmac: str
    expires_date: datetime


@dataclass
class InfiniteService:
    """Represents an Infinite Networks Service."""

    identifier: str
    id: int


class InfinteNetworksApiClientError(Exception):
    """Exception to indicate a general API error."""


class InfinteNetworksApiClientCommunicationError(
    InfinteNetworksApiClientError,
):
    """Exception to indicate a communication error."""


class InfinteNetworksApiClientAuthenticationError(
    InfinteNetworksApiClientError,
):
    """Exception to indicate an authentication error."""


UNAUTHORIZED_STATUS = 401
FORBIDDEN_STATUS = 403
AUTH_ERROR_STATUS_CODES = (UNAUTHORIZED_STATUS, FORBIDDEN_STATUS)


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in AUTH_ERROR_STATUS_CODES:
        msg = "Invalid credentials"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def _verify_sso_auth_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status == UNAUTHORIZED_STATUS:
        msg = "Invalid credentials"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


async def _extract_access_token(response: aiohttp.ClientResponse) -> str:
    data = await response.json()  # Ensure the response is JSON
    if "access_token" in data:
        return data["access_token"]

    msg = f"Unable to extract access_token from {response.real_url}"
    raise InfinteNetworksApiClientAuthenticationError(
        msg,
    )


def _extract_hmac(json: dict) -> InfinteHmac:
    if "hmac" in json:
        hmac: InfinteHmac = json["hmac"]
        hmac["expires_date"] = datetime.fromisoformat(json["hmac"]["expires"])
        return hmac

    msg = f"hmac missing from me url, json output {json}"
    raise InfinteNetworksApiClientAuthenticationError(
        msg,
    )


class InfinteNetworksApiClient:
    """Sample API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session
        self._hmac: InfinteHmac | None = None
        self._client_id: int | None = None

    @property
    def hmac(self) -> InfinteHmac:
        """Return the hmac."""
        if self._hmac:
            return self._hmac
        msg = "hmac missing"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )

    @property
    def client_id(self) -> int:
        """Return the client ID."""
        if self._client_id:
            return self._client_id
        msg = "client id missing"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )

    async def async_get_service(self) -> InfiniteService:
        """Get the first service from the API."""
        if not self._client_id:
            await self._refresh_hmac_and_client()

        async with async_timeout.timeout(10):
            json = await self._api_wrapper(
                method="get",
                url=f"https://portal.infinite.net.au/iv/api/incontrol/client/{self.client_id}/services",
            )

            return InfiniteService(
                identifier=json["services"][0]["identifier"],
                id=json["services"][0]["id"],
            )

    async def async_get_vision_details(self, infinite_service: InfiniteService) -> Any:
        """Get Vision details from the API, including things like sync speed, etc."""
        if not self._client_id:
            await self._refresh_hmac_and_client()

        async with async_timeout.timeout(30):
            detail_url = f"https://portal.infinite.net.au/iv/api/vision/service/{infinite_service.id}/details"
            LOGGER.debug("Fetching Vision connection details from %s", detail_url)
            return await self._api_wrapper(
                method="get",
                url=detail_url,
            )

    async def _refresh_hmac_and_client(self) -> None:
        self._hmac, self._client_id = await self._fetch_hmac_and_client()

    async def _fetch_hmac_and_client(self) -> tuple[InfinteHmac, int]:
        async with async_timeout.timeout(10):
            response = await self._session.post(
                url="https://portal.infinite.net.au/sso/api/login/1",
                json={"username": self._username, "password": self._password},
            )

            _verify_sso_auth_response_or_raise(response)

            access_token = await _extract_access_token(response)

            response = await self._session.get(
                url="https://portal.infinite.net.au/sso/api/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            json = await response.json()
            hmac = _extract_hmac(json)

            client_id = json["clients"][0]["id"]
            return (hmac, client_id)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            if not (
                self._hmac
                and self._hmac["expires_date"]
                > datetime.now(self._hmac["expires_date"].tzinfo)
            ):
                await self._refresh_hmac_and_client()
            headers = headers or {}
            hmac = self.hmac
            headers["Authorization"] = f"HMAC {hmac['user']}:{hmac['hmac']}"
            headers["X-Hmac-Expires"] = hmac["expires"]

            response = await self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
            )
            _verify_response_or_raise(response)
            return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise InfinteNetworksApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise InfinteNetworksApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise InfinteNetworksApiClientError(
                msg,
            ) from exception
