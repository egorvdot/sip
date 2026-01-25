from enum import Enum
from fastapi import APIRouter, HTTPException, Query, Response, Request
from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)
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


class MetricKind(Enum):
    SYSTEM = "system"


@router.get("/metrics")
def get_metrics_endpoint(
    request: Request,
    kind: MetricKind = Query(..., description="Тип метрик"),
) -> str:
    """Эндпоинт для получения метрик системы."""
    registry = request.app.state.system_metrics_registry

    match kind:
        case MetricKind.SYSTEM:
            registry = request.app.state.system_metrics_registry

    try:
        metrics_output = generate_latest(registry)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate metrics: {str(e)}"
        )

    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
