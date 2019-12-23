from time import monotonic, sleep

TEMP_CHECK_INTERVAL_SECS = 15
SMALL_CHANGE_HEAT_SECS = 70
HEAD_REENABLE_AFTER_SECS = SMALL_CHANGE_HEAT_SECS + 120
HEAT_PSEUDO_TEMP = 25


class TempMgr:
    def __init__(self, temp_sensor, heater, display, desired_temp):
        self.temp_sensor = temp_sensor
        self.heater = heater
        self.display = display
        self.desired_temp = desired_temp
        self.current_temp = None
        self.previous_temp = None
        self.desired_temp_changed = True
        self.heat_on = False
        self.heat_suppression_period = None
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
        time_now = monotonic()
        if self._beyond_suppression_period():
            self.heat_suppression_period = None
        self.current_temp = self.temp_sensor.read_temperature()
        degrees_of_heat_needed = self.desired_temp - self.current_temp
        heat_needed = degrees_of_heat_needed > 0 and self._not_in_suppression_period()
        heat_state_changing = heat_needed != self.heat_on

        if heat_state_changing:
            if heat_needed:
                self.heat_on = True
                self.heat_suppression_period = time_now + SMALL_CHANGE_HEAT_SECS, \
                    time_now + HEAD_REENABLE_AFTER_SECS if degrees_of_heat_needed < 1 else None
            else:
                self.heat_on = False
            self.heater.enable(on=heat_needed)

        if self.current_temp != self.previous_temp or heat_state_changing or self.desired_temp_changed:
            self.previous_temp = self.current_temp
            self._log_state(desired_temp=self.desired_temp if self.desired_temp_changed else None,
                heat_state=heat_needed if heat_state_changing else None)
            self.desired_temp_changed = False
            self._notify_listeners()

    def _beyond_suppression_period(self):
        return self.heat_suppression_period and monotonic() > self.heat_suppression_period[1]

    def _not_in_suppression_period(self):
        return self.heat_suppression_period is None or not self.heat_suppression_period[0] < monotonic() < self.heat_suppression_period[1]

    def _log_state(self, desired_temp=None, heat_state=None):
        desired_temp_str = '' if desired_temp is None else '{:.1f}'.format(desired_temp)
        heat_state = '\t' if heat_state is None else \
            '%.1f\t' % HEAT_PSEUDO_TEMP if heat_state else '\t%.1f' % HEAT_PSEUDO_TEMP
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
