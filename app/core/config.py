from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://") and "+psycopg" not in database_url.split("://", 1)[0]:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="naver-search-ops", alias="APP_NAME")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    admin_session_cookie: str = Field(
        default="naver_search_admin",
        alias="ADMIN_SESSION_COOKIE",
    )
    api_shared_key: str = Field(default="change-me", alias="API_SHARED_KEY")
    database_url: str = Field(default="sqlite:///./local.db", alias="DATABASE_URL")
    timezone: str = Field(default="Asia/Seoul", alias="TIMEZONE")
    monthly_limit_default: int = Field(default=2, alias="MONTHLY_LIMIT_DEFAULT")
    session_max_age_seconds: int = Field(default=60 * 60 * 12, alias="SESSION_MAX_AGE_SECONDS")

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"

    @property
    def normalized_database_url(self) -> str:
        return normalize_database_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
