from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.core.time import normalize_week_start, week_start_for
from app.db.models import AppSetting, Group, GroupWeekKeywordAssignment, Keyword
from app.services.admin_service import (
    add_flash,
    build_context,
    create_admin_audit_log,
    get_setting_int,
    set_setting_int,
)
from app.services.assignment_service import replace_group_week_assignments

router = APIRouter(prefix="/admin/assignments", tags=["admin-assignments"])


@router.get("")
def assignments_page(
    request: Request,
    week_start: str | None = None,
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    selected_week = normalize_week_start(
        date.fromisoformat(week_start) if week_start else week_start_for()
    )
    groups = list(db.scalars(select(Group).order_by(Group.name)))
    keywords = list(db.scalars(select(Keyword).where(Keyword.is_active.is_(True)).order_by(Keyword.phrase)))
    assignments = list(
        db.scalars(
            select(GroupWeekKeywordAssignment)
            .options(
                joinedload(GroupWeekKeywordAssignment.group),
                joinedload(GroupWeekKeywordAssignment.keyword),
            )
            .where(GroupWeekKeywordAssignment.week_start == selected_week)
            .order_by(GroupWeekKeywordAssignment.group_id)
        )
    )
    monthly_limit = get_setting_int(db, "monthly_limit", request.app.state.settings.monthly_limit_default)
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/assignments.html",
        build_context(
            request,
            title="주차별 할당",
            current_admin=current_admin,
            groups=groups,
            keywords=keywords,
            assignments=assignments,
            selected_week=selected_week,
            monthly_limit=monthly_limit,
        ),
    )


@router.post("")
def save_assignments(
    request: Request,
    group_id: str = Form(...),
    week_start: str = Form(...),
    keyword_ids: list[str] = Form([]),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    normalized = normalize_week_start(date.fromisoformat(week_start))
    replace_group_week_assignments(
        db,
        group_id=group_id,
        week_start=normalized,
        keyword_ids=keyword_ids,
        admin_id=current_admin.id,
    )
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="assignment_saved",
        entity_type="group_week_keyword_assignment",
        entity_id=group_id,
        detail={"week_start": normalized.isoformat(), "keyword_ids": keyword_ids},
    )
    db.commit()
    add_flash(request, "success", "주차별 키워드 할당이 저장되었습니다.")
    return RedirectResponse(f"/admin/assignments?week_start={normalized.isoformat()}", status_code=303)


@router.post("/settings")
def save_monthly_limit(
    request: Request,
    monthly_limit: int = Form(...),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    if monthly_limit < 1:
        add_flash(request, "error", "월간 제한은 1 이상이어야 합니다.")
        return RedirectResponse("/admin/assignments", status_code=303)

    setting = set_setting_int(db, "monthly_limit", monthly_limit, current_admin)
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="monthly_limit_changed",
        entity_type="app_setting",
        entity_id=setting.key,
        detail={"value": monthly_limit},
    )
    db.commit()
    add_flash(request, "success", "월간 제한이 저장되었습니다.")
    return RedirectResponse("/admin/assignments", status_code=303)
