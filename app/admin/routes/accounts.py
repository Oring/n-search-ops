from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.db.models import AdminAccount
from app.services.admin_service import add_flash, build_context, create_admin_audit_log
from app.services.auth_service import create_admin_account

router = APIRouter(prefix="/admin/accounts", tags=["admin-accounts"])


@router.get("")
def accounts_page(request: Request, db: Session = Depends(get_db_session)):
    current_admin = require_admin(request, db)
    accounts = list(db.scalars(select(AdminAccount).order_by(AdminAccount.username)))
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/accounts.html",
        build_context(request, title="관리자 계정", current_admin=current_admin, accounts=accounts),
    )


@router.post("")
def save_account(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    try:
        account = create_admin_account(db, username=username, password=password)
    except ValueError as exc:
        add_flash(request, "error", str(exc))
        return RedirectResponse("/admin/accounts", status_code=303)

    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="admin_created",
        entity_type="admin_account",
        entity_id=account.id,
        detail={"username": account.username},
    )
    db.commit()
    add_flash(request, "success", "관리자 계정이 생성되었습니다.")
    return RedirectResponse("/admin/accounts", status_code=303)


@router.post("/{account_id}/toggle")
def toggle_account(account_id: str, request: Request, db: Session = Depends(get_db_session)):
    current_admin = require_admin(request, db)
    account = db.get(AdminAccount, account_id)
    if account is None:
        add_flash(request, "error", "관리자 계정을 찾을 수 없습니다.")
        return RedirectResponse("/admin/accounts", status_code=303)
    if account.id == current_admin.id:
        add_flash(request, "error", "본인 계정은 비활성화할 수 없습니다.")
        return RedirectResponse("/admin/accounts", status_code=303)

    account.is_active = not account.is_active
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="admin_toggled",
        entity_type="admin_account",
        entity_id=account.id,
        detail={"is_active": account.is_active},
    )
    db.commit()
    add_flash(request, "success", "관리자 계정 상태가 변경되었습니다.")
    return RedirectResponse("/admin/accounts", status_code=303)
