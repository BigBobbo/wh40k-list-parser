"""Configuration settings for the Warhammer 40K List Builder."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    app_name: str = "Warhammer 40K List Builder"
    version: str = "0.1.0"
    debug: bool = True
    database_url: str = "sqlite:///./listmaker.db"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    api_prefix: str = "/api/v1"

    # Data paths
    wahapedia_data_path: str = "Wahapedia Data"

    class Config:
        """Pydantic settings config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
