from time import monotonic
from shutoff import AnticipatoryShutoff
from logger import log_state

TEMP_CHECK_INTERVAL_SECS = 45
HEAT_PSEUDO_TEMP = 23


class ThermoController:
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
        self.shutoff = None
        self.next_temp_read_time = monotonic()
        self.state_change_listeners = []

    def update(self):
        time_now = monotonic()
        if time_now >= self.next_temp_read_time:
            self._manage_temperature()
            self.next_temp_read_time = time_now + TEMP_CHECK_INTERVAL_SECS

    def change_desired_temp(self, amount):
        self.desired_temp += amount
        self.next_temp_read_time = monotonic()
        self.desired_temp_changed = True

    def _manage_temperature(self):
        if self.shutoff and self.shutoff.beyond_suppression_period():
            self.shutoff = None
        self.current_temp, self.current_humidity = self.temp_sensor.read()
        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heater_should_be_on = degrees_of_heat_needed > 0 and not (self.shutoff and self.shutoff.in_suppression_period())
        heater_state_changing = heater_should_be_on != self.heater_is_on

        if heater_state_changing:
            self._change_heater_state(heater_should_be_on, degrees_of_heat_needed)

        if self.current_temp != self.previous_temp or heater_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            dt = self.desired_temp if self.desired_temp_changed else None
            hs = heater_should_be_on if heater_state_changing else None
            log_state(HEAT_PSEUDO_TEMP, self.current_temp, desired_temp=dt, heat_state=hs)
            self.desired_temp_changed = False
            self.display.show(self.current_temp, self.desired_temp)

    def _change_heater_state(self, heater_should_be_on, degrees_of_heat_needed):
        if heater_should_be_on:
            self.heater_is_on = True
            self.shutoff = AnticipatoryShutoff(self.knob) if degrees_of_heat_needed < 1 else None
        else:
            self.heater_is_on = False

        self.heater.enable(on=heater_should_be_on)
