from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SignBridge API"
    app_version: str = "0.1.0"
    allowed_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SIGNBRIDGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
