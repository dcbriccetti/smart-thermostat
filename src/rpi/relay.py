from digitalio import DigitalInOut


class Relay:
    'Controls a relay connected to the heater, A/C or fan'

    def __init__(self, name: str, pin):
        self.name = name
        self.control = DigitalInOut(pin)
        self.control.switch_to_output()
        self.control.value = True

    def enable(self, on=True):
        self.control.value = not on  # False value turns on relay
