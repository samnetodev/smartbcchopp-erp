import json
from typing import cast

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "SmartBcChopp ERP"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me"
    CORS_ORIGINS: str = '["*"]'

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/smartbcchopp"
    DATABASE_SYNC_URL: str = "postgresql://user:password@localhost:5432/smartbcchopp"

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480

    LOG_FORMAT: str = "text"  # "text" or "json"

    WHATSAPP_BASE_URL: str = "http://localhost:8080"
    WHATSAPP_API_KEY: str = ""
    WHATSAPP_INSTANCE: str = "smartbcchopp"
    WHATSAPP_WEBHOOK_URL: str = ""

    VIA_CEP_URL: str = "https://viacep.com.br/ws"
    GOOGLE_MAPS_API_KEY: str = ""
    NFE_API_KEY: str = ""
    PAGARME_API_KEY: str = ""

    def model_post_init(self, __context: object) -> None:
        self._normalize_database_urls()

    def _normalize_database_urls(self) -> None:
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = "postgresql://" + self.DATABASE_URL[len("postgres://"):]
        if self.DATABASE_SYNC_URL.startswith("postgres://"):
            self.DATABASE_SYNC_URL = "postgresql://" + self.DATABASE_SYNC_URL[len("postgres://"):]
        if "+" not in self.DATABASE_URL.split("://", 1)[0]:
            self.DATABASE_URL = self.DATABASE_URL.replace("://", "+asyncpg://", 1)

    @property
    def cors_origins_list(self) -> list[str]:
        return cast("list[str]", json.loads(self.CORS_ORIGINS))


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
