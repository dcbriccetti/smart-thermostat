class Relay:
    'Controls a relay connected to the heater, A/C or fan'

    def __init__(self, name: str, pin):
        self.name = name

    def enable(self, on=True):
        print(f'{self.name} enabled: {on}')
