from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()
