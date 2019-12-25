import board
from analogio import AnalogIn


class TimingKnob:
    'Code for a potentiometer that controls the heat shutoff time'

    def __init__(self, pin=board.A0):
        self._knob = AnalogIn(pin)

    def value_between(self, low, high):
        'Return the knob value mapped to the given range'
        return low + self._knob.value / 65535.0 * (high - low)
