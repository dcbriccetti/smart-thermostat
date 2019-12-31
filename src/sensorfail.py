class SensorReadFailure(Exception):

    def __init__(self, humidity, temperature):
        self.humidity = humidity
        self.temperature = temperature

    def __str__(self) -> str:
        return 'Temperature: {}, Humidity: {}'.format(self.temperature, self.humidity)
