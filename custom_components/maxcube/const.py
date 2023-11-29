
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform

from homeassistant.util.dt import now
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector



DEFAULT_PORT = 62910
CONF_GATEWAYS = "gateways"
DOMAIN = "maxcube"


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
        vol.Required(CONF_SCAN_INTERVAL, default=300): PORT_SELECTOR,
    }
)



CONFIG_GATEWAY = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_SCAN_INTERVAL, default=300): cv.time_period,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_GATEWAYS, default={}): vol.All(
                    cv.ensure_list, [CONFIG_GATEWAY]
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)