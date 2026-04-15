from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://security_user:security_pass@postgres:5432/security_analytics"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "your-super-secret-key-change-this-in-production-min-32-chars"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()