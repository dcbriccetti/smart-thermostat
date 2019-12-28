import board
from digitalio import DigitalInOut, Pull


class HeaterRelay:
    'Controls the relay connected to the heater'

    def __init__(self, pin=board.D21):
        self.heater = DigitalInOut(pin)
        self.heater.switch_to_output()
        self.heater.value = True

    def enable(self, on=True):
        self.heater.value = not on  # False value turns on relay
