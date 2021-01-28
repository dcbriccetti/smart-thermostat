from typing import Dict, List, Any, Optional, Union
from queue import Queue, Full
from time import monotonic, time, sleep
from sensorfail import SensorReadFailure
from outside_weather import outside_weather

WEATHER_OBSERVATION_INTERVAL_SECS = 60


class ThermoController:
    outside_weather: Dict[str, Any]
    state_queues: List[Queue]

    def __init__(self, weather_query: str, sensor, heater, cooler, fan, desired_temp: float):
        self.weather_query = weather_query
        self.sensor = sensor
        self.heater = heater
        self.cooler = cooler
        self.fan = fan
        self.cooling = False

        self.outside_weather = {}
        self.desired_temp = desired_temp
        self.inside_temp = None
        self.inside_humidity = None

        self.previous_temp = None
        self.desired_temp_changed = True
        self.hac_is_on = False
        self.shutoff = None
        self.state_queues = []
        self.status_history = []
        self.next_temp_read_time = monotonic()
        self.next_weather_observation_time = monotonic()

    def add_state_queue(self, queue: Queue):
        self.state_queues.append(queue)
        self._enqueue_state_to_single_queue(self.current_state_dict(), queue)

    def update(self) -> Optional[Dict]:
        try:
            state: Optional[Dict] = None
            time_now = monotonic()

            if time_now >= self.next_weather_observation_time:
                self._manage_outside_weather()
                self.next_weather_observation_time = time_now + WEATHER_OBSERVATION_INTERVAL_SECS

                if self.shutoff and self.shutoff.beyond_suppression_period():
                    self.shutoff = None

                self.inside_humidity, self.inside_temp = self.sensor.read()
                self._change_hac_state(False)

            degrees_of_change_needed: float = \
                self.inside_temp - self.desired_temp if self.cooling else \
                self.desired_temp - self.inside_temp
            hac_should_be_on = degrees_of_change_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
            hac_state_changing = hac_should_be_on != self.hac_is_on

            if hac_state_changing:
                self._change_hac_state(hac_should_be_on)

            if self.inside_temp != self.previous_temp or hac_state_changing or self.desired_temp_changed:
                self.previous_temp = self.inside_temp
                self.desired_temp_changed = False
                hs = hac_should_be_on if hac_state_changing else None
                state = self.current_state_dict()
                self.status_history.append(state)
                self._enqueue_state_to_all_queues(state)

            return state
        except SensorReadFailure as f:
            print('Pausing after', f)
            sleep(30)

    def set_temperature(self, temperature: float):
        self.desired_temp = temperature
        self.desired_temp_changed = True

    def change_temperature(self, amount: float):
        if amount:
            self.set_temperature(self.desired_temp + amount)

    def activate_fan(self, activate: bool):
        self.fan.enable(activate)

    def enable_cool(self, enable: bool):
        self.cooling = enable
        for hac in self.heater, self.cooler:
            hac.enable(False)
        self.hac_is_on = False
        self._read_temp_now()

    def _read_temp_now(self) -> None:
        self.next_temp_read_time = monotonic()

    def _manage_outside_weather(self):
        if ow := outside_weather(self.weather_query):
            self.outside_weather = {
                'outside_temp'    : ow.temperature,
                'wind_dir'        : ow.wind_dir,
                'wind_speed'      : ow.wind_speed,
                'gust'            : ow.gust,
                'pressure'        : ow.pressure,
                'outside_humidity': ow.humidity,
                'main_weather'    : ow.main_weather,
            }
        else:
            print('Unable to get weather')

    def _enqueue_state_to_all_queues(self, state: Dict):
        for state_queue in self.state_queues:
            self._enqueue_state_to_single_queue(state, state_queue)

    def _enqueue_state_to_single_queue(self, state: Dict, state_queue: Queue):
        try:
            state_queue.put_nowait(state)
        except Full:
            pass

    def current_state_dict(self) -> Dict[str, Any]:
        results = {
            'time':            time(),
            'inside_temp':     self.inside_temp,
            'desired_temp':    self.desired_temp,
            'inside_humidity': self.inside_humidity,
            'heater_is_on':    self.hac_is_on
        }
        results.update(self.outside_weather)
        return results

    def _change_hac_state(self, should_be_on: bool):
        if should_be_on:
            self.hac_is_on = True
            self.shutoff = None
        else:
            self.hac_is_on = False

        current_hac, other_hac = (self.cooler, self.heater) if self.cooling else (self.heater, self.cooler)
        other_hac.enable(False)
        current_hac.enable(on=should_be_on)
