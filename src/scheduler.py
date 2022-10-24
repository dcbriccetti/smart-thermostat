from typing import NamedTuple, List
from datetime import datetime, timedelta
from thermocontroller import ThermoController


class Setting(NamedTuple):
    datetime: datetime
    temperature: float

    @classmethod
    def from_string(cls, string: str):
        parts = string.split()
        if len(parts) == 2:
            now = datetime.now()
            when, temp = parts
            hm = [int(n) for n in when.split(':')]
            hour: int = hm[0]
            minute: int = hm[1] if len(hm) == 2 else 0
            temperature = float(temp)
            next_setting_time = datetime(now.year, now.month, now.day, hour, minute)
            if next_setting_time < now:  # That time today has passed
                next_setting_time += timedelta(1)  # Advance to tomorrow
            return cls(next_setting_time, temperature)

        raise ValueError(f'{string} does not match hh[:mm] t')

class Scheduler:
    def __init__(self, thermoController: ThermoController):
        self.thermoController = thermoController
        self._settings: List[Setting] = []

    def update(self):
        for i, setting in enumerate(self._settings):
            if datetime.now() > setting.datetime:
                advanced = Setting(setting.datetime + timedelta(1), setting.temperature)
                self._settings[i] = advanced
                print('Making scheduled setting to', setting)
                self.thermoController.set_temperature(setting.temperature)
                print('settings now', self._settings)

    def set(self, text: bytes):
        '23:00 21.0'
        self._settings.clear()
        for line in text.decode('utf-8').splitlines():
            try:
                self._settings.append(Setting.from_string(line))
            except ValueError as e:
                print(e)

        print(self._settings)

    def render(self) -> str:
        def pad(num: int): return f'0{num}'[-2:]
        def f(s): return f'* {pad(s.datetime.hour)}:{pad(s.datetime.minute)}{s.temperature: .1f}'
        return '\n'.join((f(s) for s in self._settings))
