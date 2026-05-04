"""Story 5.5: GET engine/status (sem dependencias pesadas)."""

from fastapi.testclient import TestClient


def test_engine_status_ok(client: TestClient) -> None:
    r = client.get(
        "/v1/me/engine/status",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert "enabled" in d
    assert isinstance(d["enabled"], bool)
