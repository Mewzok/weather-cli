# Weather CLI

A simple Python command-line weather app that fetches the current conditions and a 3-day forecast for a city, region, or ZIP code using the Open-Meteo API.

## Description

This project is a lightweight terminal-based weather tool built in Python. It asks for a location, looks up the coordinates through the Open-Meteo geocoding service, then retrieves current weather and a short forecast for the next three days.

The program is designed to be easy to run locally and to provide a clean, readable output with basic visuals and color support in the terminal.

## Getting Started

### Dependencies

Before running the program, make sure you have:

* Python 3.10 or newer
* Windows, macOS, or Linux terminal
* Internet access for the Open-Meteo API requests

The project depends on the Python package listed in the requirements file:

* requests

### Installing

1. Open a terminal in the project folder.
2. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install the required dependency:

```powershell
pip install -r requirements.txt
```

### Executing program

Run the app from the project directory:

```powershell
python weather.py
```

When prompted, enter a city, region, or ZIP code, for example:

```text
Enter location or ZIP code (or type 'quit' to exit): Seattle
```

The program will display:

* current temperature
* humidity
* wind speed
* current weather condition
* a 3-day forecast

You can also type `quit`, `q`, or `exit` to close the program.

## Help

If the program does not return weather data:

* confirm that your internet connection is working
* verify the location name or ZIP code is spelled and typed correctly
* try a more specific place name if the first result is unclear
* if the service is unavailable, wait a moment and run the command again

If you want to re-run the app after an error, use:

```powershell
python weather.py
```

## Authors

Jonathan Kinney - [@Mewzok](https://github.com)

## Version History

* 1.0
    * Initial release

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

* Open-Meteo for the geocoding and weather APIs
* Python Requests for HTTP requests
* The original README template used as a structure for this project