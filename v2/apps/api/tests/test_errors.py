def test_not_found_returns_canonical_error(client):
    r = client.get("/v1/does-not-exist")
    assert r.status_code == 404
    body = r.json()
    assert "code" in body
    assert "message" in body
    assert "request_id" in body
    assert r.headers.get("x-request-id") == body["request_id"]


def test_request_id_echo_from_header(client):
    r = client.get("/v1/health", headers={"x-request-id": "fixed-id-123"})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == "fixed-id-123"
