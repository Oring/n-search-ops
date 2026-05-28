from app.core.config import Settings, normalize_database_url


def test_normalize_database_url_for_postgres_driver() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@example.com:5432/dbname")
        == "postgresql+psycopg://user:pass@example.com:5432/dbname"
    )
    assert (
        normalize_database_url("postgres://user:pass@example.com:5432/dbname")
        == "postgresql+psycopg://user:pass@example.com:5432/dbname"
    )
    assert (
        normalize_database_url("postgresql+psycopg://user:pass@example.com:5432/dbname")
        == "postgresql+psycopg://user:pass@example.com:5432/dbname"
    )


def test_settings_exposes_normalized_database_url() -> None:
    settings = Settings(
        APP_ENV="test",
        SECRET_KEY="secret",
        API_SHARED_KEY="api",
        DATABASE_URL="postgresql://user:pass@example.com:5432/dbname",
    )

    assert settings.normalized_database_url == "postgresql+psycopg://user:pass@example.com:5432/dbname"
