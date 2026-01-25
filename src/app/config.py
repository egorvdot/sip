import yaml
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация сервиса."""

    app_name: str
    version: str
    host: str
    port: int
    environment: str
    debug: bool

    @classmethod
    def from_yaml(cls) -> "Settings":
        """Метод для создания pydantic объекта из yaml-конфига."""
        config_path = Path(__file__).parent.parent / "config" / "local.yaml"
        with open(config_path, "r") as cfg_file:
            config_data = yaml.safe_load(cfg_file)
        return cls(**config_data)


@lru_cache
def get_settings() -> Settings:
    """
    Получить настройки приложения.

    Используем @lru_cache чтобы создавать объект Settings только один раз.
    """
    return Settings.from_yaml()
