from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.main import create_app


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        APP_ENV="test",
        APP_NAME="naver-search-ops-test",
        SECRET_KEY="test-secret-key",
        ADMIN_SESSION_COOKIE="naver_search_admin_test",
        API_SHARED_KEY="test-api-key",
        DATABASE_URL=f"sqlite:///{tmp_path / 'test.db'}",
        TIMEZONE="Asia/Seoul",
        MONTHLY_LIMIT_DEFAULT=2,
    )


@pytest.fixture
def app(settings: Settings):
    application = create_app(settings)
    Base.metadata.create_all(application.state.engine)
    with application.state.session_factory() as session:
        seed_demo_data(session)
    yield application
    Base.metadata.drop_all(application.state.engine)
    application.state.engine.dispose()


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture
def db_session(app) -> Session:
    session = app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_headers(settings: Settings) -> dict[str, str]:
    return {"X-API-Key": settings.api_shared_key}
