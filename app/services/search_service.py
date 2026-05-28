from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.time import day_bounds, month_bounds, utc_now
from app.db.models import Group, Keyword, SearchAttemptLog, Tester
from app.services.admin_service import create_warning_log, get_setting_int
from app.services.assignment_service import choose_keyword_for_tester, get_active_keyword_choices_for_tester


@dataclass
class SearchTargetResult:
    ok: bool
    keyword: str | None = None
    keyword_id: str | None = None


def _load_tester(db: Session, member_no: str) -> Tester | None:
    return db.scalar(select(Tester).where(Tester.member_no == member_no))


def _count_attempts_between(db: Session, tester_id: str, start_utc, end_utc) -> int:
    return (
        db.scalar(
            select(func.count(SearchAttemptLog.id)).where(
                SearchAttemptLog.tester_id == tester_id,
                SearchAttemptLog.attempted_at >= start_utc,
                SearchAttemptLog.attempted_at < end_utc,
            )
        )
        or 0
    )


def get_search_target(db: Session, settings: Settings, member_no: str, request_path: str) -> SearchTargetResult:
    tester = _load_tester(db, member_no)
    if tester is None:
        create_warning_log(
            db,
            event_type="unregistered_member",
            member_no=member_no,
            request_path=request_path,
            detail={},
            commit=True,
        )
        return SearchTargetResult(ok=False)

    if not tester.is_active:
        create_warning_log(
            db,
            event_type="inactive_tester",
            member_no=member_no,
            request_path=request_path,
            detail={"tester_id": tester.id},
            commit=True,
        )
        return SearchTargetResult(ok=False)

    if tester.group is None or not tester.group.is_active:
        return SearchTargetResult(ok=False)

    daily = day_bounds()
    if _count_attempts_between(db, tester.id, daily.start_utc, daily.end_utc) > 0:
        return SearchTargetResult(ok=False)

    monthly_limit = get_setting_int(db, "monthly_limit", settings.monthly_limit_default)
    monthly = month_bounds()
    if _count_attempts_between(db, tester.id, monthly.start_utc, monthly.end_utc) >= monthly_limit:
        return SearchTargetResult(ok=False)

    keyword = choose_keyword_for_tester(db, tester)
    if keyword is None:
        return SearchTargetResult(ok=False)

    return SearchTargetResult(ok=True, keyword=keyword.phrase, keyword_id=keyword.id)


def record_search_attempt(
    db: Session,
    settings: Settings,
    *,
    member_no: str,
    keyword_id: str,
    request_path: str,
) -> bool:
    del settings
    tester = _load_tester(db, member_no)
    if tester is None:
        create_warning_log(
            db,
            event_type="unregistered_member",
            member_no=member_no,
            request_path=request_path,
            detail={"keyword_id": keyword_id},
            commit=True,
        )
        return False

    if not tester.is_active:
        create_warning_log(
            db,
            event_type="inactive_tester",
            member_no=member_no,
            request_path=request_path,
            detail={"keyword_id": keyword_id, "tester_id": tester.id},
            commit=True,
        )
        return False

    if tester.group is None or not tester.group.is_active:
        return False

    valid_keywords = {item.id: item for item in get_active_keyword_choices_for_tester(db, tester)}
    keyword = valid_keywords.get(keyword_id)
    if keyword is None:
        create_warning_log(
            db,
            event_type="invalid_keyword",
            member_no=member_no,
            request_path=request_path,
            detail={"keyword_id": keyword_id, "tester_id": tester.id},
            commit=True,
        )
        return False

    group: Group | None = tester.group
    db.add(
        SearchAttemptLog(
            tester_id=tester.id,
            group_id=group.id if group else None,
            keyword_id=keyword.id,
            attempted_at=utc_now(),
            member_no_snapshot=tester.member_no,
            tester_name_snapshot=tester.name,
            group_name_snapshot=group.name if group else None,
            keyword_snapshot=keyword.phrase,
            source="app",
        )
    )
    db.commit()
    return True
