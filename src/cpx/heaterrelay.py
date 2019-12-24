from board import A5
from digitalio import DigitalInOut, Pull


class HeaterRelay:
    def __init__(self, pin=A5):
        self.heater = DigitalInOut(pin)
        self.heater.switch_to_output()
        self.heater.value = True

    def enable(self, on=True):
        self.heater.value = not on  # False value turns on relay
