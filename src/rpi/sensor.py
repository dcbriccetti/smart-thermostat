import Adafruit_DHT

from sensorfail import SensorReadFailure

REASONABLE_TEMP_RANGE = 10, 50
REASONABLE_HUMIDITY_RANGE = 20, 100


class Sensor:
    'Provides the humidity and temperature'

    def __init__(self, pin=20):
        self.pin = pin

    def read(self):
        h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
        if not self._reasonable_sensor_values(h, t):
            raise SensorReadFailure(h, t)
        return h, t

    def _reasonable_sensor_values(self, h, t):
        return h and t and REASONABLE_HUMIDITY_RANGE[0] < h < REASONABLE_HUMIDITY_RANGE[1] and \
               REASONABLE_TEMP_RANGE[0] < t < REASONABLE_TEMP_RANGE[1]
