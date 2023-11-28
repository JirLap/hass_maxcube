"""Config flow for eQ-3 MaxCube integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
        vol.Required(CONF_IP_ADDRESS): selector.TextSelector(),
        vol.Required(CONF_LISTENING_PORT, default=62910): PORT_SELECTOR,
        vol.Required(CONF_SCAN_INTERVAL, default=300): PORT_SELECTOR,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nibe Heat Pump."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        return self.async_show_form(
            step_id="modbus", data_schema=STEP_MODBUS_DATA_SCHEMA, errors=errors
        )

        host = gateway[CONF_HOST]
        port = gateway[CONF_PORT]
        scan_interval = gateway[CONF_SCAN_INTERVAL].total_seconds()

        try:
            cube = MaxCube(host, port, now=now)
