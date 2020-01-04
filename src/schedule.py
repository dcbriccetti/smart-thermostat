from datetime import datetime


class Schedule:
    def __init__(self):
        self._settings = [(datetime.fromisoformat(s[0]), s[1]) for s in (
            ('2020-01-03 22:45', 17.0),
            ('2020-01-04 05:45', 22.0),
        )]

    def get_setting(self):
        if self._settings and datetime.now() > self._settings[0][0]:
            return self._settings.pop(0)[1]
        return None

