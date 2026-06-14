import re
import requests
import urllib.parse
import sys
from datetime import datetime

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GOLD = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"

# styling helper functions ----------------------------

def visible_len(text):
    return len(re.sub(r"\x1b\[[0-9;]*m", "", text))


def colorize(text, *codes):
    if not sys.stdout.isatty():
        return text
    return "".join(codes) + text + RESET


def print_banner(title, subtitle):
    width = max(visible_len(title) + 2, visible_len(subtitle)) + 4
    border = "═" * width

    print(colorize("╔" + border + "╗", CYAN))
    print(colorize("║" + title.center(width) + "║", CYAN))
    if subtitle:
        print(colorize("║" + subtitle.center(width) + "║", DIM))
    print(colorize("╚" + border + "╝", CYAN))


def print_panel(title, lines, accent=CYAN):
    width = max(visible_len(title), max((visible_len(line) for line in lines), default=0)) + 4

    print(f"{accent}┌{'─' * width}┐{RESET}")
    print(f"{accent}│ {BOLD}{title}{RESET}{accent}{' ' * (width - visible_len(title) - 1)}│{RESET}")
    print(f"{accent}├{'─' * width}┤{RESET}")

    for line in lines:
        pad = width - visible_len(line) - 1
        print(f"{accent}│ {RESET}{line}{' ' * pad}{accent}│{RESET}")

    print(f"{accent}└{'─' * width}┘{RESET}")

# end of styling helper functions -------------------------

def get_location_data(location_query):
    # convert string with spaces into valid URL format
    encoded_query = urllib.parse.quote(location_query.strip())

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1&language=en&format=json"

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

def get_weather_data(latitude, longitude):
    # parameters for today's weather report
    today_params = [
        "temperature_2m", # temperature
        "relative_humidity_2m", # humidity
        "wind_speed_10m", # wind speed
        "weather_code",  # weather summary, returned as code, see convert_weather_code function for detailed code numbers
    ]

    # parameters for 3 day forecast report
    daily_params = [
        "temperature_2m_max", # temp high
        "temperature_2m_min", # temp low
        "weather_code", # weather code
    ]

    # build API URL with latitude and longitude, including desired parameters under "current"
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current={','.join(today_params)}"
        f"&daily={','.join(daily_params)}"
        f"&forecast_days=3"
        f"&temperature_unit=fahrenheit"
        f"&wind_speed_unit=mph"
        f"&timezone=auto"
    )

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

def format_forecast_days(date_strings):
    labels = []

    for i, date_str in enumerate(date_strings):
        if i == 0:
            labels.append("Today")
        elif i == 1:
            labels.append("Tomorrow")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            labels.append(date_obj.strftime("%A"))

    return labels

def display_weather_data(location_data, report_data):
    current_weather = report_data['current']
    forecast = report_data['daily']
    day_labels = format_forecast_days(forecast['time'])

    location_name = location_data.get('name', 'Your area')
    region = ", ".join(part for part in [location_data.get('admin'), location_data.get('country')] if part)
    heading = f"Weather Outlook for {location_name}"
    subtitle = region if region else "3-day forecast"

    print()
    print_banner(heading, subtitle)
    print()

    current_lines = [
        f"{colorize('Temperature', BOLD)}: {colorize(str(current_weather['temperature_2m']) + '°F', GOLD)}",
        f"{colorize('Humidity', BOLD)}: {current_weather['relative_humidity_2m']}%",
        f"{colorize('Wind Speed', BOLD)}: {current_weather['wind_speed_10m']} mph",
        f"{colorize('Condition', BOLD)}: {colorize(convert_weather_code(current_weather['weather_code']), GREEN)}",
    ]
    print_panel("Current Conditions", current_lines, accent=CYAN)
    print()

    for i in range(3):
        forecast_lines = [
            f"{colorize('High', BOLD)}: {forecast['temperature_2m_max'][i]}°F",
            f"{colorize('Low', BOLD)}: {forecast['temperature_2m_min'][i]}°F",
            f"{colorize('Weather', BOLD)}: {colorize(convert_weather_code(forecast['weather_code'][i]), BLUE)}",
        ]
        title = f"{day_labels[i]}'s Forecast"
        print_panel(title, forecast_lines, accent=GREEN)
        print()

    return None

def main():
    # retrieve desired location
    location_query = input("Enter location or zip code: ")

    # store name, state/region, country, latitude and longitude of user's selected location in a dictionary
    location_data = get_location_data(location_query)
    
    # retrieve today's weather report as json response data
    report_data = get_weather_data(location_data['latitude'], location_data['longitude'])

    # display today's weather report
    if(report_data is not None):
        display_weather_data(location_data, report_data)
    else:
        print("Something went wrong when retrieving location data. Please try again.")

    
if __name__ == "__main__":
    main()