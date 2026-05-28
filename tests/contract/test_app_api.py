from app.db.models import WarningLog


def test_search_target_contract_success(client, api_headers):
    response = client.get("/api/v1/search-target", params={"member_no": "1001"}, headers=api_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["keyword"], str)
    assert isinstance(body["keyword_id"], str)


def test_invalid_api_key_returns_401(client):
    response = client.get(
        "/api/v1/search-target",
        params={"member_no": "1001"},
        headers={"X-API-Key": "wrong"},
    )
    assert response.status_code == 401
    assert response.json() == {"ok": False}


def test_search_attempt_contract_success(client, api_headers):
    target = client.get("/api/v1/search-target", params={"member_no": "1002"}, headers=api_headers).json()
    response = client.post(
        "/api/v1/search-attempts",
        json={"member_no": "1002", "keyword_id": target["keyword_id"]},
        headers=api_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
