"""Platform for sensor integration."""
from __future__ import annotations
import requests
import time


from homeassistant.components.water_heater import (
    PLATFORM_SCHEMA,
    WaterHeaterEntity,
    SUPPORT_OPERATION_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    STATE_GAS,
    ATTR_OPERATION_LIST,
    ATTR_OPERATION_MODE,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import CONF_HOST, ATTR_TEMPERATURE

from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from . import DOMAIN

SCAN_INTERVAL = timedelta(seconds=10)


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
    """Set up the water heater platform."""
    # host = config[CONF_HOST]
    hass.data[DOMAIN] = {"host": config[CONF_HOST]}
    add_entities([RheemWaterHeater()])


class RheemWaterHeater(WaterHeaterEntity):
    """Representation of a Water heater."""

    def __init__(self):
        """Initialize the wate heater."""
        self._support_features = SUPPORT_TARGET_TEMPERATURE
        self._min_temp = 37
        self._max_temp = 50
        self._temperature_unit = TEMP_CELSIUS
        self._target_temp = None
        self._current_temp = None
        self._state = STATE_GAS
        self._state_attrs = {}

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "rheem_eziset"

    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return "1337_yolo"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def current_operation(self):
        """Return the state of the sensor."""
        return STATE_GAS

    @property
    def supported_features(self):
        """Return the Supported features of the water heater."""
        return self._support_features

    @property
    def min_temp(self):
        """Return the minimum temperature that can be set."""
        return self._min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature that can be set."""
        return self._max_temp

    @property
    def current_temperature(self):
        """Return the current temperature ."""
        return self._current_temp

    @property
    def target_temperature(self):
        """Return the target temperature ."""
        return self._target_temp

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        url = "http://" + self.hass.data[DOMAIN]["host"] + "/getInfo.cgi"
        temp = requests.get(url=url).json()["temp"]
        self._target_temp = temp
        self._current_temp = temp

    def set_temperature(self, **kwargs):
        set_temp = int(kwargs[ATTR_TEMPERATURE])
        ip = self.hass.data[DOMAIN]["host"]
        sid = requests.get(url="http://" + ip + "/ctrl.cgi?sid=0&heatingCtrl=1").json()[
            "sid"
        ]
        requests.get(
            url="http://"
            + ip
            + "/set.cgi?sid="
            + str(sid)
            + "&setTemp="
            + str(set_temp)
        )
        "API seems to need a wait here before the session is ended, otherwise new temperature is not applied."
        time.sleep(0.2)
        requests.get(
            url="http://" + ip + "/ctrl.cgi?sid=" + str(sid) + "&heatingCtrl=0"
        )
