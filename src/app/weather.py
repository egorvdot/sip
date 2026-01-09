import httpx
from fastapi import HTTPException


async def fetch_weather_from_api(city: str) -> dict:
    """Запрос к внешнему API погоды."""
    async with httpx.AsyncClient() as client:
        coordinates_response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko)"
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            },
        )
        coordinates_response.raise_for_status()
        [city_info, *_] = coordinates_response.json()
        latitude = float(city_info["lat"])
        longitude = float(city_info["lon"])
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code,apparent_temperature",
                "timezone": "auto",
            },
        )
        if response.status_code == 400:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
        response.raise_for_status()
        return response.json()


def get_weather_description(temp: float) -> str:
    """Текстовое описание погоды по температуре."""
    if temp < 0:
        return "freezing"
    elif temp < 10:
        return "cold"
    elif temp < 20:
        return "mild"
    elif temp < 30:
        return "warm"
    else:
        return "hot"
