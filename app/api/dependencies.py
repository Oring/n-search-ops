from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.services.admin_service import create_warning_log


class ApiAuthError(Exception):
    def __init__(self, status_code: int = 401) -> None:
        self.status_code = status_code


def get_db_session(request: Request) -> Generator[Session, None, None]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def authorize_api_key(request: Request, db: Session, member_no: str | None = None) -> None:
    provided = request.headers.get("X-API-Key")
    expected = request.app.state.settings.api_shared_key
    if provided == expected:
        return

    create_warning_log(
        db,
        event_type="invalid_api_key",
        member_no=member_no,
        request_path=request.url.path,
        detail={},
        commit=True,
    )
    raise ApiAuthError(status_code=401)
