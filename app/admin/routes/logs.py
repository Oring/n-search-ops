from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.services.admin_service import build_context, create_admin_audit_log
from app.services.csv_service import render_attempt_logs_csv
from app.services.stats_service import LogFilters, list_attempt_logs, reference_choices

router = APIRouter(prefix="/admin/logs", tags=["admin-logs"])


def _filters_from_request(
    date_from: str | None,
    date_to: str | None,
    group_id: str | None,
    keyword_id: str | None,
    tester_id: str | None,
) -> LogFilters:
    return LogFilters(
        date_from=date.fromisoformat(date_from) if date_from else None,
        date_to=date.fromisoformat(date_to) if date_to else None,
        group_id=group_id or None,
        keyword_id=keyword_id or None,
        tester_id=tester_id or None,
    )


@router.get("")
def logs_page(
    request: Request,
    date_from: str | None = None,
    date_to: str | None = None,
    group_id: str | None = None,
    keyword_id: str | None = None,
    tester_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    filters = _filters_from_request(date_from, date_to, group_id, keyword_id, tester_id)
    logs = list_attempt_logs(db, filters)
    choices = reference_choices(db)
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/logs.html",
        build_context(
            request,
            title="상세 로그",
            current_admin=current_admin,
            filters=filters,
            logs=logs,
            **choices,
        ),
    )


@router.get("/csv")
def export_logs_csv(
    request: Request,
    date_from: str | None = None,
    date_to: str | None = None,
    group_id: str | None = None,
    keyword_id: str | None = None,
    tester_id: str | None = None,
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    filters = _filters_from_request(date_from, date_to, group_id, keyword_id, tester_id)
    logs = list_attempt_logs(db, filters)
    csv_body = render_attempt_logs_csv(logs)
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="csv_exported",
        entity_type="search_attempt_logs",
        detail={
            "count": len(logs),
            "date_from": date_from,
            "date_to": date_to,
            "group_id": group_id,
            "keyword_id": keyword_id,
            "tester_id": tester_id,
        },
    )
    db.commit()
    return Response(
        content=csv_body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=search-attempt-logs.csv"},
    )
