from random import randint


class Sensor:
    'Provides the temperature and humidity'

    def __init__(self):
        pass

    def read(self):
        return 20 + randint(0, 15) / 10.0, 50.0
