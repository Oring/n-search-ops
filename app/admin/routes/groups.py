from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.db.models import Group
from app.services.admin_service import add_flash, build_context, create_admin_audit_log

router = APIRouter(prefix="/admin/groups", tags=["admin-groups"])


@router.get("")
def groups_page(request: Request, edit: str | None = None, db: Session = Depends(get_db_session)):
    current_admin = require_admin(request, db)
    groups = list(db.scalars(select(Group).order_by(Group.name)))
    editing = db.get(Group, edit) if edit else None
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/groups.html",
        build_context(request, title="그룹 관리", current_admin=current_admin, groups=groups, editing=editing),
    )


@router.post("")
def save_group(
    request: Request,
    group_id: str | None = Form(None),
    name: str = Form(...),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    existing = db.scalar(select(Group).where(Group.name == name.strip()))
    group = db.get(Group, group_id) if group_id else None
    if existing is not None and group is None:
        add_flash(request, "error", "이미 존재하는 그룹명입니다.")
        return RedirectResponse("/admin/groups", status_code=303)

    if group is None:
        group = Group(name=name.strip(), is_active=True)
        db.add(group)

    group.name = name.strip()
    group.is_active = is_active == "on"
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="group_saved",
        entity_type="group",
        entity_id=group.id,
        detail={"name": group.name},
    )
    db.commit()
    add_flash(request, "success", "그룹이 저장되었습니다.")
    return RedirectResponse("/admin/groups", status_code=303)
