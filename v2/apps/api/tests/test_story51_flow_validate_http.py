"""Story 5.1: POST /me/flows/validate (sem DB)."""

from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "operator",
}


def test_validate_empty_graph_422(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/validate",
        headers=_HDR,
        json={"nodes": [], "edges": []},
    )
    assert r.status_code == 422
    body = r.json()
    assert body.get("code") == "validation_error"
    assert isinstance(body.get("errors"), list)


def test_validate_401_without_auth_stub_headers(client: TestClient) -> None:
    r = client.post("/v1/me/flows/validate", json={"nodes": [], "edges": []})
    assert r.status_code == 401


def test_validate_403_viewer_role(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/validate",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "viewer",
        },
        json={"nodes": [], "edges": []},
    )
    assert r.status_code == 403


def test_openapi_validate_post_documents_200_schema(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = spec.get("paths", {}).get("/v1/me/flows/validate", {}).get("post") or {}
    res200 = (op.get("responses") or {}).get("200") or {}
    content = (res200.get("content") or {}).get("application/json") or {}
    schema = content.get("schema") or {}
    props = schema.get("properties") if schema.get("type") == "object" else None
    if props is None and "$ref" in schema:
        key = schema["$ref"].rsplit("/", 1)[-1]
        resolved = (spec.get("components", {}).get("schemas", {}) or {}).get(key) or {}
        props = resolved.get("properties") or {}
    assert "valid" in props
    assert "errors" in props
