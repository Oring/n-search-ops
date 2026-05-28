from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.db.models import Group, Tester
from app.services.admin_service import add_flash, build_context, create_admin_audit_log

router = APIRouter(prefix="/admin/testers", tags=["admin-testers"])


@router.get("")
def testers_page(request: Request, edit: str | None = None, db: Session = Depends(get_db_session)):
    current_admin = require_admin(request, db)
    testers = list(db.scalars(select(Tester).options(selectinload(Tester.group)).order_by(Tester.member_no)))
    groups = list(db.scalars(select(Group).order_by(Group.name)))
    editing = db.get(Tester, edit) if edit else None
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/testers.html",
        build_context(
            request,
            title="테스터 관리",
            current_admin=current_admin,
            testers=testers,
            groups=groups,
            editing=editing,
        ),
    )


@router.post("")
def save_tester(
    request: Request,
    tester_id: str | None = Form(None),
    member_no: str = Form(...),
    name: str = Form(...),
    phone_last4: str | None = Form(None),
    group_id: str | None = Form(None),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    existing = db.scalar(select(Tester).where(Tester.member_no == member_no.strip()))
    tester = db.get(Tester, tester_id) if tester_id else None

    if tester is None and existing is not None and existing.is_active:
        add_flash(request, "error", "이미 등록된 회원번호입니다.")
        return RedirectResponse("/admin/testers", status_code=303)

    if tester is None and existing is not None and not existing.is_active:
        tester = existing
    elif tester is None:
        tester = Tester(member_no=member_no.strip(), name=name.strip())
        db.add(tester)

    tester.member_no = member_no.strip()
    tester.name = name.strip()
    tester.phone_last4 = (phone_last4 or "").strip() or None
    tester.group_id = group_id or None
    tester.is_active = is_active == "on"

    event_type = "tester_created" if tester_id is None and existing is None else "tester_updated"
    if existing is not None and not existing.is_active:
        event_type = "tester_reactivated"

    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type=event_type,
        entity_type="tester",
        entity_id=tester.id,
        detail={"member_no": tester.member_no},
    )
    db.commit()
    add_flash(request, "success", "테스터가 저장되었습니다.")
    return RedirectResponse("/admin/testers", status_code=303)
