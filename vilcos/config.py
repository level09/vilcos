# vilcos/config.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Vilcos Framework"
    debug: bool = False
    
    # Database settings
    database_url: str = Field(..., description="PostgreSQL database URL")
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis URL for session storage"
    )
    
    # Security settings
    secret_key: str = Field(..., description="Secret key for session encryption")
    
    # Session settings
    session_cookie_name: str = "vilcos_session"
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    session_cookie_max_age: int = 14 * 24 * 60 * 60  # 14 days in seconds

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("secret_key must be at least 32 characters long")
        return v

    @validator("database_url")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("database_url must be a valid PostgreSQL URL")
        return v

    @validator("redis_url")
    def validate_redis_url(cls, v):
        if not v.startswith("redis://"):
            raise ValueError("redis_url must be a valid Redis URL")
        return v

    @validator("session_cookie_max_age", pre=True)
    def validate_session_cookie_max_age(cls, v):
        if isinstance(v, str):
            try:
                return int(v.strip())
            except ValueError:
                raise ValueError("session_cookie_max_age must be a valid integer")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # This will ignore extra env vars like supabase_url
    )

# Initialize settings
settings = Settings()
