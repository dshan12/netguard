from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    interface: str = "any"
    simulation_mode: str = "auto"
    packet_batch_size: int = 100
    packet_batch_timeout: float = 0.1

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    return Settings()