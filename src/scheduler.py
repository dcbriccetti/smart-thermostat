from datetime import datetime, timedelta
from thermocontroller import ThermoController


class Scheduler:
    def __init__(self, controller: ThermoController):
        self.controller = controller
        self._settings: list[tuple[datetime, float]] = []

    def update(self):
        if (scheduled_temp := self._get_setting()) is not None:
            print('Making scheduled setting to', scheduled_temp)
            print('settings now', self._settings)
            self.controller.set_temperature(scheduled_temp)

    def _get_setting(self):
        if self._settings and datetime.now() > self._settings[0][0]:
            popped = self._settings.pop(0)
            advanced = (popped[0] + timedelta(1), popped[1])
            self._settings.append(advanced)
            return popped[1]
        return None

    def set(self, text: bytes):
        '* 23:00 21.0'
        now = datetime.now()
        self._settings: list[tuple[datetime, float]] = []
        for line in text.decode('utf-8').splitlines():
            parts = line.split()
            assert parts[0] == '*'
            hm = [int(n) for n in parts[1].split(':')]
            temperature = float(parts[2])
            next_setting_time = datetime(now.year, now.month, now.day, hm[0], hm[1])
            if next_setting_time < now:  # That time today has passed
                next_setting_time += timedelta(1)  # Advance to tomorrow
            self._settings.append((next_setting_time, temperature))

        print(self._settings)

    def render(self) -> str:
        def pad(num: int): return f'0{num}'[-2:]
        def f(s): return f'* {pad(s[0].hour)}:{pad(s[0].minute)}{s[1]: .1f}'
        return '\n'.join((f(s) for s in self._settings))
