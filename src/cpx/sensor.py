from board import A5, A6
import adafruit_dht


class Sensor:
    def __init__(self, pin=A6):
        self.dht = adafruit_dht.DHT22(pin)

    def read(self):
        while True:
            try:
                temp = self.dht.temperature
                humidity = self.dht.humidity
                if 0 < temp < 50:
                    return temp, humidity
            except RuntimeError as e:
                pass
