from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.db.models import AdminAccount, AdminAuditLog, AppSetting, WarningLog


def create_warning_log(
    db: Session,
    *,
    event_type: str,
    member_no: str | None = None,
    request_path: str | None = None,
    detail: dict[str, Any] | None = None,
    commit: bool = False,
) -> None:
    db.add(
        WarningLog(
            event_type=event_type,
            member_no=member_no,
            request_path=request_path,
            detail_json=detail or {},
            occurred_at=utc_now(),
        )
    )
    if commit:
        db.commit()


def create_admin_audit_log(
    db: Session,
    *,
    admin: AdminAccount | None,
    event_type: str,
    entity_type: str,
    entity_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            admin_id=admin.id if admin else None,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            detail_json=detail or {},
            occurred_at=utc_now(),
        )
    )


def ensure_setting(db: Session, key: str, value: str, admin: AdminAccount | None = None) -> AppSetting:
    setting = db.get(AppSetting, key)
    if setting is None:
        setting = AppSetting(
            key=key,
            value=value,
            updated_at=utc_now(),
            updated_by_admin_id=admin.id if admin else None,
        )
        db.add(setting)
    return setting


def get_setting_int(db: Session, key: str, default: int) -> int:
    setting = db.get(AppSetting, key)
    if setting is None:
        return default
    try:
        return int(setting.value)
    except ValueError:
        return default


def set_setting_int(db: Session, key: str, value: int, admin: AdminAccount | None = None) -> AppSetting:
    setting = ensure_setting(db, key, str(value), admin)
    setting.value = str(value)
    setting.updated_at = utc_now()
    setting.updated_by_admin_id = admin.id if admin else None
    return setting


def add_flash(request: Any, kind: str, message: str) -> None:
    request.session["flash"] = {"kind": kind, "message": message}


def pop_flash(request: Any) -> dict[str, str] | None:
    return request.session.pop("flash", None)


def build_context(request: Any, *, title: str, current_admin: AdminAccount | None, **extra: Any) -> dict[str, Any]:
    context = {
        "request": request,
        "title": title,
        "current_admin": current_admin,
        "flash": pop_flash(request),
    }
    context.update(extra)
    return context
