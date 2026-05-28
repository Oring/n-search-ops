from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo


SEOUL = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class TimeBounds:
    start_utc: datetime
    end_utc: datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def seoul_now() -> datetime:
    return utc_now().astimezone(SEOUL)


def to_seoul(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(SEOUL)


def week_start_for(value: date | None = None) -> date:
    current = value or seoul_now().date()
    return current - timedelta(days=current.weekday())


def normalize_week_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def day_bounds(reference: datetime | None = None) -> TimeBounds:
    local = to_seoul(reference or utc_now())
    start_local = datetime.combine(local.date(), time.min, tzinfo=SEOUL)
    end_local = start_local + timedelta(days=1)
    return TimeBounds(start_utc=start_local.astimezone(UTC), end_utc=end_local.astimezone(UTC))


def month_bounds(reference: datetime | None = None) -> TimeBounds:
    local = to_seoul(reference or utc_now())
    start_local = datetime(local.year, local.month, 1, tzinfo=SEOUL)
    if local.month == 12:
        end_local = datetime(local.year + 1, 1, 1, tzinfo=SEOUL)
    else:
        end_local = datetime(local.year, local.month + 1, 1, tzinfo=SEOUL)
    return TimeBounds(start_utc=start_local.astimezone(UTC), end_utc=end_local.astimezone(UTC))
