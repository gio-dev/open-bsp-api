"""Postgres RLS isolation (Story 1.2 AC1). Requires DATABASE_URL + ALEMBIC_SYNC_URL."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
import sqlalchemy.exc as sa_exc
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rls_hides_other_tenant_settings_rows() -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    app_url = os.environ["DATABASE_URL"]

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    row_a = uuid.uuid4()
    row_b = uuid.uuid4()

    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s), (%s)",
                (str(tenant_a), str(tenant_b)),
            )
            cur.execute(
                "INSERT INTO tenant_settings_stub (id, tenant_id) "
                "VALUES (%s, %s), (%s, %s)",
                (str(row_a), str(tenant_a), str(row_b), str(tenant_b)),
            )

    engine = create_async_engine(app_url)
    try:
        async with engine.connect() as conn:
            async with conn.begin():
                bypass = await conn.scalar(
                    text(
                        "SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user"
                    )
                )
                assert bypass is False

                await conn.execute(
                    text("SELECT set_config('app.tenant_id', :t, true)"),
                    {"t": str(tenant_a)},
                )
                hidden = await conn.scalar(
                    text(
                        "SELECT count(*) FROM tenant_settings_stub "
                        "WHERE tenant_id = CAST(:tid AS uuid)"
                    ),
                    {"tid": str(tenant_b)},
                )
                assert hidden == 0

                visible = await conn.scalar(
                    text(
                        "SELECT count(*) FROM tenant_settings_stub "
                        "WHERE tenant_id = CAST(:tid AS uuid)"
                    ),
                    {"tid": str(tenant_a)},
                )
                assert visible == 1
    finally:
        await engine.dispose()
        with psycopg.connect(admin_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for tid in (str(tenant_a), str(tenant_b)):
                    cur.execute(
                        "DELETE FROM tenant_settings_stub WHERE tenant_id = %s::uuid",
                        (tid,),
                    )
                    cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (tid,))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rls_denies_insert_for_foreign_tenant() -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    app_url = os.environ["DATABASE_URL"]

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    row_a = uuid.uuid4()
    row_b = uuid.uuid4()
    evil_id = uuid.uuid4()

    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s), (%s)",
                (str(tenant_a), str(tenant_b)),
            )
            cur.execute(
                "INSERT INTO tenant_settings_stub (id, tenant_id) "
                "VALUES (%s, %s), (%s, %s)",
                (str(row_a), str(tenant_a), str(row_b), str(tenant_b)),
            )

    engine = create_async_engine(app_url)
    try:
        async with engine.connect() as conn:
            async with conn.begin():
                await conn.execute(
                    text("SELECT set_config('app.tenant_id', :t, true)"),
                    {"t": str(tenant_a)},
                )
                with pytest.raises(sa_exc.DBAPIError, match="row-level security"):
                    await conn.execute(
                        text(
                            "INSERT INTO tenant_settings_stub (id, tenant_id) "
                            "VALUES (CAST(:id AS uuid), CAST(:tid AS uuid))"
                        ),
                        {"id": str(evil_id), "tid": str(tenant_b)},
                    )
    finally:
        await engine.dispose()
        with psycopg.connect(admin_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for tid in (str(tenant_a), str(tenant_b)):
                    cur.execute(
                        "DELETE FROM tenant_settings_stub WHERE tenant_id = %s::uuid",
                        (tid,),
                    )
                    cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (tid,))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rls_update_other_tenant_row_affects_zero_rows() -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    app_url = os.environ["DATABASE_URL"]

    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    row_a = uuid.uuid4()
    row_b = uuid.uuid4()

    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s), (%s)",
                (str(tenant_a), str(tenant_b)),
            )
            cur.execute(
                "INSERT INTO tenant_settings_stub (id, tenant_id) "
                "VALUES (%s, %s), (%s, %s)",
                (str(row_a), str(tenant_a), str(row_b), str(tenant_b)),
            )

    engine = create_async_engine(app_url)
    try:
        async with engine.connect() as conn:
            async with conn.begin():
                await conn.execute(
                    text("SELECT set_config('app.tenant_id', :t, true)"),
                    {"t": str(tenant_a)},
                )
                result = await conn.execute(
                    text(
                        "UPDATE tenant_settings_stub SET display_name = 'cross-tenant' "
                        "WHERE id = CAST(:id AS uuid)"
                    ),
                    {"id": str(row_b)},
                )
                assert result.rowcount == 0
    finally:
        await engine.dispose()
        with psycopg.connect(admin_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for tid in (str(tenant_a), str(tenant_b)):
                    cur.execute(
                        "DELETE FROM tenant_settings_stub WHERE tenant_id = %s::uuid",
                        (tid,),
                    )
                    cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (tid,))
