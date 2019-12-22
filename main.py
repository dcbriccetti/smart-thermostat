from time import sleep, monotonic
from board import BUTTON_A, BUTTON_B, A5, A6, NEOPIXEL
from digitalio import DigitalInOut, Pull
from tempsensor import TempSensor
from heaterrelay import HeaterRelay
from display import Display

TEMP_CHANGE_INCREMENT = 0.1
TEMP_CHECK_INTERVAL_SECS = 30
BUTTON_SENSE_SECS = 0.1
DEFAULT_DESIRED_TEMP = 21.0

button_a = DigitalInOut(BUTTON_A)
button_b = DigitalInOut(BUTTON_B)
for b in (button_a, button_b):
    b.switch_to_input(pull=Pull.DOWN)

display = Display()
temp_sensor = TempSensor(A6)
heater = HeaterRelay(A5)

previous_temp = None
desired_temp = DEFAULT_DESIRED_TEMP
next_temp_read_time = monotonic()


def change_desired_temp(amount):
    global desired_temp, next_temp_read_time
    desired_temp += amount
    display.show_temp_difference(current_temp, desired_temp, TEMP_CHANGE_INCREMENT)
    next_temp_read_time = monotonic()
    sleep(BUTTON_SENSE_SECS)


def check_temperature():
    global current_temp, previous_temp
    current_temp = temp_sensor.read_temperature()
    if current_temp != previous_temp:
        try:
            with open('log.txt', 'a') as log:
                log.write('{:d}\t{:.1f}\t{:.1f}\n'.format(round(monotonic()), current_temp, desired_temp))
        except OSError as e:
            pass
        previous_temp = current_temp
        display.show_temp_difference(current_temp, desired_temp, TEMP_CHANGE_INCREMENT)
    heat_needed = desired_temp - current_temp
    heater.enable(on=heat_needed > 0)


while True:
    time_now = monotonic()
    if time_now >= next_temp_read_time:
        check_temperature()
        next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

    if button_a.value:
        change_desired_temp(-TEMP_CHANGE_INCREMENT)
    if button_b.value:
        change_desired_temp(TEMP_CHANGE_INCREMENT)

    display.update()
