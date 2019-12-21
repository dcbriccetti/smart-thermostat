from time import sleep, monotonic
import adafruit_dht
from board import BUTTON_A, BUTTON_B, A5, A6, NEOPIXEL
from digitalio import DigitalInOut, Pull
import neopixel

TEMP_CHANGE_INCREMENT = 0.1
TEMP_CHECK_INTERVAL_SECS = 30
BUTTON_SENSE_SECS = 0.25
DEFAULT_DESIRED_TEMP = 21.0
DISPLAY_TIME_SECS = 60
OFF_COLOR       =   0,   0,   0
NEED_HEAT_COLOR =   0,   0, 255
TOO_HOT_COLOR   = 255,   0,   0

pixels = neopixel.NeoPixel(NEOPIXEL, 10, brightness=0.2, auto_write=False)
button_a = DigitalInOut(BUTTON_A)
button_b = DigitalInOut(BUTTON_B)
for b in (button_a, button_b):
    b.switch_to_input(pull=Pull.DOWN)

dht = adafruit_dht.DHT22(A6)

heater = DigitalInOut(A5)
heater.switch_to_output()
heater.value = True

previous_temp = None
desired_temp = DEFAULT_DESIRED_TEMP
turn_off_display_time = next_temp_read_time = monotonic()
display_on = False


def read_temperature():
    while True:
        try:
            temp = dht.temperature
            if 0 < temp < 50:
                print((temp, desired_temp))
                return temp
        except RuntimeError as e:
            pass


def change_desired_temp(amount):
    global desired_temp, next_temp_read_time
    desired_temp += amount
    show_temp_difference()
    next_temp_read_time = monotonic()
    sleep(BUTTON_SENSE_SECS)


def show_temp_difference():
    global display_on, turn_off_display_time
    increase = desired_increase_degrees_increment()
    display_on = True
    turn_off_display_time = monotonic() + DISPLAY_TIME_SECS
    turn_pixels_off(show=False)
    for i in range(min(10, abs(increase))):
        if increase > 0:
            pixels[i] = NEED_HEAT_COLOR    # Counterclockwise
        else:
            pixels[9 - i] = TOO_HOT_COLOR  # Clockwise
    pixels.show()


def desired_increase_degrees_increment():
    return round((desired_temp - current_temp) / TEMP_CHANGE_INCREMENT)


def check_temperature():
    global current_temp, previous_temp
    current_temp = read_temperature()
    if current_temp != previous_temp:
        try:
            with open('log.txt', 'a') as log:
                log.write('{:d}\t{:.1f}\t{:.1f}\n'.format(round(monotonic()), current_temp, desired_temp))
        except OSError as e:
            pass
        previous_temp = current_temp
        show_temp_difference()
    heat_needed = desired_temp - current_temp
    heater.value = not heat_needed > 0  # False value turns on relay


def turn_pixels_off(show=True):
    for i in range(10):
        pixels[i] = OFF_COLOR
    if show:
        pixels.show()


while True:
    time_now = monotonic()
    if time_now >= next_temp_read_time:
        check_temperature()
        next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

    if button_a.value:
        change_desired_temp(-TEMP_CHANGE_INCREMENT)
    if button_b.value:
        change_desired_temp(TEMP_CHANGE_INCREMENT)

    if display_on and time_now > turn_off_display_time:
        display_on = False
        turn_pixels_off()
