from requests import request

KILOMETERS_PER_NAUTICAL_MILE = 1.852


def outside_weather(station='KCCR'):
    response = request('GET', 'https://w1.weather.gov/data/METAR/' + station + '.1.txt')
    lines = response.text.split('\n')
    metar_line = lines[3]
    fields = metar_line.split(' ')
    wind_speed_knots = int(fields[3][3:5])
    wind_speed_kph = wind_speed_knots * KILOMETERS_PER_NAUTICAL_MILE
    temp_dew = fields[6]
    temperature = int(temp_dew.split('/')[0])
    return temperature, wind_speed_kph


if __name__ == '__main__':
    w = outside_weather()
    print(w)
