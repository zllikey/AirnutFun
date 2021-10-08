"""
Support for Airnut Fun plant sensor.
Developer by billhu
modify by zllikey
10.0.0.10 apn.airnut.com apn2.airnut.com
"""
import logging
import datetime
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    ATTR_TEMPERATURE,
    ATTR_HUMIDITY,
    ATTR_PM25,
    ATTR_BATTERY,
    ATTR_WEATHE,
    ATTR_VOLUME,
    ATTR_TIME,
    MEASUREMENT_UNITE_DICT,
)

CONF_TYPE = "type"
CONF_IP = "ip"
DEFAULT_NAME = 'Airnut Fun'

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_IP): cv.string,
    vol.Required(CONF_TYPE): vol.Any(ATTR_TEMPERATURE, ATTR_HUMIDITY, ATTR_PM25, ATTR_BATTERY,ATTR_WEATHE),
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    if DOMAIN in hass.data:
        server = hass.data[DOMAIN]['server']
        async_add_entities([AirnutSensor(config, server)],True)
     
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    if DOMAIN in hass.data:
        server = hass.data[DOMAIN]['server']
        async_add_entities(
            [AirnutSensor(entry.data, server)], False,
        )
    return True

class AirnutSensor(Entity):
    """Implementing the Airnut 1S sensor."""

    def __init__(self, config, server):
        """Initialize the sensor."""
        _LOGGER.info("AirnutSensor __init__")
        self.config = config
        self._server = server
        self._type = config.get(CONF_TYPE)
        self._ip = config.get(CONF_IP)
        self._name = config.get(CONF_NAME)
        if self._name == DEFAULT_NAME:
            self._name += "_" + self._type
        self._icon = None
        self._state = None
        self._state_attrs = {
            self._type: None,
            ATTR_TIME: None,
        }
#        await self.hass.async_add_executor_job(self.async_update)

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self.config.get("unique_id", None)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state of the sensor."""
        return self._state_attrs
    
    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return MEASUREMENT_UNITE_DICT[self._type]

    async def async_added_to_hass(self):
        """Once the entity is added we should update to get the initial data loaded."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        self.hass.async_add_executor_job(self._server.update)
        try:
            data = self._server.get_data(self._ip)
            self._state = data[self._type]
            self._state_attrs[self._type] = self._state
            self._state_attrs[ATTR_TIME] = data[ATTR_TIME]
        except:
            _LOGGER.info("AirnutSensor get data error with ip %s", self._ip)
            return
