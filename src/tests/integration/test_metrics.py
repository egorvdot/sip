from unittest.mock import AsyncMock, patch
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families


async def test_metrics_with_valid_type(async_client):
    """Тест успешного получения метрик с правильным параметром kind=system"""

    response = await async_client.get("/metrics?kind=system")

    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST

    # Проверяем, что в ответе есть ожидаемые метрики
    content = response.content.decode("utf-8")

    # Проверяем наличие метрик от GC коллектора
    assert "python_gc_" in content or "# HELP python_gc_" in content

    # Проверяем наличие метрик от PLATFORM коллектора
    assert "python_info" in content or "# HELP python_info" in content

    # Проверяем наличие метрик от PROCESS коллектора
    assert "process_" in content or "# HELP process_" in content

    # Проверяем, что это действительно метрики в формате Prometheus
    assert "# TYPE" in content
    assert "# HELP" in content


async def test_metrics_without_type_parameter(async_client):
    """Тест запроса без параметра type (должна быть ошибка 422)"""
    response = await async_client.get("/metrics")

    # FastAPI вернет 422, так как параметр type обязательный
    assert response.status_code == 422

    # Проверяем детали ошибки
    error_detail = response.json()["detail"][0]
    assert error_detail["type"] == "missing"
    assert error_detail["loc"] == ["query", "kind"]


async def test_metrics_with_invalid_type(async_client):
    """Тест запроса с неверным значением параметра type"""
    response = await async_client.get("/metrics?kind=invalid")

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"


async def test_metrics_with_empty_type(async_client):
    """Тест запроса с пустым значением параметра type"""
    response = await async_client.get("/metrics?kind=")

    assert response.status_code == 422


async def test_metrics_with_different_case_type(async_client):
    """Тест запроса с разным регистром в параметре type"""
    response = await async_client.get("/metrics?kind=System")
    assert response.status_code == 422

    response = await async_client.get("/metrics?kind=SYSTEM")
    assert response.status_code == 422

    response = await async_client.get("/metrics?kind=systeM")
    assert response.status_code == 422


async def test_metrics_content_type_and_headers(async_client):
    """Тест правильности заголовков ответа"""
    response = await async_client.get("/metrics?kind=system")

    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST

    assert (
        response.headers["content-type"] == "text/plain; version=1.0.0; charset=utf-8"
    )


async def test_metrics_response_is_binary(async_client):
    """Тест, что ответ содержит бинарные данные"""
    response = await async_client.get("/metrics?kind=system")

    assert response.status_code == 200
    assert isinstance(response.content, bytes)

    # Проверяем, что можно декодировать как текст
    content = response.content.decode("utf-8")
    assert len(content) > 0


async def test_metrics_with_multiple_query_params(async_client):
    """Тест запроса с дополнительными параметрами (должны игнорироваться)"""
    response = await async_client.get("/metrics?kind=system&extra=param")

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "python_info" in content


async def test_weather_feels_like_metric(async_client, mock_weather_data):
    """Проверка сбора информации о погоде в метрику."""
    with patch(
        "app.api.fetch_weather_from_api",
        new_callable=AsyncMock,
        return_value=mock_weather_data,
    ):
        await async_client.get("/weather/London")
        response = await async_client.get("/metrics?kind=analytic")

        [family, *_] = text_string_to_metric_families(response.text)
        assert family.name == "temp_feels_like"
        [sample] = family.samples
        assert sample.value == 1.0
        assert sample.labels == {"feels_like": "warm"}
