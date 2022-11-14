""" Constants """
# Base component constants
DOMAIN = "airnut"
VERSION = "1.0.1"
ISSUE_URL = "https://github.com/billhu1996/Airnut/issues"
ISSUE_URL2 = "https://github.com/zllikey/AirnutFun/issues"
ATTRIBUTION = ""

# Configuration
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_PM25 = "pm25"
ATTR_BATTERY = "battery"
ATTR_VOLUME = "volume"
ATTR_TIME = "time"
ATTR_WEATHE = "weathe"

#Unit
MEASUREMENT_UNITE_DICT = {
    ATTR_TEMPERATURE: "°C",
    ATTR_HUMIDITY: "%",
    ATTR_PM25: "μg/m³",
    ATTR_BATTERY: "%",
    ATTR_WEATHE: None
}

# Defaults
DEFAULT_SCAN_INTERVAL = 600
