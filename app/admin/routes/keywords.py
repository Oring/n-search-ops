from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.auth import require_admin
from app.api.dependencies import get_db_session
from app.db.models import Keyword
from app.services.admin_service import add_flash, build_context, create_admin_audit_log

router = APIRouter(prefix="/admin/keywords", tags=["admin-keywords"])


@router.get("")
def keywords_page(request: Request, edit: str | None = None, db: Session = Depends(get_db_session)):
    current_admin = require_admin(request, db)
    keywords = list(db.scalars(select(Keyword).order_by(Keyword.phrase)))
    editing = db.get(Keyword, edit) if edit else None
    return request.app.state.templates.TemplateResponse(
        request,
        "admin/keywords.html",
        build_context(
            request,
            title="키워드 관리",
            current_admin=current_admin,
            keywords=keywords,
            editing=editing,
        ),
    )


@router.post("")
def save_keyword(
    request: Request,
    keyword_id: str | None = Form(None),
    phrase: str = Form(...),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db_session),
):
    current_admin = require_admin(request, db)
    existing = db.scalar(select(Keyword).where(Keyword.phrase == phrase.strip()))
    keyword = db.get(Keyword, keyword_id) if keyword_id else None
    if existing is not None and keyword is None:
        add_flash(request, "error", "이미 존재하는 키워드입니다.")
        return RedirectResponse("/admin/keywords", status_code=303)

    if keyword is None:
        keyword = Keyword(phrase=phrase.strip(), is_active=True)
        db.add(keyword)

    keyword.phrase = phrase.strip()
    keyword.is_active = is_active == "on"
    create_admin_audit_log(
        db,
        admin=current_admin,
        event_type="keyword_saved",
        entity_type="keyword",
        entity_id=keyword.id,
        detail={"phrase": keyword.phrase},
    )
    db.commit()
    add_flash(request, "success", "키워드가 저장되었습니다.")
    return RedirectResponse("/admin/keywords", status_code=303)
