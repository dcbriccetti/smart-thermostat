import adafruit_dht


class TempSensor:
    def __init__(self, pin):
        self.dht = adafruit_dht.DHT22(pin)

    def read_temperature(self):
        while True:
            try:
                temp = self.dht.temperature
                if 0 < temp < 50:
                    return temp
            except RuntimeError as e:
                pass
