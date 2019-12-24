from time import monotonic, sleep
from logger import log_state

TEMP_CHECK_INTERVAL_SECS = 15
HEAD_REENABLE_AFTER_SECS = 180
HEAT_PSEUDO_TEMP = 23


class TempMgr:
    def __init__(self, temp_sensor, knob, heater, display, desired_temp):
        self.temp_sensor = temp_sensor
        self.knob = knob
        self.heater = heater
        self.display = display
        self.desired_temp = desired_temp
        self.current_temp = None
        self.current_humidity = None
        self.previous_temp = None
        self.desired_temp_changed = True
        self.heater_is_on = False
        self.heat_suppression_period = None
        self.next_temp_read_time = monotonic()
        self.state_change_listeners = []

    def add_state_change_listener(self, listener):
        self.state_change_listeners.append(listener)

    def update(self):
        time_now = monotonic()
        if time_now >= self.next_temp_read_time:
            self._check_temperature()
            self.next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

    def change_desired_temp(self, amount):
        self.desired_temp += amount
        self.next_temp_read_time = monotonic()
        self.desired_temp_changed = True

    def _check_temperature(self):
        time_now = monotonic()
        if self._beyond_suppression_period():
            self.heat_suppression_period = None
        self.current_temp, self.current_humidity = self.temp_sensor.read()
        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heater_should_be_on = degrees_of_heat_needed > 0 and self._not_in_suppression_period()
        heater_state_changing = heater_should_be_on != self.heater_is_on

        if heater_state_changing:
            if heater_should_be_on:
                self.heater_is_on = True
                schs = self._small_change_heat_secs()
                self.heat_suppression_period = time_now + schs, \
                    time_now + schs + HEAD_REENABLE_AFTER_SECS if degrees_of_heat_needed < 1 else None
            else:
                self.heater_is_on = False
            self.heater.enable(on=heater_should_be_on)

        if self.current_temp != self.previous_temp or heater_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            log_state(HEAT_PSEUDO_TEMP, self.current_temp, desired_temp=self.desired_temp if self.desired_temp_changed
                      else None, heat_state=heater_should_be_on if heater_state_changing else None)
            self.desired_temp_changed = False
            self._notify_listeners()

    def _small_change_heat_secs(self):
        t_min = 90
        t_max = 60 * 10
        t_range = t_max - t_min
        setting = self.knob.value / 65535.0
        return t_min + setting * t_range

    def _beyond_suppression_period(self):
        return self.heat_suppression_period and monotonic() > self.heat_suppression_period[1]

    def _not_in_suppression_period(self):
        return self.heat_suppression_period is None or \
               not self.heat_suppression_period[0] < monotonic() < self.heat_suppression_period[1]

    def _notify_listeners(self):
        for l in self.state_change_listeners:
            l(self.current_temp, self.desired_temp)
