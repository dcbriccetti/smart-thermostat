import requests

ORINDA = 'D3835'
url = "https://api.weather.gov/points/37.9039,-122.0979/"

querystring = {}

headers = {}

response = requests.request("GET", url, headers=headers, params=querystring)
j = response.json()
fc = j['properties']['forecast']
print(fc)
response = requests.request("GET", fc, headers=headers, params=querystring)
response = requests.request("GET", 'https://api.weather.gov/gridpoints/MTR/100,130/', headers=headers, params=querystring)
j = response.json()
print('{:.1f} °C'.format(j['properties']['temperature']['values'][0]['value']))
