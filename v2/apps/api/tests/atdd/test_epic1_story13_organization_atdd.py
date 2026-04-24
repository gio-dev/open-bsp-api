"""ATDD Story 1.3 - organization profile (FR1), RED phase."""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic1_atdd]


@pytest.mark.atdd
def test_story_13_get_me_organization_returns_200(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    """RED: GET /v1/me/organization with tenant context (dev stub)."""
    r = client.get("/v1/me/organization", headers=atdd_dev_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "display_name" in body or "name" in body, body
    assert "timezone" in body, body
    assert "operational_email" in body, body


@pytest.mark.atdd
def test_story_13_patch_me_organization_updates_display_name(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    """RED: PATCH updates display name and persists."""
    payload = {"display_name": "ATDD Org Alpha", "timezone": "Europe/Lisbon"}
    r = client.patch("/v1/me/organization", headers=atdd_dev_headers, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("display_name") == "ATDD Org Alpha"

    r2 = client.get("/v1/me/organization", headers=atdd_dev_headers)
    assert r2.status_code == 200
    assert r2.json().get("display_name") == "ATDD Org Alpha"


@pytest.mark.atdd
def test_story_13_cross_tenant_isolation_returns_403_or_404(
    client: TestClient,
):
    """RED: without valid tenant context, must not expose data."""
    r = client.get("/v1/me/organization")
    assert r.status_code in (401, 403, 404), r.text


@pytest.mark.atdd
def test_story_13_viewer_reads_org_but_cannot_patch(client: TestClient):
    """Story 2.2: viewer le org; PATCH exige org_admin."""
    headers = {
        "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
        "X-Dev-Roles": "viewer",
        "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    }
    r = client.get("/v1/me/organization", headers=headers)
    assert r.status_code in (200, 503), r.text
    r2 = client.patch(
        "/v1/me/organization",
        headers=headers,
        json={"display_name": "No"},
    )
    assert r2.status_code == 403, r2.text


@pytest.mark.atdd
def test_story_13_patch_invalid_operational_email_422(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    r = client.patch(
        "/v1/me/organization",
        headers=atdd_dev_headers,
        json={"operational_email": "not-an-email"},
    )
    assert r.status_code == 422, r.text
    body = r.json()
    assert body.get("code") == "validation_error"
    assert "errors" in body and isinstance(body["errors"], list)
    fields = {e.get("field") for e in body["errors"] if isinstance(e, dict)}
    assert "operational_email" in fields


@pytest.mark.atdd
def test_story_13_patch_invalid_timezone_422(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    r = client.patch(
        "/v1/me/organization",
        headers=atdd_dev_headers,
        json={"timezone": "Not/A/Real/Zone"},
    )
    assert r.status_code == 422, r.text
    body = r.json()
    assert body.get("code") == "validation_error"
    fields = {e.get("field") for e in body.get("errors", []) if isinstance(e, dict)}
    assert "timezone" in fields


@pytest.mark.atdd
def test_story_13_patch_operational_email_strips_whitespace(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    r = client.patch(
        "/v1/me/organization",
        headers=atdd_dev_headers,
        json={"operational_email": "  trimmed@example.com  "},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("operational_email") == "trimmed@example.com"

    r2 = client.patch(
        "/v1/me/organization",
        headers=atdd_dev_headers,
        json={"operational_email": "   "},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json().get("operational_email") == ""
