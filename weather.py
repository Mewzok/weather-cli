import requests
import urllib.parse

def get_location_data(location_query):
    # convert string with spaces into valid URL format
    encoded_query = urllib.parse.quote(location_query.strip())

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1&language=en&format=json"

    print(url)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                best_match = data["results"][0]
                return {
                    "name": best_match.get("name"),
                    "admin": best_match.get("admin1"), # state or region
                    "country": best_match.get("country"),
                    "latitude": best_match.get("latitude"),
                    "longitude": best_match.get("longitude")
                }
            return None
        
    except Exception as e:
        print(f"Geocoding error occured: {e}")
        return None

def get_todays_data(latitude, longitude):
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
    else:
        # later -  handle reponse error
        print("Failed to retrieve data")

    return data

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
    # retrieve desired location
    location_query = input("Enter location or zip code: ")

    # store name, state/region, country, latitude and longitude of user's selected location in a dictionary
    location_data = get_location_data(location_query)
    
    # retrieve today's weather report as json response data
    report_data = get_todays_data(location_data['latitude'], location_data['longitude'])

    if(report_data is not None):
        # display today's weather report
        current_weather = report_data['current']
        print(f"Current Weather Report in {location_data['name']}, {location_data['admin']}, {location_data['country']}:")
        print(f"Temperature: {current_weather['temperature_2m']}°F")
        print(f"Humidity: {current_weather['relative_humidity_2m']}")
        print(f"Wind Speed: {current_weather['wind_speed_10m']} mph")
        print(f"Weather Status: {convert_weather_code(current_weather['weather_code'])}")
    else:
        print("Something went wrong when retrieving location data. Please try again.")
        

if __name__ == "__main__":
    main()