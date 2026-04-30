"""Story 5.4: GET versions sem Postgres (503 quando BD ausente)."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import Settings

_HDR_ADMIN = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}
_HDR_VIEWER = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "viewer",
}


def test_versions_list_viewer_allowed_atdd_flow(client: TestClient) -> None:
    """Qualquer papel tenant pode ler historico material (Story 5.4)."""
    r = client.get(
        "/v1/me/flows/atdd-flow/versions",
        headers=_HDR_VIEWER,
        params={"limit": 5, "offset": 0},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("items"), list)


def test_versions_list_requires_db_else_503(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(database_url=None, auth_dev_stub=True),
    ):
        r = client.get(
            "/v1/me/flows/atdd-flow/versions",
            headers=_HDR_ADMIN,
        )
    assert r.status_code == 503


def test_versions_detail_requires_db_else_503(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(database_url=None, auth_dev_stub=True),
    ):
        r = client.get(
            f"/v1/me/flows/atdd-flow/versions/{uuid.uuid4()}",
            headers=_HDR_ADMIN,
        )
    assert r.status_code == 503
