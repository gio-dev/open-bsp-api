"""RBAC Story 2.4: viewer nao roda segredo de webhook."""

from fastapi.testclient import TestClient


def test_viewer_cannot_rotate_webhook_secret(client: TestClient) -> None:
    r = client.post(
        "/v1/me/webhook-secrets/rotate",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
        json={},
    )
    assert r.status_code == 403
    assert r.json().get("code") == "http_403"
