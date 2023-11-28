"""Support for MAX! sensors via MAX! Cube."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import Entity
from homeassistant.const import TEMP_CELSIUS

from . import DATA_KEY

UNIT_OF_MEASUREMENT_VALVE = "%"

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Iterate through all MAX! Devices and add window shutters."""
    devices: list[MaxCubeSensorBase] = []
    for handler in hass.data[DATA_KEY].values():
        for device in handler.cube.devices:
            if device.is_thermostat():
                devices.append(MaxCubeValveSensor(handler, device))
            if device.is_wallthermostat():
                devices.append(MaxCubeTemperature(handler, device))

    add_entities(devices)


class MaxCubeSensorBase(Entity):
    """Base class for maxcube sensors."""

#    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, handler, device):
        """Initialize MAX! Cube Sensor Entity."""
        self._cubehandle = handler
        self._device = device
#        self._attr_room = handler.cube.room_by_id(device.room_id)
#        self._state = None

    def update(self) -> None:
        """Get latest data from MAX! Cube."""
        self._cubehandle.update()


class MaxCubeValveSensor(MaxCubeSensorBase):
    """Representation of a MAX! Cube Sensor device."""

    _attr_device_class = SensorDeviceClass.POWER_FACTOR

    def __init__(self, handler, device):
        """Initialize MAX! Cube SensorEntity."""
        super().__init__(handler, device)
        self._unit_of_measurement = UNIT_OF_MEASUREMENT_VALVE
        self._attr_name = f"{self._device.name} Valve"
        self._attr_unique_id = f"{self._device.serial}_valve"

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        """Return saved state."""
        return self._device.valve_position

#    def update(self):
#        """Get latest data from MAX! Cube."""
#        self._cubehandle.update()
#        device = self._cubehandle.cube.device_by_rf(self._rf_address)
#        self._state = device.valve_position

class MaxCubeTemperature(MaxCubeSensorBase):
    """Representation of a MAX! Cube Sensor device."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, handler, device):
        """Initialize MAX! Cube SensorEntity."""
        super().__init__(handler, device)

        self._attr_name = f"{self._device.name} Temperature"
        self._attr_unique_id = f"{self._device.serial}_temperature"
        self._unit_of_measurement = TEMP_CELSIUS

    @property
    def state(self):
        """Return the current temperature."""
        return self._device.actual_temperature
