from time import monotonic
import neopixel
from board import NEOPIXEL

DISPLAY_TIME_SECS = 60 * 5
OFF_COLOR       =   0,   0,   0
NEED_HEAT_COLOR =   0,   0, 255
TOO_HOT_COLOR   = 255,   0,   0


class Display:
    def __init__(self):
        self.pixels = neopixel.NeoPixel(NEOPIXEL, 10, brightness=0.1, auto_write=False)
        self.turn_off_display_time = monotonic()
        self.display_on = False

    def show_temp_difference(self, current_temp, desired_temp, temp_change_increment):
        increase = round((desired_temp - current_temp) / temp_change_increment)
        self.display_on = True
        self.turn_off_display_time = monotonic() + DISPLAY_TIME_SECS
        self.turn_pixels_off(show=False)
        for i in range(min(10, abs(increase))):
            if increase > 0:
                self.pixels[i] = NEED_HEAT_COLOR    # Counterclockwise
            else:
                self.pixels[9 - i] = TOO_HOT_COLOR  # Clockwise
        self.pixels.show()

    def turn_pixels_off(self, show=True):
        for i in range(10):
            self.pixels[i] = OFF_COLOR
        if show:
            self.pixels.show()

    def update(self):
        time_now = monotonic()
        if self.display_on and time_now > self.turn_off_display_time:
            self.display_on = False
            self.turn_pixels_off()
