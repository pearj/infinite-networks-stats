"""Sample API Client."""

from __future__ import annotations

import socket
from datetime import datetime
import token
from typing import Any, Tuple, TypedDict
from urllib.parse import parse_qs

import aiohttp
import async_timeout
import pyotp
from selectolax.parser import HTMLParser

from custom_components.integration_blueprint.const import LOGGER


class InfinteHmac(TypedDict):
    expires: str
    user: str
    hmac: str
    expires_date: datetime


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


class InfinteNetworksApiClientMfaError(
    InfinteNetworksApiClientError,
):
    """Exception to indicate the MFA shared secret is wrong."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def _verify_sso_auth_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.url.path not in {"/", "/authenticate"}:
        msg = "Invalid credentials"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def _extract_access_token(response: aiohttp.ClientResponse) -> str:
    if response.real_url.fragment:
        querystring = parse_qs(response.real_url.fragment)
        if "access_token" in querystring:
            return querystring["access_token"][0]

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
        mfa_shared_secret: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._mfa_shared_secret = mfa_shared_secret
        self._session = session
        self._hmac: InfinteHmac | None = None
        self._client_id: int | None = None

    @property
    def hmac(self) -> InfinteHmac:
        if self._hmac:
            return self._hmac
        msg = "hmac missing"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )

    @property
    def client_id(self) -> int:
        if self._client_id:
            return self._client_id
        msg = "client id missing"
        raise InfinteNetworksApiClientAuthenticationError(
            msg,
        )

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        if not self._client_id:
            await self._refresh_hmac_and_client()
        json = await self._api_wrapper(
            method="get",
            url=f"https://invocation.infinite.net.au/api/incontrol/client/{self.client_id}/services",
        )

        return json["services"][0]["identifier"]

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _refresh_hmac_and_client(self) -> None:
        self._hmac, self._client_id = await self._fetch_hmac_and_client()

    async def _fetch_hmac_and_client(self) -> tuple[InfinteHmac, int]:
        async with async_timeout.timeout(10):
            data = aiohttp.FormData()
            data.add_field("_username", self._username)
            data.add_field("_password", self._password)
            response = await self._session.post(
                url="https://sso.infinite.net.au/login",
                data=data,
            )

            _verify_sso_auth_response_or_raise(response)

            if response.url.path == "/authenticate":
                # Time to do MFA
                mfa = pyotp.TOTP(self._mfa_shared_secret)
                mfa_code = mfa.now()

                # Grab the two factor token from the response
                html_text = await response.text()
                tree = HTMLParser(html=html_text)
                token_elem = tree.css_first("input#two_factor_register__token")
                if token_elem:
                    token = token_elem.attributes["value"]
                else:
                    msg = "Unable to find two factor token in MFA form"
                    raise InfinteNetworksApiClientMfaError(
                        msg,
                    )

                data = aiohttp.FormData()
                data.add_field("two_factor_register[code]", mfa_code)
                data.add_field("two_factor_register[_token]", token)
                # Hopefully can remove this in the future, as this is not a
                # good implementation on their side
                data.add_field("two_factor_register[secret]", self._mfa_shared_secret)

                response = await self._session.post(
                    url="https://sso.infinite.net.au/authenticate",
                    data=data,
                )

                if response.url.path != "/":
                    # We are not authenticated
                    msg = "Unable to authenticate with MFA"
                    raise InfinteNetworksApiClientMfaError(
                        msg,
                    )

                response.raise_for_status()

                # MFA is done, we should be authenticated now

            response = await self._session.get(
                url="https://sso.infinite.net.au/leave/1"
            )

            access_token = _extract_access_token(response)

            response = await self._session.get(
                url="https://sso.infinite.net.au/api/me",
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
            async with async_timeout.timeout(10):
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
