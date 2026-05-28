from sqlalchemy import select

from app.db.models import AdminAuditLog, Tester as TesterModel
from tests.helpers import login_as_admin


def test_dashboard_logs_and_csv_export(client, api_headers, db_session):
    first = client.get("/api/v1/search-target", params={"member_no": "1001"}, headers=api_headers).json()
    second = client.get("/api/v1/search-target", params={"member_no": "1002"}, headers=api_headers).json()

    client.post(
        "/api/v1/search-attempts",
        json={"member_no": "1001", "keyword_id": first["keyword_id"]},
        headers=api_headers,
    )
    client.post(
        "/api/v1/search-attempts",
        json={"member_no": "1002", "keyword_id": second["keyword_id"]},
        headers=api_headers,
    )

    login_as_admin(client)
    dashboard = client.get("/admin")
    assert dashboard.status_code == 200
    assert "원시 시도 수" in dashboard.text
    assert "고유 참여자 수" in dashboard.text

    tester = db_session.scalar(select(TesterModel).where(TesterModel.member_no == "1001"))
    logs_page = client.get("/admin/logs", params={"tester_id": tester.id})
    assert logs_page.status_code == 200
    assert "상세 로그" in logs_page.text

    csv_response = client.get("/admin/logs/csv", params={"tester_id": tester.id})
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]
    assert "회원번호,이름,그룹,키워드" in csv_response.text
    assert "1001" in csv_response.text
    assert "1002" not in csv_response.text

    audit = db_session.scalar(
        select(AdminAuditLog).where(AdminAuditLog.event_type == "csv_exported").order_by(AdminAuditLog.occurred_at.desc())
    )
    assert audit is not None
