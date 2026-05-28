from datetime import timedelta

from sqlalchemy import select

from app.core.time import month_bounds
from app.db.models import AppSetting, Keyword, SearchAttemptLog, Tester as TesterModel, WarningLog


def test_second_lookup_after_successful_record_returns_false(client, api_headers):
    target = client.get("/api/v1/search-target", params={"member_no": "1001"}, headers=api_headers).json()
    assert target["ok"] is True

    attempt = client.post(
        "/api/v1/search-attempts",
        json={"member_no": "1001", "keyword_id": target["keyword_id"]},
        headers=api_headers,
    ).json()
    assert attempt == {"ok": True}

    second_lookup = client.get("/api/v1/search-target", params={"member_no": "1001"}, headers=api_headers)
    assert second_lookup.status_code == 200
    assert second_lookup.json() == {"ok": False, "keyword": None, "keyword_id": None}


def test_monthly_limit_blocks_lookup(client, api_headers, db_session):
    tester = db_session.scalar(select(TesterModel).where(TesterModel.member_no == "1002"))
    keyword = db_session.scalar(select(Keyword).limit(1))
    db_session.get(AppSetting, "monthly_limit").value = "1"
    monthly_start = month_bounds().start_utc + timedelta(days=1)
    db_session.add(
        SearchAttemptLog(
            tester_id=tester.id,
            group_id=tester.group_id,
            keyword_id=keyword.id,
            attempted_at=monthly_start,
            member_no_snapshot=tester.member_no,
            tester_name_snapshot=tester.name,
            group_name_snapshot=tester.group.name if tester.group else None,
            keyword_snapshot="기존 키워드",
            source="app",
        )
    )
    db_session.commit()

    response = client.get("/api/v1/search-target", params={"member_no": "1002"}, headers=api_headers)
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_invalid_keyword_attempt_creates_warning_log(client, api_headers, db_session):
    response = client.post(
        "/api/v1/search-attempts",
        json={"member_no": "1001", "keyword_id": "00000000-0000-0000-0000-000000000000"},
        headers=api_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"ok": False}

    warning = db_session.scalar(
        select(WarningLog).where(WarningLog.event_type == "invalid_keyword").order_by(WarningLog.occurred_at.desc())
    )
    assert warning is not None
    assert warning.member_no == "1001"
