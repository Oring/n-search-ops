from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import day_bounds, month_bounds, to_seoul
from app.db.models import Group, Keyword, SearchAttemptLog, Tester


@dataclass
class LogFilters:
    date_from: date | None = None
    date_to: date | None = None
    group_id: str | None = None
    keyword_id: str | None = None
    tester_id: str | None = None


def list_attempt_logs(db: Session, filters: LogFilters) -> list[SearchAttemptLog]:
    statement = select(SearchAttemptLog).order_by(SearchAttemptLog.attempted_at.desc())

    if filters.group_id:
        statement = statement.where(SearchAttemptLog.group_id == filters.group_id)
    if filters.keyword_id:
        statement = statement.where(SearchAttemptLog.keyword_id == filters.keyword_id)
    if filters.tester_id:
        statement = statement.where(SearchAttemptLog.tester_id == filters.tester_id)

    logs = list(db.scalars(statement))
    results: list[SearchAttemptLog] = []
    for log in logs:
        local_date = to_seoul(log.attempted_at).date()
        if filters.date_from and local_date < filters.date_from:
            continue
        if filters.date_to and local_date > filters.date_to:
            continue
        results.append(log)
    return results


def dashboard_payload(db: Session, filters: LogFilters) -> dict[str, object]:
    logs = list_attempt_logs(db, filters)
    total_attempts = len(logs)
    unique_testers = len({log.tester_id for log in logs})

    by_day: dict[date, dict[str, object]] = {}
    day_members: dict[date, set[str]] = defaultdict(set)
    for log in logs:
        local_day = to_seoul(log.attempted_at).date()
        by_day.setdefault(local_day, {"date": local_day, "attempts": 0, "unique_testers": 0})
        by_day[local_day]["attempts"] += 1
        day_members[local_day].add(log.tester_id)
    for key, members in day_members.items():
        by_day[key]["unique_testers"] = len(members)

    by_keyword: dict[str, dict[str, object]] = {}
    keyword_members: dict[str, set[str]] = defaultdict(set)
    for log in logs:
        by_keyword.setdefault(
            log.keyword_snapshot,
            {"keyword": log.keyword_snapshot, "attempts": 0, "unique_testers": 0},
        )
        by_keyword[log.keyword_snapshot]["attempts"] += 1
        keyword_members[log.keyword_snapshot].add(log.tester_id)
    for key, members in keyword_members.items():
        by_keyword[key]["unique_testers"] = len(members)

    by_tester: dict[str, dict[str, object]] = {}
    for log in logs:
        bucket = by_tester.setdefault(
            log.tester_id,
            {
                "member_no": log.member_no_snapshot,
                "name": log.tester_name_snapshot,
                "group_name": log.group_name_snapshot or "-",
                "attempts": 0,
                "last_attempt_at": log.attempted_at,
            },
        )
        bucket["attempts"] += 1
        if log.attempted_at > bucket["last_attempt_at"]:
            bucket["last_attempt_at"] = log.attempted_at

    return {
        "totals": {"attempts": total_attempts, "unique_testers": unique_testers},
        "by_day": sorted(by_day.values(), key=lambda item: item["date"], reverse=True),
        "by_keyword": sorted(by_keyword.values(), key=lambda item: item["attempts"], reverse=True),
        "by_tester": sorted(by_tester.values(), key=lambda item: item["attempts"], reverse=True),
    }


def reference_choices(db: Session) -> dict[str, object]:
    return {
        "groups": list(db.scalars(select(Group).order_by(Group.name))),
        "keywords": list(db.scalars(select(Keyword).order_by(Keyword.phrase))),
        "testers": list(db.scalars(select(Tester).order_by(Tester.name))),
    }
