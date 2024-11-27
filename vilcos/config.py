# vilcos/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Vilcos Framework"
    debug: bool = False
    database_url: str
    secret_key: str
    redis_url: str = "redis://localhost:6379"
    
    # Session settings
    session_cookie_name: str = "vilcos_session"
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    session_cookie_max_age: int = 14 * 24 * 60 * 60  # 14 days in seconds

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
