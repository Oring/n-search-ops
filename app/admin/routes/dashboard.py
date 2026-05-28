from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.services.admin_service import build_context
from app.services.stats_service import LogFilters, dashboard_payload

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])


@router.get("")
def dashboard(
    request: Request,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    end = date.fromisoformat(date_to) if date_to else date.today()
    start = date.fromisoformat(date_from) if date_from else end - timedelta(days=29)
    filters = LogFilters(date_from=start, date_to=end)
    payload = dashboard_payload(db, filters)
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        build_context(
            request,
            title="대시보드",
            current_admin=current_admin,
            filters=filters,
            stats=payload,
        ),
    )
