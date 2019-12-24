import board
from analogio import AnalogIn


class TimingKnob:
    def __init__(self, pin=board.A0):
        self._knob = AnalogIn(pin)

    def value_between(self, low, high):
        'Return the knob value mapped to the given range'
        t_range = high - low
        setting = self._knob.value / 65535.0
        return low + setting * t_range
