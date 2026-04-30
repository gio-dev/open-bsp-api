"""Story 5.3: POST publish (sem Postgres obrigatorio para 403/atdd-flow policy)."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import Settings

_HDR_OP = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "operator",
}
_HDR_ADMIN = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}
_HDR_VIEWER = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "viewer",
}


def test_publish_403_viewer(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR_VIEWER,
        json={"environment": "staging"},
    )
    assert r.status_code == 403


def test_publish_operator_prod_403(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR_OP,
        json={"environment": "production"},
    )
    assert r.status_code == 403


def test_publish_finance_staging_403(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "finance",
        },
        json={"environment": "staging"},
    )
    assert r.status_code == 403


def test_publish_support_staging_403(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "support",
        },
        json={"environment": "staging"},
    )
    assert r.status_code == 403


def test_publish_operator_staging_requires_db_else_503(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(database_url=None, auth_dev_stub=True),
    ):
        r = client.post(
            "/v1/me/flows/atdd-flow/publish",
            headers=_HDR_OP,
            json={"environment": "staging"},
        )
    assert r.status_code == 503


def test_publish_atdd_flow_policy_when_stub_disabled(client: TestClient) -> None:
    with patch(
        "app.api.routes.me_flows.get_settings",
        return_value=Settings(
            auth_dev_stub=False,
            allow_atdd_sandbox_flow_key=False,
            database_url="postgresql+asyncpg://x:y@localhost:5432/db",
        ),
    ):
        r = client.post(
            "/v1/me/flows/atdd-flow/publish",
            headers=_HDR_ADMIN,
            json={"environment": "staging"},
        )
    assert r.status_code == 422
    errs = r.json().get("errors") or []
    assert any(e.get("field") == "flow_id" for e in errs)


def test_roles_may_publish_flow_matrix() -> None:
    from app.tenancy.rbac import roles_may_publish_flow

    admin = frozenset({"org_admin"})
    operator = frozenset({"operator"})
    assert roles_may_publish_flow(admin, environment="production")
    assert roles_may_publish_flow(operator, environment="staging")
    assert roles_may_publish_flow(operator, environment="development")
    assert not roles_may_publish_flow(operator, environment="production")
