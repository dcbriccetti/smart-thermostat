from time import monotonic, sleep

TEMP_CHECK_INTERVAL_SECS = 30


class TempMgr:
    def __init__(self, temp_sensor, heater, display, desired_temp):
        self.temp_sensor = temp_sensor
        self.heater = heater
        self.display = display
        self.current_temp = None
        self.previous_temp = None
        self.desired_temp = desired_temp
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
        self._notify_listeners()

    def _check_temperature(self):
        self.current_temp = self.temp_sensor.read_temperature()
        if self.current_temp != self.previous_temp:
            try:
                with open('log.txt', 'a') as log:
                    log.write('{:d}\t{:.1f}\t{:.1f}\n'.format(round(monotonic()), self.current_temp, self.desired_temp))
            except OSError as e:
                pass
            self.previous_temp = self.current_temp
            self._notify_listeners()
        heat_needed = self.desired_temp - self.current_temp > 0
        self.heater.enable(on=heat_needed)

    def add_state_change_listener(self, listener):
        self.state_change_listeners.append(listener)

    def _notify_listeners(self):
        for l in self.state_change_listeners:
            l(self.current_temp, self.desired_temp)
