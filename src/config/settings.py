"""
src/config/settings.py

Production-ready configuration management for the "Real-Time Cyber Threat Detection and Response System".
This file uses Pydantic for validation and environment-specific settings. Secrets and sensitive data are
managed via environment variables to ensure security. Sensible defaults are provided for development and
staging environments, while production requires explicit configuration via environment variables.

Environment-specific settings are loaded based on the `ENVIRONMENT` variable, which can be one of:
- "development"
- "staging"
- "production"

Usage:
- Define environment variables in your system or use a `.env` file for local development.
- Use Pydantic's validation to ensure all required settings are properly configured.
"""

import os
from pydantic import BaseSettings, Field, validator, AnyHttpUrl, PostgresDsn, RedisDsn
from typing import List, Optional


class CommonSettings(BaseSettings):
    """
    Common settings shared across all environments.
    """
    APP_NAME: str = "Real-Time Cyber Threat Detection and Response System"
    ENVIRONMENT: str = Field(..., env="ENVIRONMENT", description="Application environment: development, staging, production")
    DEBUG: bool = Field(False, description="Enable or disable debug mode")
    LOG_LEVEL: str = Field("INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    ALLOWED_HOSTS: List[str] = Field(["*"], description="List of allowed hosts for the application")

    # Database settings
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL", description="Database connection URL")

    # Redis settings
    REDIS_URL: RedisDsn = Field(..., env="REDIS_URL", description="Redis connection URL for caching and task queues")

    # Security settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY", description="Secret key for cryptographic operations")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Access token expiration time in minutes")
    CORS_ORIGINS: List[AnyHttpUrl] = Field([], description="Allowed CORS origins")

    # Performance settings
    WORKER_COUNT: int = Field(4, description="Number of worker processes for the application")
    REQUEST_TIMEOUT: int = Field(30, description="Request timeout in seconds")
    MAX_CONNECTIONS: int = Field(100, description="Maximum number of database connections")

    # Email settings
    EMAIL_HOST: str = Field(..., env="EMAIL_HOST", description="SMTP server host")
    EMAIL_PORT: int = Field(587, description="SMTP server port")
    EMAIL_USERNAME: str = Field(..., env="EMAIL_USERNAME", description="SMTP server username")
    EMAIL_PASSWORD: str = Field(..., env="EMAIL_PASSWORD", description="SMTP server password")
    EMAIL_USE_TLS: bool = Field(True, description="Use TLS for email communication")

    # Validation for environment
    @validator("ENVIRONMENT")
    def validate_environment(cls, value):
        if value not in {"development", "staging", "production"}:
            raise ValueError("ENVIRONMENT must be one of 'development', 'staging', or 'production'")
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentSettings(CommonSettings):
    """
    Development-specific settings.
    """
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    DATABASE_URL: PostgresDsn = "postgresql://dev_user:dev_password@localhost/dev_db"
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key"
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]


class StagingSettings(CommonSettings):
    """
    Staging-specific settings.
    """
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = ["staging.example.com"]
    DATABASE_URL: PostgresDsn = "postgresql://staging_user:staging_password@staging-db/staging_db"
    REDIS_URL: RedisDsn = "redis://staging-redis:6379/0"
    SECRET_KEY: str = Field(..., env="STAGING_SECRET_KEY")
    CORS_ORIGINS: List[AnyHttpUrl] = ["https://staging-frontend.example.com"]


class ProductionSettings(CommonSettings):
    """
    Production-specific settings.
    """
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    ALLOWED_HOSTS: List[str] = ["example.com", "api.example.com"]
    DATABASE_URL: PostgresDsn = Field(..., env="PROD_DATABASE_URL")
    REDIS_URL: RedisDsn = Field(..., env="PROD_REDIS_URL")
    SECRET_KEY: str = Field(..., env="PROD_SECRET_KEY")
    CORS_ORIGINS: List[AnyHttpUrl] = ["https://frontend.example.com"]


def get_settings() -> CommonSettings:
    """
    Load the appropriate settings class based on the ENVIRONMENT variable.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "development":
        return DevelopmentSettings()
    elif environment == "staging":
        return StagingSettings()
    elif environment == "production":
        return ProductionSettings()
    else:
        raise ValueError(f"Invalid ENVIRONMENT: {environment}")


# Instantiate settings for the current environment
settings = get_settings()