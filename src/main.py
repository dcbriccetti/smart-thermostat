from cpx.sensor import Sensor
from cpx.timingknob import TimingKnob
from cpx.heaterrelay import HeaterRelay
from cpx.buttons import Buttons
from cpx.display import Display
from tempmgr import TempMgr

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0
BUTTON_REPEAT_DELAY_SECS = 0.3


def state_change_listener(current_temp, desired_temp):
    display.show_temp_difference(current_temp, desired_temp, TEMP_CHANGE_INCREMENT)


def button_push_listener(button_index):
    sign = (-1, 1)[button_index]
    temp_mgr.change_desired_temp(sign * TEMP_CHANGE_INCREMENT)


buttons = Buttons(BUTTON_REPEAT_DELAY_SECS)
buttons.add_push_listener(button_push_listener)
display = Display()
temp_mgr = TempMgr(Sensor(), TimingKnob(), HeaterRelay(), display, DEFAULT_DESIRED_TEMP)
temp_mgr.add_state_change_listener(state_change_listener)

while True:
    temp_mgr.update()
    buttons.update()
    display.update()
