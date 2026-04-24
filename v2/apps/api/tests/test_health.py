def test_health_ok(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_ok(client):
    r = client.get("/v1/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_openapi_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert body["info"]["title"] == "Open BSP API"
    assert "/v1/health" in str(body.get("paths", {}))
