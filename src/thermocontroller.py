from typing import Dict
from queue import Queue, Full
from time import monotonic, time, sleep
from logger import log_state
from sensorfail import SensorReadFailure
from metardecoder import outside_weather

TEMP_CHECK_INTERVAL_SECS = 30
OUTSIDE_WEATHER_CHECK_INTERVAL_SECS = 60 * 15
HEAT_PSEUDO_TEMP = 23


class ThermoController:
    def __init__(self, weather_station, sensor, heater, desired_temp):
        self.weather_station = weather_station
        self.sensor = sensor
        self.heater = heater
        self.desired_temp = desired_temp
        self.outside_temp = None
        self.current_temp = None
        self.current_humidity = None
        self.previous_temp = None
        self.desired_temp_changed = True
        self.heater_is_on = False
        self.shutoff = None
        self.state_queues = []
        self.status_history = []
        self.next_temp_read_time = monotonic()
        self.next_outside_weather_read_time = monotonic()

    def add_listener(self, queue: Queue):
        self.state_queues.append(queue)
        self._enqueue_state_to_single_queue(self.current_state_dict(), queue)

    def run(self):
        while True:
            try:
                self._update()
            except SensorReadFailure as f:
                print('Pausing after', f)
                sleep(30)
            sleep(0.1)

    def increase_temperature(self, amount: float):
        if amount:
            self.desired_temp += amount
            self.desired_temp_changed = True

    def _update(self):
        time_now = monotonic()
        if time_now >= self.next_outside_weather_read_time:
            self.next_outside_weather_read_time = time_now + OUTSIDE_WEATHER_CHECK_INTERVAL_SECS
            ow = outside_weather(self.weather_station)
            if ow:
                self.outside_temp = ow[0]
            else:
                print('Unable to get outside temperature')

        if time_now >= self.next_temp_read_time:
            self.next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

            if self.shutoff and self.shutoff.beyond_suppression_period():
                self.shutoff = None

            self.current_humidity, self.current_temp = self.sensor.read()
            self._change_heater_state(False)

        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heater_should_be_on = degrees_of_heat_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
        heater_state_changing = heater_should_be_on != self.heater_is_on

        if heater_state_changing:
            self._change_heater_state(heater_should_be_on)

        if self.current_temp != self.previous_temp or heater_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            self.desired_temp_changed = False
            hs = heater_should_be_on if heater_state_changing else None
            state = self.current_state_dict()
            self.status_history.append(state)
            self._enqueue_state_to_all_queues(state)
            log_state(HEAT_PSEUDO_TEMP, self.current_humidity, self.current_temp, self.desired_temp, heat_state=hs)

    def _enqueue_state_to_all_queues(self, state: Dict):
        for state_queue in self.state_queues:
            self._enqueue_state_to_single_queue(state, state_queue)

    def _enqueue_state_to_single_queue(self, state: Dict, state_queue: Queue):
        try:
            state_queue.put_nowait(state)
        except Full:
            pass

    def current_state_dict(self) -> Dict[str, str]:
        return {
            'time': time(),
            'outside_temp': self.outside_temp,
            'current_temp': self.current_temp,
            'desired_temp': self.desired_temp,
            'current_humidity': self.current_humidity,
            'heater_is_on': self.heater_is_on}

    def _change_heater_state(self, heater_should_be_on):
        if heater_should_be_on:
            self.heater_is_on = True
            self.shutoff = None
        else:
            self.heater_is_on = False

        self.heater.enable(on=heater_should_be_on)
