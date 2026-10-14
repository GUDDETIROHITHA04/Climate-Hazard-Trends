import os
from functools import lru_cache


class Settings:
    """Application settings, read once from environment variables."""

    def __init__(self) -> None:
        self.app_name = "Climate Hazard Trend Analyzer"
        self.api_prefix = "/api/v1"
        self.environment = os.getenv("APP_ENV", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        self.mongodb_uri = os.getenv("MONGODB_URI", "")
        self.mongodb_db = os.getenv("MONGODB_DB", "climate_hazards")
        self.cache_ttl_days = int(os.getenv("CACHE_TTL_DAYS", "30"))

        self.cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
        self.rate_limit = os.getenv("RATE_LIMIT", "20/minute")
        self.http_timeout = float(os.getenv("HTTP_TIMEOUT", "30"))

        # WMO climatological normal period used as the fixed reference for all hazards
        self.baseline_start = 1991
        self.baseline_end = 2020
        self.min_year = 1950  # ERA5 exists from 1940; 1950 keeps the record homogeneous

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
