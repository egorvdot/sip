import httpx
import pytest
from httpx import ASGITransport

from app.main import app


@pytest.fixture
async def async_client():
    """Асинхронный клиент для тестирования."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def mock_weather_data():
    """Мок ответа от внешнего API."""
    return {
        "current": {
            "temperature_2m": 22.5,
            "apparent_temperature": 21.0,
        }
    }
