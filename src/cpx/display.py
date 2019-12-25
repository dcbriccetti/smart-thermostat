from time import monotonic
import neopixel
from board import NEOPIXEL

DISPLAY_TIME_SECS = 60 * 5
OFF_COLOR       =    0,   0,   0
NEED_HEAT_COLOR = (  0,   0, 255), (  0, 255, 255)
TOO_HOT_COLOR   = (255,   0,   0), (255,  64,   0)


class Display:
    'Displays the difference between the measured and desired temperatures on LEDs'

    def __init__(self, temp_change_increment):
        self.temp_change_increment = temp_change_increment
        self.pixels = neopixel.NeoPixel(NEOPIXEL, 10, brightness=0.1, auto_write=False)
        self.turn_off_display_time = monotonic()
        self.display_on = False

    def show(self, current_temp, desired_temp):
        temp_diff = desired_temp - current_temp
        incremental_increase = round(temp_diff / self.temp_change_increment)
        if abs(incremental_increase) > 10:
            increase = round(temp_diff)
            color_index = 1
        else:
            increase = incremental_increase
            color_index = 0
        self.display_on = True
        self.turn_off_display_time = monotonic() + DISPLAY_TIME_SECS
        self._turn_pixels_off(show=False)
        for i in range(min(10, abs(increase))):
            if increase > 0:
                self.pixels[i] = NEED_HEAT_COLOR[color_index]    # Counterclockwise
            else:
                self.pixels[9 - i] = TOO_HOT_COLOR[color_index]  # Clockwise
        self.pixels.show()

    def update(self):
        'Turn off display at the appropriate time'
        time_now = monotonic()
        if self.display_on and time_now > self.turn_off_display_time:
            self.display_on = False
            self._turn_pixels_off()

    def _turn_pixels_off(self, show=True):
        for i in range(10):
            self.pixels[i] = OFF_COLOR
        if show:
            self.pixels.show()
