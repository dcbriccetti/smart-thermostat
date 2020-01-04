from datetime import datetime


class Schedule:
    def __init__(self):
        self._settings = [(datetime.strptime(s[0], '%Y-%m-%d %H:%M'), s[1]) for s in (
            ('2020-01-04 12:41', 25.0),
            ('2020-01-04 12:42', 22.0),
        )]

    def get_setting(self):
        if self._settings and datetime.now() > self._settings[0][0]:
            return self._settings.pop(0)[1]
        return None
