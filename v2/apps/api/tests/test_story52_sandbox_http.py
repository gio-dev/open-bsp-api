"""Story 5.2: POST sandbox-run (sem depender de draft UUID)."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.routes import me_flows as me_flows_routes
from app.core.config import Settings

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "operator",
}
_BODY = {"fixture_message": {"type": "text", "body": "hi"}}


def _url(flow_key: str = "atdd-flow") -> str:
    return f"/v1/me/flows/{flow_key}/sandbox-run"


def test_sandbox_environment_production_rejected_422(client: TestClient) -> None:
    r = client.post(
        _url(),
        headers=_HDR,
        params={"environment": "production"},
        json=_BODY,
    )
    assert r.status_code == 422
    data = r.json()
    assert data.get("code") == "validation_error"
    errs = data.get("errors") or []
    assert any(e.get("field") == "environment" for e in errs)


def test_sandbox_401_without_dev_stub_headers(client: TestClient) -> None:
    r = client.post(_url(), json=_BODY)
    assert r.status_code == 401


def test_sandbox_403_viewer(client: TestClient) -> None:
    r = client.post(
        _url(),
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
        },
        json=_BODY,
    )
    assert r.status_code == 403


def test_sandbox_200_atdd_flow_has_persist_fixture_fields(client: TestClient) -> None:
    r = client.post(_url(), headers=_HDR, json=_BODY)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "persisted" in data
    assert "fixture_fingerprint" in data
    assert isinstance(data.get("trace"), list)
    assert any("fixture_fingerprint_sha256_16" in x for x in data["trace"])


def test_sandbox_atdd_flow_rejected_when_stub_disabled(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(
            auth_dev_stub=False,
            allow_atdd_sandbox_flow_key=False,
            database_url="postgresql+asyncpg://x:y@localhost:5432/db",
        ),
    ):
        r = client.post(_url(), headers=_HDR, json=_BODY)
    assert r.status_code == 422
    errs = (r.json().get("errors") or [])
    assert any(e.get("field") == "flow_id" for e in errs)


def test_sandbox_atdd_allowed_with_explicit_flag(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(
            auth_dev_stub=False,
            allow_atdd_sandbox_flow_key=True,
            database_url=None,
        ),
    ):
        r = client.post(_url(), headers=_HDR, json=_BODY)
    assert r.status_code == 200, r.text
    assert r.json()["persisted"] is False


def test_sandbox_helpers_atdd_key_policy() -> None:
    assert me_flows_routes._sandbox_atdd_flow_key_allowed(
        Settings(auth_dev_stub=True, allow_atdd_sandbox_flow_key=False),
    )
    assert me_flows_routes._sandbox_atdd_flow_key_allowed(
        Settings(auth_dev_stub=False, allow_atdd_sandbox_flow_key=True),
    )
    assert not me_flows_routes._sandbox_atdd_flow_key_allowed(
        Settings(auth_dev_stub=False, allow_atdd_sandbox_flow_key=False),
    )


def test_openapi_sandbox_post_200_schema_has_trace_fields(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = (
        spec.get("paths", {})
        .get("/v1/me/flows/{flow_id}/sandbox-run", {})
        .get("post")
        or {}
    )
    res200 = (op.get("responses") or {}).get("200") or {}
    content = (res200.get("content") or {}).get("application/json") or {}
    schema = content.get("schema") or {}
    props = schema.get("properties") if schema.get("type") == "object" else None
    if props is None and "$ref" in schema:
        key = schema["$ref"].rsplit("/", 1)[-1]
        resolved = (spec.get("components", {}).get("schemas", {}) or {}).get(key) or {}
        props = resolved.get("properties") or {}
    for key in ("persisted", "fixture_fingerprint", "trace", "correlation_id"):
        assert key in props
