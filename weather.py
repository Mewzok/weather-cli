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
RED = "\033[91m"

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
    if not isinstance(location_query, str) or not location_query.strip():
        raise ValueError("Please enter a location or ZIP code before continuing.")

    encoded_query = urllib.parse.quote(location_query.strip())
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1&language=en&format=json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("The location lookup timed out. Please try again in a moment.")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"The location service returned an error: {exc}")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Unable to reach the location service: {exc}")
    except ValueError as exc:
        raise RuntimeError("The location service returned invalid data.") from exc

    if not isinstance(data, dict) or not isinstance(data.get("results"), list) or not data["results"]:
        raise ValueError("No matching location was found. Please try another city, region, or ZIP code.")

    best_match = data["results"][0]

    if not isinstance(best_match, dict):
        raise RuntimeError("The location service returned an unexpected response format.")

    latitude = best_match.get("latitude")
    longitude = best_match.get("longitude")

    if latitude is None or longitude is None:
        raise RuntimeError("The location service returned incomplete coordinates.")

    return {
        "name": best_match.get("name") or "Unknown location",
        "admin": best_match.get("admin1"),
        "country": best_match.get("country"),
        "latitude": latitude,
        "longitude": longitude,
    }

def get_weather_data(latitude, longitude):
    if latitude is None or longitude is None:
        raise ValueError("Location coordinates are missing, so weather data cannot be loaded.")
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise ValueError("Location coordinates are invalid.")

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

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("The weather service timed out. Please try again in a moment.")
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            raise RuntimeError("The weather service is rate-limiting requests. Please wait a moment and try again.") from exc
        raise RuntimeError(f"The weather service returned an error: {exc}") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Network connection failed while reaching the weather service. Please check your internet connection.") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Unable to reach the weather service: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("The weather service returned invalid JSON.") from exc

    if not isinstance(data, dict) or "current" not in data or "daily" not in data:
        raise RuntimeError("The weather service returned incomplete data.")

    if not isinstance(data.get("daily"), dict) or not isinstance(data["daily"].get("time"), list):
        raise RuntimeError("The weather forecast data is missing its daily timeline.")

    return data

def convert_weather_code(weather_code):
    status_map = {
        0: "Clear Sky",
        1: "Mostly Clear Sky",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy with Deposits",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        56: "Freezing Drizzle",
        57: "Dense Freezing Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Light Snowfall",
        73: "Moderate Snowfall",
        75: "Heavy Snowfall",
        77: "Snow Grains",
        80: "Light Rain Showers",
        81: "Moderate Rain Showers",
        82: "Heavy Rain Showers",
        85: "Light Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Light Hail",
        99: "Thunderstorm with Heavy Hail",
    }

    return status_map.get(weather_code, "Unknown Weather Condition")

def convert_weather_code_legacy(weather_code):
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
    try:
        current_weather = report_data['current']
        forecast = report_data['daily']
        day_labels = format_forecast_days(forecast['time'])
    except (TypeError, KeyError, ValueError) as exc:
        raise RuntimeError("The weather response is incomplete and cannot be displayed.") from exc

    if not isinstance(current_weather, dict):
        raise RuntimeError("Current weather data is missing or invalid.")

    if not isinstance(forecast, dict):
        raise RuntimeError("Forecast data is missing or invalid.")

    required_daily_fields = ("temperature_2m_max", "temperature_2m_min", "weather_code", "time")
    missing_daily_fields = [field for field in required_daily_fields if field not in forecast or forecast[field] is None]
    if missing_daily_fields:
        raise RuntimeError("The forecast is missing one or more required values.")

    if not isinstance(forecast['time'], list) or len(forecast['time']) < 3:
        raise RuntimeError("The forecast timeline is incomplete.")

    for key in ("temperature_2m_max", "temperature_2m_min", "weather_code"):
        if not isinstance(forecast[key], list) or len(forecast[key]) < 3:
            raise RuntimeError("The daily forecast values are incomplete.")

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
    while True:
        try:
            location_query = input("Enter location or ZIP code (or type 'quit' to exit): ").strip()

            if not location_query:
                print("Please enter a location or ZIP code before continuing.")
                continue

            if location_query.lower() in {"q", "quit", "exit"}:
                print("\nGoodbye.")
                return

            location_data = get_location_data(location_query)
            report_data = get_weather_data(location_data['latitude'], location_data['longitude'])
            display_weather_data(location_data, report_data)
            return

        except ValueError as exc:
            print(str(exc))
        except RuntimeError as exc:
            print(str(exc))
        except KeyboardInterrupt:
            print("Weather lookup interrupted. Exiting gracefully.")
            return
        except EOFError:
            print("Input stream ended unexpectedly. Please run the command again.")
            return
        except requests.exceptions.RequestException as exc:
            print("A network problem occurred while contacting the weather service.", str(exc))
        except Exception as exc:
            print("An unexpected error occurred.", str(exc))

    
if __name__ == "__main__":
    main()