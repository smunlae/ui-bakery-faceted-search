from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")

    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")
    default_limit: int = Field(20, alias="DEFAULT_LIMIT")
    max_limit: int = Field(100, alias="MAX_LIMIT")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()