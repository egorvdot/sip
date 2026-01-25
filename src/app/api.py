from enum import Enum
from fastapi import APIRouter, HTTPException, Query, Response, Request
from prometheus_client import (
    Counter,
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
async def get_weather(request: Request, city: str):
    """Получение погоды для города."""
    data = await fetch_weather_from_api(city)
    temp = data["current"]["temperature_2m"]
    temp_description = get_weather_description(temp)
    feels_like_counter: Counter = request.app.state.feels_like_counter
    feels_like_counter.labels(feels_like=temp_description).inc()

    return WeatherResponse(
        city=city,
        temperature=temp,
        description=temp_description,
        feels_like=data["current"]["apparent_temperature"],
    )


class MetricKind(Enum):
    SYSTEM = "system"
    ANALYTIC = "analytic"


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
        case MetricKind.ANALYTIC:
            registry = request.app.state.analytic_metrics_registry

    try:
        metrics_output = generate_latest(registry)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate metrics: {str(e)}"
        )

    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
