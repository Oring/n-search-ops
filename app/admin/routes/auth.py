from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.admin.auth import get_current_admin, login_admin_session, logout_admin_session, require_admin
from app.api.dependencies import get_db_session
from app.services.admin_service import add_flash, build_context, create_admin_audit_log
from app.services.auth_service import authenticate_admin, change_password

router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db_session)):
    current_admin = get_current_admin(request, db)
    if current_admin is not None:
        return RedirectResponse("/admin", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/login.html",
        build_context(request, title="관리자 로그인", current_admin=None),
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    admin = authenticate_admin(db, username, password)
    if admin is None:
        add_flash(request, "error", "로그인에 실패했습니다.")
        return RedirectResponse("/admin/login", status_code=303)

    login_admin_session(request, admin)
    add_flash(request, "success", "로그인되었습니다.")
    return RedirectResponse("/admin", status_code=303)


@router.post("/logout")
def logout(request: Request):
    logout_admin_session(request)
    add_flash(request, "success", "로그아웃되었습니다.")
    return RedirectResponse("/admin/login", status_code=303)


@router.post("/password")
def update_password(
    request: Request,
    new_password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    admin = require_admin(request, db)
    try:
        change_password(db, admin, new_password)
    except ValueError as exc:
        add_flash(request, "error", str(exc))
        return RedirectResponse("/admin/accounts", status_code=303)

    create_admin_audit_log(
        db,
        admin=admin,
        event_type="password_changed",
        entity_type="admin_account",
        entity_id=admin.id,
        detail={},
    )
    db.commit()
    add_flash(request, "success", "비밀번호가 변경되었습니다.")
    return RedirectResponse("/admin/accounts", status_code=303)
