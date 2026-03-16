"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration loaded from environment — never use os.getenv directly."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = ""

    # Supabase
    supabase_service_key: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # Scheduler
    fetch_cron: str = "0 6,18 * * *"

    # App
    environment: str = "development"
    log_level: str = "INFO"

    # CORS — comma-separated list of allowed origins
    cors_origins_raw: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    # Redis (Phase 5)
    redis_url: str = ""


settings = Settings()
