from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    # Redis server hostname or IP address (default: 'localhost', can be set via REDIS_HOST in .env)
    host: str = "localhost"
    # Redis server port (default: 6379, can be set via REDIS_PORT in .env)
    port: int = 6379
    # Redis database number (default: 0, can be set via REDIS_DB in .env)
    db: int = 0

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="ignore"
    )
