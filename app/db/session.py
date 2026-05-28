from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def create_engine_and_session_factory(settings: Settings) -> tuple[Engine, sessionmaker[Session]]:
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return engine, session_factory
