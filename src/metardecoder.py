from typing import Tuple
from requests import request

KILOMETERS_PER_NAUTICAL_MILE = 1.852

''' Example METAR response:
000
SAUS70 KWBC 312200 RRQ
MTRCCR
METAR KCCR 312153Z 32003KT 10SM CLR 17/04 A3014 RMK AO2 SLP193
T01720039
'''


def outside_weather(station='KCCR') -> Tuple[float, float]:
    'Return temperature and wind speed (in SI units)'
    response = request('GET', 'https://w1.weather.gov/data/METAR/' + station + '.1.txt')
    metar_line = response.text.split('\n')[3]
    print(metar_line)
    fields = metar_line.split(' ')
    wind_knots = int(fields[3][3:5])
    wind_kph = wind_knots * KILOMETERS_PER_NAUTICAL_MILE
    temperature = int(fields[6].split('/')[0])
    return temperature, wind_kph


if __name__ == '__main__':
    w = outside_weather()
    print(w)
