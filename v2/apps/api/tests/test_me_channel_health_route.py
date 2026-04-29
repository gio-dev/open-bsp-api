"""Rotas GET channel-health: erros de infra (sem postgres obrigatorio)."""

from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
import sqlalchemy.exc as sa_exc
from fastapi.testclient import TestClient

_TENANT = "11111111-1111-4111-8111-111111111111"
_HDR = {"X-Dev-Tenant-Id": _TENANT, "X-Dev-Roles": "org_admin"}


def test_channel_health_503_on_sqlalchemy_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class _StubSettings:
        database_url = "postgresql+asyncpg://stub"

    monkeypatch.setattr(
        "app.api.routes.me_channel_health.get_settings",
        lambda: _StubSettings(),
    )

    @asynccontextmanager
    async def _fake_tenant_session(_tenant_id: object):
        yield None

    monkeypatch.setattr(
        "app.api.routes.me_channel_health.tenant_session",
        _fake_tenant_session,
    )

    async def _fail(*_a, **_kw):
        raise sa_exc.SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(
        "app.api.routes.me_channel_health.build_channel_health",
        _fail,
    )
    r = client.get("/v1/me/channel-health", headers=_HDR)
    assert r.status_code == 503, r.text
    body = r.json()
    assert "message" in body or "code" in body
