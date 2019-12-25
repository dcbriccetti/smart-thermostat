'Smart thermostat project main module'

from cpx.sensor import Sensor
from cpx.timingknob import TimingKnob
from cpx.heaterrelay import HeaterRelay
from cpx.buttons import Buttons
from cpx.display import Display
from thermocontroller import ThermoController

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3

buttons = Buttons(BUTTON_REPEAT_DELAY_SECS)
buttons.on_change(
    lambda button_index:
    controller.change_desired_temp((-1, 1)[button_index] * TEMP_CHANGE_INCREMENT))

display = Display(TEMP_CHANGE_INCREMENT)

controller = ThermoController(
    Sensor(), TimingKnob(), HeaterRelay(), display, DEFAULT_DESIRED_TEMP)

while True:
    controller.update()
    buttons.update()
    display.update()
