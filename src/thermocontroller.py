from typing import Dict
from queue import Queue, Full
from time import monotonic, time, sleep
from sensorfail import SensorReadFailure
from outside_weather import outside_weather

TEMP_CHECK_INTERVAL_SECS = 30
OUTSIDE_WEATHER_CHECK_INTERVAL_SECS = 60


class ThermoController:
    def __init__(self, weather_query: str, sensor, heater, cooler, fan, desired_temp: float):
        self.weather_query = weather_query
        self.sensor = sensor
        self.heater = heater
        self.cooler = cooler
        self.fan = fan
        self.cooling = False
        self.desired_temp = desired_temp
        self.outside_temp = None
        self.current_temp = None
        self.current_temp_collection_time = None
        self.humidity = None
        self.outside_humidity = None
        self.wind_dir = None
        self.wind_speed = None
        self.gust = None
        self.pressure = None
        self.main_weather = None
        self.previous_temp = None
        self.desired_temp_changed = True
        self.hac_is_on = False
        self.shutoff = None
        self.state_queues = []
        self.status_history = []
        self.next_temp_read_time = monotonic()
        self.next_outside_weather_read_time = monotonic()

    def add_listener(self, queue: Queue):
        self.state_queues.append(queue)
        self._enqueue_state_to_single_queue(self.current_state_dict(), queue)

    def update(self):
        try:
            self._update()
        except SensorReadFailure as f:
            print('Pausing after', f)
            sleep(30)
        sleep(0.1)

    def set_temperature(self, temperature: float):
        self.desired_temp = temperature
        self.desired_temp_changed = True

    def increase_temperature(self, amount: float):
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

    def _update(self):
        time_now = monotonic()

        self._manage_outside_weather(time_now)

        if time_now >= self.next_temp_read_time:
            self.next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

            if self.shutoff and self.shutoff.beyond_suppression_period():
                self.shutoff = None

            self.humidity, self.current_temp = self.sensor.read()
            self._change_hac_state(False)

        degrees_of_change_needed = \
            self.current_temp - self.desired_temp if self.cooling else \
            self.desired_temp - self.current_temp
        hac_should_be_on = degrees_of_change_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
        hac_state_changing = hac_should_be_on != self.hac_is_on

        if hac_state_changing:
            self._change_hac_state(hac_should_be_on)

        if self.current_temp != self.previous_temp or hac_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            self.desired_temp_changed = False
            hs = hac_should_be_on if hac_state_changing else None
            state = self.current_state_dict()
            self.status_history.append(state)
            self._enqueue_state_to_all_queues(state)

    def _read_temp_now(self) -> None:
        self.next_temp_read_time = monotonic()

    def _manage_outside_weather(self, time_now):
        if time_now >= self.next_outside_weather_read_time:
            self.next_outside_weather_read_time = time_now + OUTSIDE_WEATHER_CHECK_INTERVAL_SECS
            if ow := outside_weather(self.weather_query):
                self.outside_temp_collection_time = ow.local_time
                self.outside_temp = ow.temperature
                self.wind_dir = ow.wind_dir
                self.wind_speed = ow.wind_speed
                self.gust = ow.gust
                self.pressure = ow.pressure
                self.outside_humidity = ow.humidity
                self.main_weather = ow.main_weather
                oat_age = round((time() - self.outside_temp_collection_time) / 60)
                print(f'Outside temp {self.outside_temp} from {oat_age} minutes ago')
            else:
                self.outside_temp_collection_time = self.outside_temp = None
                print('Unable to get outside temperature')

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
            'outside_temp_collection_time': self.outside_temp_collection_time,
            'wind_dir': self.wind_dir,
            'wind_speed': self.wind_speed,
            'gust': self.gust,
            'current_temp': self.current_temp,
            'desired_temp': self.desired_temp,
            'humidity': self.humidity,
            'outside_humidity': self.outside_humidity,
            'pressure': self.pressure,
            'main_weather': self.main_weather,
            'heater_is_on': self.hac_is_on}

    def _change_hac_state(self, should_be_on: bool):
        if should_be_on:
            self.hac_is_on = True
            self.shutoff = None
        else:
            self.hac_is_on = False

        current_hac, other_hac = (self.cooler, self.heater) if self.cooling else (self.heater, self.cooler)
        other_hac.enable(False)
        current_hac.enable(on=should_be_on)
