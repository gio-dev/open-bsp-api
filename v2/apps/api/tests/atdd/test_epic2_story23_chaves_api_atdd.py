"""ATDD Story 2.3 - API keys issue/revoke."""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic2_atdd]


def _openapi_paths(client: TestClient) -> dict:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json().get("paths", {})


def test_story_23_openapi_includes_api_keys(client: TestClient) -> None:
    """2.3: rotas /v1/me/api-keys documentadas (CDA)."""
    paths = _openapi_paths(client)
    assert "/v1/me/api-keys" in paths
    assert "get" in paths["/v1/me/api-keys"]
    assert "post" in paths["/v1/me/api-keys"]
    patch_key = next(
        (p for p in paths if p.startswith("/v1/me/api-keys/") and "{" in p),
        None,
    )
    assert patch_key, "PATCH /v1/me/api-keys/{key_id} documentado"
    assert "patch" in paths[patch_key]


def test_story_23_post_api_key_returns_secret_once(client: TestClient) -> None:
    """2.3: POST cria chave; 201 com secret mostrado uma vez."""
    r = client.post(
        "/v1/me/api-keys",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "X-Dev-Roles": "org_admin",
        },
        json={"name": "atdd-key"},
    )
    if r.status_code == 503:
        pytest.skip("database not configured in this runner")
    assert r.status_code == 201, r.text
    body = r.json()
    assert "secret" in body or "key_prefix" in body
    assert "secret" in body

    r2 = client.get(
        "/v1/me/api-keys",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r2.status_code == 200
    for item in r2.json().get("items", []):
        assert "secret" not in item
