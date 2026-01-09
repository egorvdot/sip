from fastapi import APIRouter
from pydantic import BaseModel

from app.weather import fetch_weather_from_api, get_weather_description


router = APIRouter()


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    description: str
    feels_like: float


@router.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    """Получение погоды для города."""
    data = await fetch_weather_from_api(city)
    temp = data["current"]["temperature_2m"]
    return WeatherResponse(
        city=city,
        temperature=temp,
        description=get_weather_description(temp),
        feels_like=data["current"]["apparent_temperature"],
    )
