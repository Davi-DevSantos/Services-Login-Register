import json
from functools import lru_cache
from typing import Any

from pydantic import AnyHttpUrl, TypeAdapter, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "API Login"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    # Use Any to avoid pydantic-settings json decoding for list; parsed in validator
    cors_origins: Any = []
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[AnyHttpUrl]:
        if v is None or v == "":
            return []
        if isinstance(v, list):
            # validate each as AnyHttpUrl
            adapter = TypeAdapter(list[AnyHttpUrl])
            return adapter.validate_python(v)
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            # JSON array like '["http://a","http://b"]'
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    adapter = TypeAdapter(list[AnyHttpUrl])
                    return adapter.validate_python(parsed)
                except (json.JSONDecodeError, ValueError):
                    pass
            # comma separated
            parts = [s.strip() for s in v.split(",") if s.strip()]
            adapter = TypeAdapter(list[AnyHttpUrl])
            return adapter.validate_python(parts)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
