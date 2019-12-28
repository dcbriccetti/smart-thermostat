import Adafruit_DHT


class Sensor:
    'Provides the temperature and humidity'

    def __init__(self, pin=4):
        self.pin = pin

    def read(self):
        return Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
