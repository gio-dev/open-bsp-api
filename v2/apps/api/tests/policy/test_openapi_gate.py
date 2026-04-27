"""OpenAPI policy gate: contract published and meets minimal repo rules (CI)."""

import pytest


@pytest.mark.policy
def test_openapi_is_openapi_v3(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    version = spec.get("openapi", "")
    assert str(version).startswith("3."), f"expected OpenAPI 3.x, got {version!r}"


@pytest.mark.policy
def test_openapi_info_and_public_paths(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    info = spec.get("info") or {}
    assert info.get("title"), "info.title is required"
    assert info.get("version") is not None, "info.version is required"

    paths = spec.get("paths") or {}
    assert "/v1/health" in paths, "public health path must be documented"
    assert "/v1/ready" in paths, "public ready path must be documented"
    assert "get" in paths["/v1/health"], "/v1/health must declare GET"
    assert "get" in paths["/v1/ready"], "/v1/ready must declare GET"


@pytest.mark.policy
def test_openapi_json_is_cached_safe_for_ci(client):
    """Response must be JSON object (pipeline tools and diffs assume object root)."""
    r = client.get("/openapi.json")
    assert r.headers.get("content-type", "").startswith("application/json")
    body = r.json()
    assert isinstance(body, dict)


@pytest.mark.policy
def test_me_organization_documents_error_envelope(client):
    """AC4: erros documentados; 422 inclui lista `errors` (Story 1.3)."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    paths = spec.get("paths") or {}
    for method in ("get", "patch"):
        op = paths.get("/v1/me/organization", {}).get(method) or {}
        responses = op.get("responses") or {}
        for code in ("401", "403", "404", "422", "503"):
            assert code in responses, (
                f"{method.upper()} /v1/me/organization must document HTTP {code}"
            )
        for code in ("401", "403", "404", "503"):
            content = responses[code].get("content") or {}
            schema = (content.get("application/json") or {}).get("schema") or {}
            if schema.get("type") == "object":
                props = schema.get("properties") or {}
            else:
                props = {}
            if "$ref" in schema:
                ref = schema["$ref"]
                components = spec.get("components", {}).get("schemas", {})
                key = ref.rsplit("/", 1)[-1]
                ref_schema = components.get(key) or {}
                props = ref_schema.get("properties") or {}
            assert "code" in props and "message" in props and "request_id" in props, (
                f"{code} response must expose canonical error fields (got {schema!r})"
            )
        content422 = responses["422"].get("content") or {}
        schema422 = (content422.get("application/json") or {}).get("schema") or {}
        props422: dict = {}
        if "$ref" in schema422:
            key422 = schema422["$ref"].rsplit("/", 1)[-1]
            ref422 = spec.get("components", {}).get("schemas", {}).get(key422) or {}
            props422 = ref422.get("properties") or {}
        elif schema422.get("type") == "object":
            props422 = schema422.get("properties") or {}
        for key in ("code", "message", "request_id", "errors"):
            assert key in props422, f"422 must include {key} (got {props422!r})"


def _assert_error_envelope_fields(spec: dict, schema: dict) -> None:
    if schema.get("type") == "object":
        props = schema.get("properties") or {}
    else:
        props = {}
    if "$ref" in schema:
        ref = schema["$ref"]
        key = ref.rsplit("/", 1)[-1]
        comp = spec.get("components", {}).get("schemas", {}).get(key) or {}
        props = comp.get("properties") or {}
    assert "code" in props and "message" in props and "request_id" in props, (
        f"response must expose canonical error fields (got {schema!r})"
    )


@pytest.mark.policy
def test_auth_session_documents_errors(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = spec.get("paths", {}).get("/v1/auth/session", {}).get("get") or {}
    responses = op.get("responses") or {}
    for code in ("401", "503"):
        assert code in responses, f"GET /v1/auth/session must document HTTP {code}"
        content = responses[code].get("content") or {}
        schema = (content.get("application/json") or {}).get("schema") or {}
        _assert_error_envelope_fields(spec, schema)


@pytest.mark.policy
def test_me_api_keys_post_documents_errors(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = spec.get("paths", {}).get("/v1/me/api-keys", {}).get("post") or {}
    responses = op.get("responses") or {}
    for code in (
        "400",
        "401",
        "403",
        "409",
        "422",
        "429",
        "503",
    ):
        assert code in responses, f"POST /v1/me/api-keys must document HTTP {code}"
        if code in ("400", "401", "403", "409", "429", "503"):
            content = responses[code].get("content") or {}
            schema = (content.get("application/json") or {}).get("schema") or {}
            _assert_error_envelope_fields(spec, schema)


@pytest.mark.policy
def test_me_members_get_documents_errors(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = spec.get("paths", {}).get("/v1/me/members", {}).get("get") or {}
    responses = op.get("responses") or {}
    for code in ("401", "403", "503"):
        assert code in responses, f"GET /v1/me/members must document HTTP {code}"
        content = responses[code].get("content") or {}
        schema = (content.get("application/json") or {}).get("schema") or {}
        _assert_error_envelope_fields(spec, schema)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    op = spec.get("paths", {}).get("/v1/me/waba-phone-numbers", {}).get("get") or {}
    names = {p.get("name") for p in op.get("parameters", [])}
    assert "limit" in names
    assert "cursor" in names
    assert "environment" in names
