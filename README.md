# Omarchy Weather

Weather plugin for Omarchy, displayed as a widget in the top bar.

## Features

- Current temperature and weather icon.
- Feels-like temperature, wind speed, and humidity.
- Forecast for the next 5 days, including yesterday and today.
- Detailed forecast for the current day, including high, low, and rain probability.
- Hourly forecast for the current day with a draggable horizontal scrollbar.
- Activity forecasts for hiking, cycling, and running.
- Search for and change the location directly from the panel.
- Automatic location detection when no city is configured.
- Metric and imperial unit support.
- Configurable automatic refresh interval.

## Installation

Install this plugin from the `guiestrela/weather` GitHub repository with the standard Omarchy plugin manager:

```bash
omarchy plugin add https://github.com/guiestrela/weather.git --enable
```

The `--enable` option enables the plugin and adds its bar widget automatically. To install it without enabling it immediately, omit `--enable`, then run:

```bash
omarchy plugin enable io.github.guiestrela.weather --section right
```

Verify the installation with:

```bash
omarchy plugin list
omarchy plugin validate ~/.config/omarchy/plugins/io.github.guiestrela.weather
```

To update the installed plugin:

```bash
omarchy plugin update io.github.guiestrela.weather
```

To remove the plugin:

```bash
omarchy plugin remove io.github.guiestrela.weather
```

## Usage

Click the weather widget to open the panel.

- Left-click: open or close the panel.
- Middle-click: refresh the weather data.
- Right-click: send the weather summary as a notification.
- In the panel, click the city name to search for another location.

The plugin uses Open-Meteo for daily forecasts and wttr.in for current conditions and as a fallback.

## Configuration

Settings are read through the Omarchy module system. Available options include:

- `unit`: `metric` or `imperial`.
- `refreshMinutes`: refresh interval in minutes.

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

- Updated the daily view to show yesterday, today, and the following 5 days.
- Reduced the daily query to fetch only the displayed forecast range.
- Added a dedicated current-day forecast section below the future forecast.
- The current-day forecast displays the icon, high, low, and rain probability when provided by the API.
- Added an hourly forecast strip with a draggable horizontal scrollbar.
- Added hiking, cycling, and running recommendations based on rain, wind, temperature, and storm conditions.
- Added separate data normalization for today and future forecast days.
- Reorganized the forecast into an aligned daily list with day/night symbols.

## Development

The plugin has no local Node.js dependencies. To validate the data-processing functions:

```bash
node --check Model.js
```

The panel should be tested inside an Omarchy/Quickshell session because it depends on the `qs.Commons`, `qs.Ui`, and shell component modules.
