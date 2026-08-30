# Omarchy Weather

Weather plugin for Omarchy, displayed as a widget in the top bar.

## Preview

### Metric units

![Omarchy Weather panel showing metric units, forecast, activity recommendations, and radar map](preview.png)

### Imperial units

![Omarchy Weather panel showing imperial units, forecast, activity recommendations, and radar map](preview2.png)

## Features

- Current temperature and weather icon.
- Feels-like temperature, wind speed, and humidity.
- Forecast for the next 5 days, including yesterday and today.
- Detailed forecast for the current day, including high, low, and rain probability.
- Hourly forecast for the current day with a draggable horizontal scrollbar.
- Activity forecasts for hiking, cycling, running, and camping.
- Live weather radar always enabled and centered on the configured location.
- Satellite imagery with CARTO city labels, roads, and map outlines underneath the radar.
- Search for and change the location directly from the panel.
- Automatic location detection when no city is configured.
- Metric and imperial unit support.
- Configurable automatic refresh interval.

## Installation

Install and configure the plugin with the standard Omarchy plugin manager:

```bash
omarchy plugin add https://github.com/guiestrela/weather.git --enable && omarchy plugin disable omarchy.weather && omarchy bar move io.github.guiestrela.weather --section center --index 4 && omarchy restart shell
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
- Added a dedicated current-day forecast section above the daily forecast.
- The current-day forecast displays the icon, high, low, and rain probability when provided by the API.
- Added an hourly forecast strip with a draggable horizontal scrollbar.
- Added hiking, cycling, running, and camping recommendations based on rain, wind, temperature, and storm conditions.
- Added a live RainViewer radar section below the activity forecasts.
- Kept the radar layer permanently enabled without layer-switching buttons.
- Kept the detailed map zoom at level 10 while scaling RainViewer's level-7
  radar tiles to fit the map.
- Added separate data normalization for today and future forecast days.
- Reorganized the forecast into an aligned daily list with day/night symbols.

## Development

The plugin has no local Node.js dependencies. To validate the data-processing functions:

```bash
node --check Model.js
```

The panel should be tested inside an Omarchy/Quickshell session because it depends on the `qs.Commons`, `qs.Ui`, and shell component modules.

Radar imagery is provided by [RainViewer](https://www.rainviewer.com/) and is
available for personal, educational, and small community use.
