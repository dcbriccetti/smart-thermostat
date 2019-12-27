'Smart thermostat project main module'

from rpi.sensor import Sensor
from rpi.heaterrelay import HeaterRelay
from thermocontroller import ThermoController

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

controller = ThermoController(Sensor(), HeaterRelay(), diDEFAULT_DESIRED_TEMP)

while True:
    controller.update()
