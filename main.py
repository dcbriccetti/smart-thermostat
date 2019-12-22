from time import monotonic, sleep
from board import BUTTON_A, BUTTON_B, A5, A6
from digitalio import DigitalInOut, Pull
from tempsensor import TempSensor
from heaterrelay import HeaterRelay
from buttons import Buttons
from display import Display
from tempmgr import TempMgr

TEMP_CHANGE_INCREMENT = 0.1
DEFAULT_DESIRED_TEMP = 21.0

buttons = Buttons()
display = Display()
heater = HeaterRelay(A5)
temp_mgr = TempMgr(TempSensor(A6), heater, display, DEFAULT_DESIRED_TEMP)


def state_change_listener(current_temp, desired_temp):
    display.show_temp_difference(current_temp, desired_temp, TEMP_CHANGE_INCREMENT)


def button_push_listener(button_index):
    sign = (-1, 1)[button_index]
    temp_mgr.change_desired_temp(sign * TEMP_CHANGE_INCREMENT)


temp_mgr.add_state_change_listener(state_change_listener)
buttons.add_push_listener(button_push_listener)

while True:
    temp_mgr.update()
    buttons.update()
    display.update()
