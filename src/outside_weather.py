import os
from time import time
from typing import Optional, NamedTuple, Dict, List

import requests
from requests.models import Response

key = os.environ['OPEN_WEATHER_MAP_KEY']


class WeatherMeas(NamedTuple):
    local_time: int
    temperature: float
    wind_speed: float
    gust: float
    wind_dir: int
    pressure: float
    humidity: int
    main_weather: List[Dict[str, str]]


def outside_weather(weather_query='q=Oakland') -> Optional[WeatherMeas]:
    url = f'http://api.openweathermap.org/data/2.5/weather?{weather_query}&units=metric&APPID={key}'
    response: Response = requests.get(url)
    if response.status_code == 200:
        json: dict = response.json()
        print(json)
        main: dict = json['main']
        wind: dict = json['wind']
        return WeatherMeas(
            int(time()),
            float(main['temp']),
            _mps_to_kph(float(wind['speed'])),
            _mps_to_kph(float(wind.get('gust', 0))),
            int(wind['deg']),
            float(main['pressure']),
            int(main['humidity']),
            json['weather'],
        )
    else:
        print(response.status_code, response.text)
        return None


def _mps_to_kph(speed: float) -> float:
    return speed / 1000 * 3600


if __name__ == '__main__':
    print(outside_weather('zip=94549'))
