from queue import Queue, Full
from time import monotonic
from logger import log_state

HEAT_PSEUDO_TEMP = 23


class ThermoController:
    def __init__(self, temp_sensor, heater, desired_temp):
        self.temp_sensor = temp_sensor
        self.heater = heater
        self.desired_temp = desired_temp
        self.current_temp = None
        self.current_humidity = None
        self.heater_is_on = False
        self.shutoff = None
        self.state_queues = []
        self.next_temp_read_time = monotonic()

    def add_listener(self, queue: Queue):
        self.state_queues.append(queue)

    def update(self):
        if self.shutoff and self.shutoff.beyond_suppression_period():
            self.shutoff = None
        self.current_humidity, self.current_temp = self.temp_sensor.read()
        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heater_should_be_on = degrees_of_heat_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
        heater_state_changing = heater_should_be_on != self.heater_is_on

        if heater_state_changing:
            self._change_heater_state(heater_should_be_on)

        hs = heater_should_be_on if heater_state_changing else None
        self.enqueue_state()
        log_state(HEAT_PSEUDO_TEMP, self.current_humidity, self.current_temp, self.desired_temp, heat_state=hs)

    def set_desired_temp(self, temperature):
        self.desired_temp = temperature
        self.next_temp_read_time = monotonic()

    def change_desired_temp(self, amount):
        self.set_desired_temp(self.desired_temp + amount)

    def enqueue_state(self):
        for state_queue in self.state_queues:
            try:
                state_queue.put_nowait({
                    'current_temp': self.current_temp, 'desired_temp': self.desired_temp,
                    'current_humidity': self.current_humidity})
            except Full:
                pass
                #print(f'queue {state_queue} is full')

    def _change_heater_state(self, heater_should_be_on):
        if heater_should_be_on:
            self.heater_is_on = True
            self.shutoff = None
        else:
            self.heater_is_on = False

        self.heater.enable(on=heater_should_be_on)
