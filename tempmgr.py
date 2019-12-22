from time import monotonic, sleep

TEMP_CHECK_INTERVAL_SECS = 30
HEAT_ON_PSEUDO_TEMP = 23.5
HEAT_OFF_PSEUDO_TEMP = 23.0


class TempMgr:
    def __init__(self, temp_sensor, heater, display, desired_temp):
        self.temp_sensor = temp_sensor
        self.heater = heater
        self.display = display
        self.current_temp = None
        self.previous_temp = None
        self.desired_temp = desired_temp
        self.desired_temp_changed = True
        self.heat_on = False
        self.next_temp_read_time = monotonic()
        self.state_change_listeners = []

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
        self.current_temp = self.temp_sensor.read_temperature()
        heat_needed = self.desired_temp - self.current_temp > 0
        heat_state_changing = heat_needed != self.heat_on

        if heat_state_changing:
            self.heat_on = heat_needed
            self.heater.enable(on=heat_needed)

        if self.current_temp != self.previous_temp or heat_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            self._log_state(desired_temp=self.desired_temp if self.desired_temp_changed else None,
                            heat_state=heat_needed if heat_state_changing else None)
            self.desired_temp_changed = False
            self._notify_listeners()

    def _log_state(self, desired_temp=None, heat_state=None):
        desired_temp_str = '' if desired_temp is None else '{:.1f}'.format(desired_temp)
        heat_state = '' if heat_state is None else HEAT_ON_PSEUDO_TEMP if heat_state else HEAT_OFF_PSEUDO_TEMP
        line = '{:.2f}\t{:.1f}\t{}\t{}\n'.format(monotonic(), self.current_temp, desired_temp_str, heat_state)
        print(line.strip())
        try:
            with open('log.txt', 'a') as log:
                log.write(line)
        except OSError as e:
            pass

    def add_state_change_listener(self, listener):
        self.state_change_listeners.append(listener)

    def _notify_listeners(self):
        for l in self.state_change_listeners:
            l(self.current_temp, self.desired_temp)
