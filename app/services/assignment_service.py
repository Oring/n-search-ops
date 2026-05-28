from __future__ import annotations

import random
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.time import normalize_week_start, utc_now, week_start_for
from app.db.models import GroupWeekKeywordAssignment, Keyword, Tester


def replace_group_week_assignments(
    db: Session,
    *,
    group_id: str,
    week_start: date,
    keyword_ids: list[str],
    admin_id: str | None,
) -> None:
    normalized = normalize_week_start(week_start)
    db.execute(
        delete(GroupWeekKeywordAssignment).where(
            GroupWeekKeywordAssignment.group_id == group_id,
            GroupWeekKeywordAssignment.week_start == normalized,
        )
    )

    for keyword_id in keyword_ids:
        db.add(
            GroupWeekKeywordAssignment(
                group_id=group_id,
                week_start=normalized,
                keyword_id=keyword_id,
                created_at=utc_now(),
                created_by_admin_id=admin_id,
            )
        )


def get_active_keyword_choices_for_tester(db: Session, tester: Tester) -> list[Keyword]:
    if tester.group_id is None:
        return []

    current_week = week_start_for()
    statement = (
        select(Keyword)
        .join(GroupWeekKeywordAssignment, GroupWeekKeywordAssignment.keyword_id == Keyword.id)
        .where(
            GroupWeekKeywordAssignment.group_id == tester.group_id,
            GroupWeekKeywordAssignment.week_start == current_week,
            Keyword.is_active.is_(True),
        )
        .order_by(Keyword.phrase)
    )
    return list(db.scalars(statement))


def choose_keyword_for_tester(db: Session, tester: Tester) -> Keyword | None:
    choices = get_active_keyword_choices_for_tester(db, tester)
    if not choices:
        return None
    return random.choice(choices)
