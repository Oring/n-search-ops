from sqlalchemy import select

from app.core.time import week_start_for
from app.db.models import Group, GroupWeekKeywordAssignment, Keyword, Tester as TesterModel
from tests.helpers import login_as_admin


def test_admin_login_reactivate_tester_and_overwrite_assignment(client, db_session):
    login_as_admin(client)

    tester = db_session.scalar(select(TesterModel).where(TesterModel.member_no == "1001"))
    tester.is_active = False
    db_session.commit()

    response = client.post(
        "/admin/testers",
        data={
            "member_no": "1001",
            "name": "홍길동 재활성",
            "group_id": tester.group_id,
            "phone_last4": "1234",
            "is_active": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    db_session.expire_all()
    refreshed = db_session.scalar(select(TesterModel).where(TesterModel.member_no == "1001"))
    assert refreshed.is_active is True
    assert refreshed.name == "홍길동 재활성"

    group = db_session.scalar(select(Group).where(Group.name == "A"))
    keyword = Keyword(phrase="본스탬프 이벤트", is_active=True)
    keyword_2 = Keyword(phrase="본스탬프 체험단", is_active=True)
    db_session.add_all([keyword, keyword_2])
    db_session.commit()

    response = client.post(
        "/admin/assignments",
        data={
            "group_id": group.id,
            "week_start": week_start_for().isoformat(),
            "keyword_ids": [keyword.id, keyword_2.id],
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    assignments = list(
        db_session.scalars(
            select(GroupWeekKeywordAssignment).where(
                GroupWeekKeywordAssignment.group_id == group.id,
                GroupWeekKeywordAssignment.week_start == week_start_for(),
            )
        )
    )
    assert len(assignments) == 2
    assert {assignment.keyword_id for assignment in assignments} == {keyword.id, keyword_2.id}


def test_admin_can_change_own_password(client):
    login_as_admin(client)
    response = client.post("/admin/password", data={"new_password": "newpass123"}, follow_redirects=True)
    assert response.status_code == 200

    client.post("/admin/logout", follow_redirects=True)
    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "newpass123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
