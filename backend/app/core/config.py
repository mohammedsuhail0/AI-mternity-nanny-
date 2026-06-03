from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "AI Maternal Monitor"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Local-first default so the MVP can run without external infrastructure.
    DATABASE_URL: str = "sqlite+aiosqlite:///./maternal_monitor.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ML
    MODEL_PATH: str = "ml/models/c_section_risk.pkl"
    PREDICTION_THRESHOLD: float = 0.65

    # Companion LLM
    COMPANION_LLM_API_KEY: str | None = None
    COMPANION_LLM_MODEL: str | None = None
    COMPANION_LLM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    COMPANION_LLM_TIMEOUT_SECONDS: float = 20.0


@lru_cache()
def get_settings() -> Settings:
    return Settings()
