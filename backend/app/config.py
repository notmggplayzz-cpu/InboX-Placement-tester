import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Database
    database_url: str = "sqlite:///./inbox_tester.db"

    # Gmail API
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/api/accounts/callback"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Encryption
    encryption_key: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    frontend_url: str = "http://localhost:5173"

    # Gmail Configuration
    gmail_api_max_concurrent: int = 5
    gmail_api_rate_limit: int = 100
    gmail_scan_timeout_seconds: int = 60
    send_email_method: Literal["gmail_api", "smtp"] = "gmail_api"

    # SMTP (if using SMTP method)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_from_email: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Features
    enable_webhook_notifications: bool = False
    enable_scheduled_tests: bool = True
    auto_rescan_enabled: bool = True
    auto_rescan_interval_seconds: int = 10
    auto_rescan_timeout_minutes: int = 5

    # Redis (optional)
    redis_url: str = "redis://localhost:6379/0"
    enable_redis: bool = False

    # Timeouts
    request_timeout_seconds: int = 30
    db_pool_size: int = 5
    db_max_overflow: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
