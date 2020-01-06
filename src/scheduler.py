from typing import NamedTuple
from datetime import datetime, timedelta
from thermocontroller import ThermoController


class Setting(NamedTuple):
    datetime: datetime
    temperature: float


class Scheduler:
    def __init__(self, controller: ThermoController):
        self.controller = controller
        self._settings: list[Setting] = []

    def update(self):
        for i, setting in enumerate(self._settings):
            if datetime.now() > setting.datetime:
                advanced = Setting(setting.datetime + timedelta(1), setting.temperature)
                self._settings[i] = advanced
                print('Making scheduled setting to', setting)
                self.controller.set_temperature(setting.temperature)
                print('settings now', self._settings)

    def set(self, text: bytes):
        '* 23:00 21.0'
        now = datetime.now()
        self._settings.clear()
        for line in text.decode('utf-8').splitlines():
            parts = line.split()
            assert parts[0] == '*'
            hm = [int(n) for n in parts[1].split(':')]
            temperature = float(parts[2])
            next_setting_time = datetime(now.year, now.month, now.day, hm[0], hm[1])
            if next_setting_time < now:  # That time today has passed
                next_setting_time += timedelta(1)  # Advance to tomorrow
            self._settings.append(Setting(next_setting_time, temperature))

        print(self._settings)

    def render(self) -> str:
        def pad(num: int): return f'0{num}'[-2:]
        def f(s): return f'* {pad(s.datetime.hour)}:{pad(s.datetime.minute)}{s.temperature: .1f}'
        return '\n'.join((f(s) for s in self._settings))
