import board
from analogio import AnalogIn


class Knob:
    def __init__(self, pin=board.A0):
        self._knob = AnalogIn(pin)

    @property
    def value(self):
        return self._knob.value
