from time import localtime
from datetime import datetime, timedelta
from typing import Tuple, Sequence, Optional, Match, NamedTuple
from requests import request
from re import match

KILOMETERS_PER_NAUTICAL_MILE = 1.852
gmt_offset = localtime().tm_gmtoff

# Example METAR response:
example = '''000
SAUS70 KWBC 312200 RRQ
MTRCCR
METAR KCCR 312153Z 32003KT 10SM CLR 17/04 A3014 RMK AO2 SLP193
T01720039
'''

# or the METAR line could contain AUTO, like this:
'METAR KCCR 010553Z AUTO 15004KT 6SM BR CLR 08/06 A3015 RMK AO2 SLP195'


class WeatherMeas(NamedTuple):
    local_time: int
    temperature: float


class MatchGroupsRetriever:
    def __init__(self, match: Optional[Match[str]]):
        self.match = match

    def get(self, groups: Sequence[int]):
        return [int(self.match.group(group)) for group in groups]


def outside_weather(station='KCCR') -> WeatherMeas:
    'Return time, temperature and wind speed (in SI units)'
    response = request('GET', 'https://w1.weather.gov/data/METAR/' + station + '.1.txt')
    if response.status_code == 200:
        for line in response.text.split('\n'):
            if m := match(r'METAR.* (\d\d)(\d\d)(\d\d)Z .* (\d\d)/\d\d', line):
                print(line)
                matches = MatchGroupsRetriever(m)
                day, hour, minute, temperature = matches.get(range(1, 5))
                return WeatherMeas(metar_local_time(day, hour, minute), temperature)
        print('No METAR found in', response.text)
    else:
        print(response.status_code, response.text)


def metar_local_time(day, hour, minute) -> int:
    utc_now = datetime.utcnow()
    metar_utc = datetime(utc_now.year, utc_now.month, day, hour, minute)
    return round((metar_utc + timedelta(0, gmt_offset)).timestamp())
