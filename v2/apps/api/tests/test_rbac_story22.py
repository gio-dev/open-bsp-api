"""RBAC Story 2.2: 403 quando papel nao autorizado."""

from fastapi.testclient import TestClient


def test_viewer_cannot_create_waba_phone(client: TestClient) -> None:
    r = client.post(
        "/v1/me/waba-phone-numbers",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
        json={
            "waba_id": "w",
            "phone_number_id": "p",
            "display_phone_number": "+1",
            "environment": "production",
        },
    )
    assert r.status_code == 403
    assert r.json().get("code") == "http_403"


def test_viewer_cannot_list_members(client: TestClient) -> None:
    r = client.get(
        "/v1/me/members",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
    )
    assert r.status_code == 403
    assert r.json().get("code") == "http_403"

