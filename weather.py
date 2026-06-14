import requests

def convert_weather_code(weather_code):
    status = ""

    match weather_code:
        case 0:
            status = "Clear Sky"
        case 1:
            status = "Mostly Clear Sky"
        case 2:
            status = "Partly Cloudy"
        case 3:
            status = "Overcast"
        case 45 | 48:
            status = "Foggy"
        case 51:
            status = "Light Drizzle"
        case 53:
            status = "Moderate Drizzle"
        case 55:
            status = "Dense Drizzle"
        case 56 | 57:
            status = "Freezing Drizzle"
        case 61:
            status = "Light Rain"
        case 63:
            status = "Moderate Rain"
        case 65:
            status = "Heavy Rain"
        case 66 | 67:
            status = "Freezing Rain"
        case 71:
            status = "Light Snowfall"
        case 73:
            status = "Moderate Snowfall"
        case 75:
            status = "Heavy Snowfall"
        case 77:
            status = "Snow Grains"
        case 80:
            status = "Light Rain Showers"
        case 81:
            status = "Moderate Rain Showers"
        case 82:
            status = "Heavy Rain Showers"
        case 85:
            status = "Light Snow Showers"
        case 86:
            status = "Heavy Snow Showers"
        case 95:
            status = "Thunderstorm"
        case 96:
            status = "Thunderstorm with Light Hail"
        case 99:
            status = "Thunderstorm with Heavy Hail"

    return status

def main():
    location = ""

    # latitude and logitude required for open-meteo API request
    latitude = 40.7608
    longitude = -111.8910

    # desired parameters
    params = [
        "temperature_2m", # temperature
        "relative_humidity_2m", # humidity
        "wind_speed_10m", # wind speed
        "weather_code"  # weather summary, returned as code, see convert_weather_code function for detailed code numbers
        ]

    param_string = ",".join(params)

    # build API URL with latitude and longitude, including desired parameters under "current"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current={param_string}&temperature_unit=fahrenheit&wind_speed_unit=mph"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        current_weather = data['current']
        print(f"Current Weather Report in {location}:")
        print(f"Tempurature: {current_weather['temperature_2m']}°F")
        print(f"Humidity: {current_weather['relative_humidity_2m']}")
        print(f"Wind Speed: {current_weather['wind_speed_10m']} mph")
        print(f"Weather Status: {convert_weather_code(current_weather['weather_code'])}")
    else:
        # later -  handle reponse error
        print("Failed to retrieve data")


if __name__ == "__main__":
    main()