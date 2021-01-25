import os
from time import time
from typing import Optional, NamedTuple

import requests

key = os.environ['OPEN_WEATHER_MAP_KEY']


class WeatherMeas(NamedTuple):
    local_time: int
    temperature: float
    wind_speed: float
    wind_dir: int


def outside_weather(weather_query='q=Oakland') -> Optional[WeatherMeas]:
    'Return time, temperature and wind speed (in SI units)'
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?{weather_query}&units=metric&APPID={key}'
        response = requests.get(url)
        if response.status_code == 200:
            json: dict = response.json()
            return WeatherMeas(int(time()), float(json['main']['temp']), float(json['wind']['speed']), int(json['wind']['deg']))
        else:
            print(response.status_code, response.text)
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    print(outside_weather('zip=94549'))
