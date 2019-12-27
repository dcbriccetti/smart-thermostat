class HeaterRelay:
    'Controls the relay connected to the heater'

    def __init__(self):
        pass

    def enable(self, on=True):
        print('heat enabled:', on)
