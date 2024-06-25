from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    RANDOM_TAPS_COUNT: list[int] = [10, 50]
    SLEEP_BETWEEN_TAP: list[int] = [10, 25]

    USE_RANDOM_USERAGENT: bool = False

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()
