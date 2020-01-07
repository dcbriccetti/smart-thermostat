from math import sin
from time import monotonic


class Sensor:
    'Provides the humidity and temperature'

    def __init__(self):
        pass

    def read(self):
        return 50, 18 + sin(monotonic() / 1000) * 5
