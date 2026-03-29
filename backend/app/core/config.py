from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Vani-Flow API"
    env: str = "dev"
    log_level: str = "INFO"

    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str | None = None

    drift_mode: str = "off"

    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()

