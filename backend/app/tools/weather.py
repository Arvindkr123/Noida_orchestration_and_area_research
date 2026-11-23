from typing import Any

import httpx

from app.schemas.research import ResearchIntent, ResearchPlan


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather(
    intent: ResearchIntent,
    _plan: ResearchPlan,
) -> dict[str, Any]:
    """Fetch current conditions and a short forecast for Noida."""
    # The forecast API needs coordinates, so first resolve the city name.
    async with httpx.AsyncClient(timeout=20) as client:
        geocoding_response = await client.get(
            GEOCODING_URL,
            params={
                "name": intent.city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        geocoding_response.raise_for_status()
        geocoding_payload = geocoding_response.json()
        if not isinstance(geocoding_payload, dict):
            raise ValueError("Weather provider returned invalid geocoding data")
        locations = geocoding_payload.get("results")

        # Stop here with a clear error if geocoding cannot provide coordinates.
        if not isinstance(locations, list) or not locations:
            raise ValueError(f"Could not find weather coordinates for {intent.city}")

        location = locations[0]
        if not isinstance(location, dict):
            raise ValueError("Weather provider returned an invalid location")

        latitude = location.get("latitude")
        longitude = location.get("longitude")
        if not isinstance(latitude, (int, float)) or not isinstance(
            longitude, (int, float)
        ):
            raise ValueError("Weather provider returned invalid coordinates")

        # Use the resolved coordinates to request current and three-day data.
        forecast_response = await client.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,apparent_temperature,"
                    "precipitation,weather_code,wind_speed_10m"
                ),
                "daily": (
                    "weather_code,temperature_2m_max,temperature_2m_min,"
                    "precipitation_probability_max"
                ),
                "timezone": "Asia/Kolkata",
                "forecast_days": 3,
            },
        )
        forecast_response.raise_for_status()
        forecast = forecast_response.json()

    # Check provider response shapes before building the API's result object.
    if not isinstance(forecast, dict):
        raise ValueError("Weather provider returned invalid forecast data")

    current = forecast.get("current")
    daily = forecast.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise ValueError("Weather provider returned an incomplete forecast")

    return {
        "provider": "Open-Meteo",
        "location": {
            "name": location.get("name", intent.city),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": forecast.get("timezone", "Asia/Kolkata"),
        },
        "current": current,
        "current_units": forecast.get("current_units", {}),
        "daily": daily,
        "daily_units": forecast.get("daily_units", {}),
    }