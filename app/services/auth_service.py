from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, validate_password, verify_password
from app.core.time import utc_now
from app.db.models import AdminAccount


def authenticate_admin(db: Session, username: str, password: str) -> AdminAccount | None:
    admin = db.scalar(select(AdminAccount).where(AdminAccount.username == username))
    if admin is None or not admin.is_active:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    admin.last_login_at = utc_now()
    db.commit()
    db.refresh(admin)
    return admin


def create_admin_account(db: Session, *, username: str, password: str) -> AdminAccount:
    existing = db.scalar(select(AdminAccount).where(AdminAccount.username == username))
    if existing is not None:
        raise ValueError("이미 사용 중인 관리자 아이디입니다.")

    admin = AdminAccount(username=username.strip(), password_hash=hash_password(password), is_active=True)
    db.add(admin)
    db.flush()
    return admin


def change_password(db: Session, admin: AdminAccount, password: str) -> AdminAccount:
    validate_password(password)
    admin.password_hash = hash_password(password)
    admin.updated_at = utc_now()
    db.flush()
    return admin
