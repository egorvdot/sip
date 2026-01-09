import pytest

from app.weather import get_weather_description


@pytest.mark.parametrize(
    "temp,expected",
    [
        (-15, "freezing"),
        (-1, "freezing"),
        (0, "cold"),
        (5, "cold"),
        (10, "mild"),
        (15, "mild"),
        (20, "warm"),
        (25, "warm"),
        (30, "hot"),
        (40, "hot"),
    ],
)
def test_weather_description_temperature_ranges(temp, expected):
    """Проверка всех температурных диапазонов."""
    assert get_weather_description(temp) == expected
