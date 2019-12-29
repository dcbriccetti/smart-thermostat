from queue import Queue, Full
from time import monotonic, time
from logger import log_state

TEMP_CHECK_INTERVAL_SECS = 30
HEAT_PSEUDO_TEMP = 23


class SensorReadFailure(Exception):
    pass


class ThermoController:
    def __init__(self, sensor, heater, desired_temp):
        self.sensor = sensor
        self.heater = heater
        self.desired_temp = desired_temp
        self.current_temp = None
        self.current_humidity = None
        self.previous_temp = None
        self.desired_temp_changed = True
        self.heater_is_on = False
        self.shutoff = None
        self.state_queues = []
        self.next_temp_read_time = monotonic()

    def add_listener(self, queue: Queue):
        self.state_queues.append(queue)
        self._enqueue_state_to_single_queue(queue)

    def update(self):
        time_now = monotonic()
        if time_now >= self.next_temp_read_time:
            self.next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

            if self.shutoff and self.shutoff.beyond_suppression_period():
                self.shutoff = None
            self.current_humidity, self.current_temp = self.sensor.read()
            if not (self.current_humidity and self.current_temp):
                self._change_heater_state(False)
                raise SensorReadFailure()

        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heater_should_be_on = degrees_of_heat_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
        heater_state_changing = heater_should_be_on != self.heater_is_on

        if heater_state_changing:
            self._change_heater_state(heater_should_be_on)

        if self.current_temp != self.previous_temp or heater_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            self.desired_temp_changed = False
            hs = heater_should_be_on if heater_state_changing else None
            self._enqueue_state_to_all_queues()
            log_state(HEAT_PSEUDO_TEMP, self.current_humidity, self.current_temp, self.desired_temp, heat_state=hs)

    def set_desired_temp(self, temperature):
        if temperature != self.desired_temp:
            self.desired_temp = temperature
            self.desired_temp_changed = True

    def _enqueue_state_to_all_queues(self):
        for state_queue in self.state_queues:
            self._enqueue_state_to_single_queue(state_queue)

    def _enqueue_state_to_single_queue(self, state_queue):
        try:
            state_queue.put_nowait({
                'time': time(),
                'current_temp': self.current_temp,
                'desired_temp': self.desired_temp,
                'current_humidity': self.current_humidity,
                'heater_is_on': self.heater_is_on})
        except Full:
            pass

    def _change_heater_state(self, heater_should_be_on):
        if heater_should_be_on:
            self.heater_is_on = True
            self.shutoff = None
        else:
            self.heater_is_on = False

        self.heater.enable(on=heater_should_be_on)
