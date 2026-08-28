# Omarchy Weather

Weather plugin for Omarchy, displayed as a widget in the top bar.

## Features

- Current temperature and weather icon.
- Feels-like temperature, wind speed, and humidity.
- Forecast for the next 7 days.
- Detailed forecast for the current day, including high, low, and rain probability.
- Search for and change the location directly from the panel.
- Automatic location detection when no city is configured.
- Metric and imperial unit support.
- Configurable automatic refresh interval.

## Usage

Click the weather widget to open the panel.

- Left-click: open or close the panel.
- Middle-click: refresh the weather data.
- Right-click: send the weather summary as a notification.
- In the panel, click the city name to search for another location.

The plugin uses Open-Meteo for daily forecasts and wttr.in for current conditions and as a fallback.

## Configuration

Settings are read through the Omarchy module system. Available options include:

- `unit`: `metric` ou `imperial`.
- `refreshMinutes`: intervalo de atualização em minutos.

The selected location is stored at:

```text
~/.local/state/omarchy/settings/weather.json
```

This file is managed by the `omarchy-weather-location` command.

## Project structure

- `manifest.json`: plugin metadata and entry point.
- `BarWidget.qml`: widget displayed in the bar.
- `Panel.qml`: pop-up panel, location editing, and network requests.
- `Model.js`: weather data, temperature, and icon processing.

## Recent changes

- Expanded the future forecast from 3 to 7 days.
- Updated the daily query to fetch today and the following 7 days.
- Added a dedicated current-day forecast section below the future forecast.
- The current-day forecast displays the icon, high, low, and rain probability when provided by the API.
- Added separate data normalization for today and future forecast days.
- Reorganized the forecast into compact cards that fit inside the panel.

## Development

The plugin has no local Node.js dependencies. To validate the data-processing functions:

```bash
node --check Model.js
```

The panel should be tested inside an Omarchy/Quickshell session because it depends on the `qs.Commons`, `qs.Ui`, and shell component modules.
