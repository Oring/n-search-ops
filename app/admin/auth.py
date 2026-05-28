from __future__ import annotations

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.models import AdminAccount


class AdminLoginRequired(Exception):
    pass


def get_current_admin(request: Request, db: Session) -> AdminAccount | None:
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return None

    admin = db.get(AdminAccount, admin_id)
    if admin is None or not admin.is_active:
        request.session.pop("admin_id", None)
        return None
    return admin


def require_admin(request: Request, db: Session) -> AdminAccount:
    admin = get_current_admin(request, db)
    if admin is None:
        raise AdminLoginRequired()
    return admin


def login_admin_session(request: Request, admin: AdminAccount) -> None:
    request.session["admin_id"] = admin.id


def logout_admin_session(request: Request) -> None:
    request.session.pop("admin_id", None)
