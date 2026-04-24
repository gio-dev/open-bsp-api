"""Minimal smoke: proves the ASGI app responds on the public health route."""

import pytest


@pytest.mark.smoke
def test_health_liveness(client):
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
