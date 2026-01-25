from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


# ===== /weather/{city} =====


async def test_weather_success(async_client, mock_weather_data):
    """Успешное получение погоды."""
    with patch(
        "app.api.fetch_weather_from_api",
        new_callable=AsyncMock,
        return_value=mock_weather_data,
    ):
        response = await async_client.get("/weather/London")

        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "London"
        assert data["temperature"] == 22.5
        assert data["feels_like"] == 21.0
        assert data["description"] == "warm"


async def test_weather_cold_city(async_client):
    """Погода для холодного города."""
    cold_weather = {"current": {"temperature_2m": -5.0, "apparent_temperature": -10.0}}

    with patch(
        "app.api.fetch_weather_from_api",
        new_callable=AsyncMock,
        return_value=cold_weather,
    ):
        response = await async_client.get("/weather/Yakutsk")

        assert response.status_code == 200
        assert response.json()["description"] == "freezing"


async def test_weather_city_not_found(async_client):
    """Город не найден."""
    with patch(
        "app.api.fetch_weather_from_api",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=404, detail="City 'xyz' not found"),
    ):
        response = await async_client.get("/weather/xyz")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


# ===== /weather/{city} с monkeypatch =====


async def test_weather_success_monkeypatch(
    async_client, mock_weather_data, monkeypatch
):
    """Успешное получение погоды с использованием monkeypatch."""

    async def mock_fetch(city: str) -> dict:
        return mock_weather_data

    monkeypatch.setattr("app.api.fetch_weather_from_api", mock_fetch)

    response = await async_client.get("/weather/Paris")

    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert data["temperature"] == 22.5
    assert data["description"] == "warm"


async def test_weather_city_not_found_monkeypatch(async_client, monkeypatch):
    """Город не найден с использованием monkeypatch."""

    async def mock_fetch(city: str) -> dict:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")

    monkeypatch.setattr("app.api.fetch_weather_from_api", mock_fetch)

    response = await async_client.get("/weather/unknown")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
