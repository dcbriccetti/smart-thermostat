import os
from time import time
from typing import Optional, NamedTuple, Dict, List, Any

import requests
from requests.models import Response

key = os.environ['OPEN_WEATHER_MAP_KEY']


class WeatherObservation(NamedTuple):
    local_time: int
    temperature: float
    wind_speed: float
    gust: float
    wind_dir: int
    pressure: float
    humidity: int
    main_weather: List[Dict[str, str]]


def outside_weather(weather_query='q=Oakland') -> Optional[WeatherObservation]:
    url = f'http://api.openweathermap.org/data/2.5/weather?{weather_query}&units=metric&APPID={key}'
    try:
        response: Response = requests.get(url)
        if response.status_code == 200:
            weather: Dict[str, Any] = response.json()
            main: Dict[str, Any] = weather['main']
            wind: Dict[str, Any] = weather['wind']

            return WeatherObservation(
                int(time()),
                float(main['temp']),
                _mps_to_kph(float(wind['speed'])),
                _mps_to_kph(float(wind.get('gust', 0))),
                int(wind['deg']),
                float(main['pressure']),
                int(main['humidity']),
                weather['weather'],
            )
        print(response.status_code, response.text)
    except requests.RequestException as ex:
        print(ex)

    return None


def _mps_to_kph(meters_per_second: float) -> float:
    km_per_second = meters_per_second / 1000
    seconds_per_hour = 3600
    return km_per_second * seconds_per_hour


if __name__ == '__main__':
    print(outside_weather('zip=94549'))
