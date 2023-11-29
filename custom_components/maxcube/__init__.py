"""Support for the MAX! Cube LAN Gateway."""
from __future__ import annotations
import logging
import time
import voluptuous as vol

from typing import Any

from socket import timeout
from threading import Lock

from .const import *
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.const import Platform
from homeassistant.helpers.discovery import load_platform
from homeassistant.components import persistent_notification
from homeassistant.util.dt import now
from homeassistant.helpers.typing import ConfigType

from maxcube.cube import MaxCube

_LOGGER = logging.getLogger(__name__)
DOMAIN = "maxcube"
DATA_KEY = "maxcube"
CONF_GATEWAYS = "gateways"
NOTIFICATION_ID = "maxcube_notification"
NOTIFICATION_TITLE = "Max!Cube gateway setup"

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up Nibe Heat Pump from a config entry."""
    host = config.data[CONF_HOST]
    port = config.data[CONF_PORT]
    scan_interval = config.data[CONF_SCAN_INTERVAL]

    if DATA_KEY not in hass.data:
      hass.data[DATA_KEY] = {}

    try:
        cube = MaxCube(host, port, now=now)
        hass.data[DATA_KEY][host] = MaxCubeHandle(cube, scan_interval)
    except timeout as ex:
        _LOGGER.error("Unable to connect to Max!Cube gateway: %s", str(ex))
        return False

    load_platform(hass, Platform.CLIMATE, DOMAIN, {}, config)
#    load_platform(hass, Platform.BINARY_SENSOR, DOMAIN, {}, config)
    load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
    return True

# def setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Establish connection to MAX! Cube."""

#     if DATA_KEY not in hass.data:
#         hass.data[DATA_KEY] = {}

#     connection_failed = 0
#     gateways = config[DOMAIN][CONF_GATEWAYS]
#     for gateway in gateways:
#         host = gateway[CONF_HOST]
#         port = gateway[CONF_PORT]
#         scan_interval = gateway[CONF_SCAN_INTERVAL]

#         try:
#             cube = MaxCube(host, port, now=now)
#             hass.data[DATA_KEY][host] = MaxCubeHandle(cube, scan_interval)
#         except timeout as ex:
#             _LOGGER.error("Unable to connect to Max!Cube gateway: %s", str(ex))
#             persistent_notification.create(
#                 hass,
#                 (
#                     f"Error: {ex}<br />You will need to restart Home Assistant after"
#                     " fixing."
#                 ),
#                 title=NOTIFICATION_TITLE,
#                 notification_id=NOTIFICATION_ID,
#             )
#             connection_failed += 1

#     if connection_failed >= len(gateways):
#         return False

#     load_platform(hass, Platform.CLIMATE, DOMAIN, {}, config)
#     load_platform(hass, Platform.BINARY_SENSOR, DOMAIN, {}, config)
#     load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)

#     return True


class MaxCubeHandle:
    """Keep the cube instance in one place and centralize the update."""

    def __init__(self, cube, scan_interval):
        """Initialize the Cube Handle."""
        self.cube = cube
        self.cube.use_persistent_connection = scan_interval <= 300  # seconds
        self.scan_interval = scan_interval
        self.mutex = Lock()
        self._updatets = time.monotonic()

    def update(self):
        """Pull the latest data from the MAX! Cube."""
        # Acquire mutex to prevent simultaneous update from multiple threads
        with self.mutex:
            # Only update every update_interval
            if (time.monotonic() - self._updatets) >= self.scan_interval:
                _LOGGER.debug("Updating")

                try:
                    self.cube.update()
                except timeout:
                    _LOGGER.error("Max!Cube connection failed")
                    return False

                self._updatets = time.monotonic()
            else:
                _LOGGER.debug("Skipping update")

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   """Unload a config entry."""
   if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
       hass.data[DATA_KEY].pop(entry.entry_id)

   return unload_ok