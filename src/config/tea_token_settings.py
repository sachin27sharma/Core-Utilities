from pydantic_settings import BaseSettings, SettingsConfigDict


class TeaTokenSettings(BaseSettings):
    # Username for TEA token authentication (can be set via TEA_TOKEN_USERNAME in .env)
    username: str = ""
    # Password for TEA token authentication (can be set via TEA_TOKEN_PASSWORD in .env)
    password: str = ""

    model_config = SettingsConfigDict(
        env_prefix="TEA_TOKEN_"
    )

