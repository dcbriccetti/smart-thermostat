import board
from digitalio import DigitalInOut, Pull


class FanRelay:
    'Controls the relay connected to the heater'

    def __init__(self, pin=board.D16):
        self.fan = DigitalInOut(pin)
        self.fan.switch_to_output()
        self.fan.value = True

    def enable(self, on=True):
        self.fan.value = not on  # False value turns on relay
