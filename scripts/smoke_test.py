from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def fetch_json(url: str, *, headers: dict[str, str] | None = None, data: dict[str, str] | None = None) -> dict:
    payload = None
    request_headers = headers or {}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = Request(url, headers=request_headers, data=payload)
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
    api_key = os.environ.get("API_SHARED_KEY")
    member_no = os.environ.get("SMOKE_MEMBER_NO")

    health = fetch_json(f"{base_url}/health")
    print("health:", health)

    if not api_key or not member_no:
        print("API_SHARED_KEY or SMOKE_MEMBER_NO not set; skipping app API smoke.")
        return

    target = fetch_json(
        f"{base_url}/api/v1/search-target?{urlencode({'member_no': member_no})}",
        headers={"X-API-Key": api_key},
    )
    print("target:", target)
    if not target.get("ok"):
        return

    attempt = fetch_json(
        f"{base_url}/api/v1/search-attempts",
        headers={"X-API-Key": api_key},
        data={"member_no": member_no, "keyword_id": target["keyword_id"]},
    )
    print("attempt:", attempt)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as exc:
        print("HTTP error:", exc.code, exc.read().decode("utf-8"))
        raise
