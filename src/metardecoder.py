from typing import Tuple
from requests import request
from re import match

KILOMETERS_PER_NAUTICAL_MILE = 1.852

# Example METAR response:
example = '''000
SAUS70 KWBC 312200 RRQ
MTRCCR
METAR KCCR 312153Z 32003KT 10SM CLR 17/04 A3014 RMK AO2 SLP193
T01720039
'''

# or the METAR line could contain AUTO, like this:
'METAR KCCR 010553Z AUTO 15004KT 6SM BR CLR 08/06 A3015 RMK AO2 SLP195'


def outside_weather(station='KCCR') -> Tuple[float, float]:
    'Return temperature and wind speed (in SI units)'
    response = request('GET', 'https://w1.weather.gov/data/METAR/' + station + '.1.txt')
    if response.status_code == 200:
        for line in response.text.split('\n'):
            m = match(r'METAR.* \d\d\d(\d\d)KT .* (\d\d)/\d\d', line)
            if m:
                print(line)
                wind_knots = int(m.group(1))
                wind_kph = round(wind_knots * KILOMETERS_PER_NAUTICAL_MILE)
                temperature = int(m.group(2))
                return temperature, wind_kph


if __name__ == '__main__':
    w = outside_weather('KSFO')
    print(w)
