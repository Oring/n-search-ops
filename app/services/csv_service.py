from __future__ import annotations

import csv
from io import StringIO

from app.core.time import to_seoul
from app.db.models import SearchAttemptLog


def render_attempt_logs_csv(logs: list[SearchAttemptLog]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["시각", "회원번호", "이름", "그룹", "키워드"])

    for log in logs:
        writer.writerow(
            [
                to_seoul(log.attempted_at).strftime("%Y-%m-%d %H:%M:%S"),
                log.member_no_snapshot,
                log.tester_name_snapshot,
                log.group_name_snapshot or "",
                log.keyword_snapshot,
            ]
        )

    return buffer.getvalue()
