from requests import request

response = request("GET", "https://w1.weather.gov/data/METAR/KCCR.1.txt")
lines = response.text.split("\n")
fields = lines[3].split(" ")
wind_speed_knots = int(fields[3][3:5])
wind_speed_knots = 12
wind_speed_kph = wind_speed_knots * 1.852
temp_dew = fields[6]
temperature = temp_dew.split("/")[0]
print(temperature)
print('{:.1f} kph'.format(wind_speed_kph))
