import os
import yaml
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.log_settings import LogSettings
from src.config.redis_settings import RedisSettings
from src.config.tea_token_settings import TeaTokenSettings


class AppSettings(BaseModel):
    environment: str = "dev"
    project_name: str
    api_prefix: str = "/api"
    openapi_prefix: str = ""
    version: str = "0.1.0"
    debug: bool = False
    description: str | None = None
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    reload: bool = False  # Default for uvicorn/fastapi
    workers: int = 1     # Default for uvicorn/fastapi

    host: str
    port: int
    tea_token_url: str
    region: str

    model_config = SettingsConfigDict(
        extra="ignore"
    )

class Settings(BaseSettings):
    redis: RedisSettings
    app: AppSettings
    log_settings: LogSettings
    tea_credentials: TeaTokenSettings
    # Store any additional config properties
    extra_config: dict = {}

    IS_ALLOWED_CREDENTIALS: bool = True
    ALLOWED_ORIGINS: list[str] = ["*"]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    @classmethod
    def load(cls, config_file_path: str):
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Config file not found: {config_file_path}")

        with open(config_file_path, 'r') as f:
            data = yaml.safe_load(f)

        app_data = data.get('app_settings', {})
        log_data = data.get('log_settings', {})
        redis = RedisSettings()
        tea_credentials = TeaTokenSettings()

        if os.getenv('LOCAL_HOST'):
            app_data['host'] = os.getenv('LOCAL_HOST')
        if os.getenv('LOCAL_PORT'):
            app_data['port'] = os.getenv('LOCAL_PORT')

        # Remove known keys to collect extra config
        known_keys = {'app_settings'}
        extra_config = {k: v for k, v in data.items() if k not in known_keys}

        return cls(
            redis=redis,
            tea_credentials=tea_credentials,
            app=AppSettings(**app_data),
            log_settings=LogSettings(**log_data),
            extra_config=extra_config
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields
    )

    @property
    def get_fastapi_cls_attributes(self) -> dict[str, str | bool | None]:
        """
        Gets all `FastAPI` class' attributes defined in `Settings`.
        """
        return {
            "title": self.app.project_name,
            "version": self.app.version,
            "debug": self.app.debug,
            "description": self.app.description,
            "docs_url": self.app.docs_url,
            "openapi_url": self.app.openapi_url,
            "redoc_url": self.app.redoc_url,
            "openapi_prefix": self.app.api_prefix,
            "api_prefix": self.app.openapi_prefix,
        }

@lru_cache()
def get_settings(config_file: str = "config.yaml") -> Settings:
    return Settings.load(config_file)

