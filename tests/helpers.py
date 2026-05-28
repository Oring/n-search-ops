from fastapi.testclient import TestClient


def login_as_admin(client: TestClient, username: str = "admin", password: str = "admin1234") -> None:
    response = client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
