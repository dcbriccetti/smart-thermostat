from random import randint


class Sensor:
    'Provides the humidity and temperature'

    def __init__(self):
        pass

    def read(self):
        return 50, 20 + randint(0, 15) / 10.0
