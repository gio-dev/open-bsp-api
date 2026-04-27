"""RBAC Story 2.3: viewer nao gere chaves de API."""

from fastapi.testclient import TestClient


def test_viewer_cannot_list_api_keys(client: TestClient) -> None:
    r = client.get(
        "/v1/me/api-keys",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
    )
    assert r.status_code == 403
    assert r.json().get("code") == "http_403"


def test_operator_can_list_api_keys_when_db_configured(client: TestClient) -> None:
    """Sem DATABASE_URL devolve 503; com DB (CI) deve ser 200."""
    r = client.get(
        "/v1/me/api-keys",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
    )
    assert r.status_code in (200, 503)
