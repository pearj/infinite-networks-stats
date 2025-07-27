"""Constants for integration_blueprint."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "integration_blueprint"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
CONF_MFA_SHARED_SECRET = "mfa_shared_secret"  # noqa: S105
