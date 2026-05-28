from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import AdminLoginRequired
from app.admin.routes import accounts, assignments, auth, dashboard, groups, keywords, logs, testers
from app.api.dependencies import ApiAuthError
from app.api.routes import app_api, health
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.time import to_seoul
from app.db.session import create_engine_and_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    app_settings = settings or get_settings()
    engine, session_factory = create_engine_and_session_factory(app_settings)

    app = FastAPI(title=app_settings.app_name)
    app.state.settings = app_settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    base_dir = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=str(base_dir / "templates"))
    templates.env.filters["seoul_datetime"] = lambda value: to_seoul(value).strftime("%Y-%m-%d %H:%M:%S")
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")
    app.add_middleware(
        SessionMiddleware,
        secret_key=app_settings.secret_key,
        session_cookie=app_settings.admin_session_cookie,
        max_age=app_settings.session_max_age_seconds,
        same_site="lax",
        https_only=app_settings.app_env == "production",
    )

    @app.exception_handler(ApiAuthError)
    async def handle_api_auth_error(_: Request, exc: ApiAuthError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"ok": False})

    @app.exception_handler(AdminLoginRequired)
    async def handle_admin_login_required(_: Request, __: AdminLoginRequired) -> RedirectResponse:
        return RedirectResponse("/admin/login", status_code=303)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse("/admin", status_code=303)

    app.include_router(health.router)
    app.include_router(app_api.router, prefix="/api/v1")
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(testers.router)
    app.include_router(groups.router)
    app.include_router(keywords.router)
    app.include_router(assignments.router)
    app.include_router(accounts.router)
    app.include_router(logs.router)
    return app


app = create_app()
