"""ATDD Story 1.2 - tenant foundation + RLS (RED until DS)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic1_atdd]


@pytest.mark.atdd
def test_story_12_tenant_context_module_file_exists():
    """RED: tenant/DB context module file must exist (story 1.2)."""
    app_root = Path(__file__).resolve().parents[2] / "app"
    ok = (
        (app_root / "tenancy" / "context.py").is_file()
        or (app_root / "db" / "session.py").is_file()
        or (app_root / "core" / "tenant_context.py").is_file()
    )
    assert ok, (
        "Story 1.2: add app/tenancy/context.py, app/db/session.py, or "
        "app/core/tenant_context.py with SET LOCAL / tenant resolution."
    )


@pytest.mark.atdd
def test_story_12_alembic_ini_exists():
    """RED: Alembic must be initialized under v2/apps/api."""
    root = Path(__file__).resolve().parents[2]
    assert (root / "alembic.ini").is_file(), (
        "Add alembic.ini at v2/apps/api root per story 1.2."
    )
    assert (root / "alembic").is_dir(), "Add alembic/ directory with revisions."


@pytest.mark.atdd
def test_story_12_openapi_lists_me_organization(client: TestClient):
    """RED: OpenAPI must list GET /v1/me/organization (story 1.3 VS)."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/v1/me/organization" in paths, (
        "Expose GET /v1/me/organization in OpenAPI after 1.2/1.3 implementation."
    )
