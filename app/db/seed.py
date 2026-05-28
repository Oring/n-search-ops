from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.time import utc_now, week_start_for
from app.db.models import AdminAccount, AppSetting, Group, GroupWeekKeywordAssignment, Keyword, Tester


def seed_demo_data(session: Session) -> None:
    if session.scalar(select(AdminAccount).limit(1)) is None:
        admin = AdminAccount(
            username="admin",
            password_hash=hash_password("admin1234"),
            is_active=True,
        )
        session.add(admin)
        session.flush()
    else:
        admin = session.scalars(select(AdminAccount)).first()

    if session.get(AppSetting, "monthly_limit") is None:
        session.add(
            AppSetting(
                key="monthly_limit",
                value="2",
                updated_at=utc_now(),
                updated_by_admin_id=admin.id if admin else None,
            )
        )

    if session.scalar(select(Group).limit(1)) is None:
        group_a = Group(name="A", is_active=True)
        group_b = Group(name="B", is_active=True)
        session.add_all([group_a, group_b])
        session.flush()
    else:
        groups = session.scalars(select(Group).order_by(Group.name)).all()
        group_a = groups[0]
        group_b = groups[-1]

    if session.scalar(select(Keyword).limit(1)) is None:
        keyword_one = Keyword(phrase="본스탬프 후기", is_active=True)
        keyword_two = Keyword(phrase="본스탬프 리뷰", is_active=True)
        session.add_all([keyword_one, keyword_two])
        session.flush()
    else:
        keywords = session.scalars(select(Keyword).order_by(Keyword.phrase)).all()
        keyword_one = keywords[0]
        keyword_two = keywords[-1]

    if session.scalar(select(Tester).limit(1)) is None:
        session.add_all(
            [
                Tester(member_no="1001", name="홍길동", group_id=group_a.id, is_active=True),
                Tester(member_no="1002", name="김민수", group_id=group_b.id, is_active=True),
            ]
        )

    current_week = week_start_for(date.today())
    existing = session.scalar(
        select(GroupWeekKeywordAssignment).where(
            GroupWeekKeywordAssignment.group_id == group_a.id,
            GroupWeekKeywordAssignment.week_start == current_week,
        )
    )
    if existing is None:
        session.add_all(
            [
                GroupWeekKeywordAssignment(
                    group_id=group_a.id,
                    week_start=current_week,
                    keyword_id=keyword_one.id,
                    created_at=utc_now(),
                    created_by_admin_id=admin.id if admin else None,
                ),
                GroupWeekKeywordAssignment(
                    group_id=group_b.id,
                    week_start=current_week,
                    keyword_id=keyword_two.id,
                    created_at=utc_now(),
                    created_by_admin_id=admin.id if admin else None,
                ),
            ]
        )

    session.commit()
