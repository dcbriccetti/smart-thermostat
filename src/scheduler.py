from datetime import datetime
from thermocontroller import ThermoController


class Scheduler:
    def __init__(self, controller: ThermoController):
        self.controller = controller
        self._settings = [(datetime.strptime(s[0], '%Y-%m-%d %H:%M'), s[1]) for s in (
            ('2020-01-04 12:41', 25.0),
            ('2020-01-04 12:42', 22.1),
        )]

    def update(self):
        if (scheduled_temp := self._get_setting()) is not None:
            print('Making scheduled setting to', scheduled_temp)
            self.controller.set_temperature(scheduled_temp)

    def _get_setting(self):
        if self._settings and datetime.now() > self._settings[0][0]:
            return self._settings.pop(0)[1]
        return None
