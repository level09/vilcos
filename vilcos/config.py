# vilcos/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    debug: bool = True
    database_url: str
    supabase_url: str
    supabase_key: str
    secret_key: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
