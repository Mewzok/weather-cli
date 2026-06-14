import requests

# latitude and logitude required for open-meteo API request
latitude = 40.7608
longitude = -111.8910

# desired parameters
params = [
    "temperature_2m", # temperature
    "relative_humidity_2m", # humidity
    "wind_speed_10m", # wind speed
    "weather_code"  # weather summary, returned as code: 0 = clear sky, 1 = mainly clear, 2 = partly cloudy, 
                    # 3 = overcast, 45/48 = fog, 51/53/55 = light/moderate/dense drizzle, 
                    # 61/63/65 = slight/moderate/heavy rain, 66/67 = freezing rain, 
                    # 71/73/75 = slight/moderate/heavy snow fall, 77 = snow grains, 80/81/82 = rain showers,
                    # 85, 86 = snow showers, 95, 96, 99 = thunderstorm
    ]

# build API URL with latitude and longitude, including desired parameters under "current"
url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&temperature_unit=fahrenheit"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    current_weather = data['current']
    print(f"Tempurature: {current_weather['temperature_2m']}°F")
    print(f"Wind Speed: {current_weather['wind_speed_10m']} km/h")
    print(f"Weather Status: {current_weather['weather_code']}")
else:
    # later -  handle reponse error
    print("Failed to retrieve data")