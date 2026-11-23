
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# BaseSettings reads environment variables or a .env file in the working
# directory.
class Settings(BaseSettings):
    GROQ_API_KEY: str
    TAVILY_API_KEY: str

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    APP_NAME: str = "Noida Research Agent"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Read environment settings once and reuse them for the lifetime of the process.
@lru_cache
def get_settings():
    # Caching avoids re-reading configuration every time a tool needs a key.
    return Settings()

