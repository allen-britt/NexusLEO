"""Application configuration."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/nexusleo"


@lru_cache
def get_settings() -> Settings:
    return Settings()
