"""Config flow for eQ-3 MaxCube integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from .const import *

from socket import timeout
from typing import Any
from .maxcube_api.cube import MaxCube

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.util.dt import now
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

DOMAIN = "maxcube"
DATA_KEY = "maxcube"
_LOGGER = logging.getLogger(__name__)

PORT_SELECTOR = vol.All(
    selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1, step=1, max=65535, mode=selector.NumberSelectorMode.BOX
        )
    ),
    vol.Coerce(int),
)

SCAN_SELECTOR = vol.All(
    selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=5, step=1, max=3000, mode=selector.NumberSelectorMode.BOX
        )
    ),
    vol.Coerce(int),
)

STEP_CUBEGW_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): selector.TextSelector(),
        vol.Required(CONF_PORT, default=62910): PORT_SELECTOR,
        vol.Required(CONF_SCAN_INTERVAL, default=300): SCAN_SELECTOR,
    }
)



class FieldError(Exception):
    """Field with invalid data."""

    def __init__(self, message: str, field: str, error: str) -> None:
        """Set up error."""
        super().__init__(message)
        self.field = field
        self.error = error

async def validate_user_input(hass: HomeAssistant, data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    scan_interval = data[CONF_SCAN_INTERVAL]
    try:
        cube = MaxCube(host, port, now=now)
#            hass.data[DOMAIN][host] = MaxCubeHandle(cube, scan_interval)
    except timeout as ex:
        _LOGGER.error("Unable to connect to Max!Cube gateway: %s", str(ex))
        raise FieldError("Unable to connect to Max!Cube gateway: %s", CONF_HOST, "address") from ex

    return f"MaxCube at {data[CONF_HOST]}", {
        **data,
        CONF_HOST: host,
        CONF_PORT: port,
        CONF_SCAN_INTERVAL: scan_interval
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nibe Heat Pump."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user config input step."""
        errors = {}
        if user_input is not None:
            try:
                title, data = await validate_user_input(self.hass, user_input)
            except FieldError as exception:
                _LOGGER.exception("Validation error")
                errors[exception.field] = exception.error
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown:" + Exception
            else:
                return self.async_create_entry(title=title, data=data)        
        return self.async_show_form(
            step_id="user", data_schema=STEP_CUBEGW_DATA_SCHEMA, errors=errors
        )

        
