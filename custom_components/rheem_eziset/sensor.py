"""Platform for sensor integration."""
from __future__ import annotations
import requests


from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST

from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from . import DOMAIN

SCAN_INTERVAL = timedelta(seconds=5)


# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # host = config[CONF_HOST]
    hass.data[DOMAIN] = {"host": config[CONF_HOST]}
    add_entities([WaterTempSensor()])


class WaterTempSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Hot Water Temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        url = "http://" + self.hass.data[DOMAIN]["host"] + "/getInfo.cgi"
        self._state = requests.get(url=url).json()["temp"]
