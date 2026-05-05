"""Incremento e leitura de contadores diarios (Story 8.1)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_usage import (
    USAGE_METRIC_KEYS_KNOWN,
    TenantMeteringDaily,
)

_UPSERT_SQL = text(
    """
    INSERT INTO tenant_metering_daily (id, tenant_id, bucket_date, metric_key, count)
    VALUES (
        gen_random_uuid(),
        CAST(:tid AS uuid),
        CAST(:bd AS date),
        :mk,
        :delta
    )
    ON CONFLICT ON CONSTRAINT uq_tenant_metering_daily_tenant_bucket_metric
    DO UPDATE SET
        count = tenant_metering_daily.count + EXCLUDED.count,
        updated_at = now()
    """
)


def _utc_date(at: datetime | None) -> date:
    ts = at if at is not None else datetime.now(timezone.utc)
    return ts.astimezone(timezone.utc).date()


async def increment_tenant_daily_metric(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    metric_key: str,
    delta: int = 1,
    at: datetime | None = None,
) -> None:
    if metric_key not in USAGE_METRIC_KEYS_KNOWN or delta <= 0:
        return
    bucket = _utc_date(at)
    await session.execute(
        _UPSERT_SQL,
        {
            "tid": str(tenant_id),
            "bd": bucket,
            "mk": metric_key,
            "delta": delta,
        },
    )


async def sum_usage_by_metric(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    period_start: date,
    period_end: date,
) -> dict[str, int]:
    stmt = (
        select(TenantMeteringDaily.metric_key, func.sum(TenantMeteringDaily.count))
        .where(
            TenantMeteringDaily.tenant_id == tenant_id,
            TenantMeteringDaily.bucket_date >= period_start,
            TenantMeteringDaily.bucket_date <= period_end,
        )
        .group_by(TenantMeteringDaily.metric_key)
    )
    rows = (await session.execute(stmt)).all()
    return {str(k): int(v or 0) for k, v in rows}


def default_usage_period_utc(
    *,
    today: date | None = None,
    days_inclusive: int = 30,
) -> tuple[date, date]:
    end = today or datetime.now(timezone.utc).date()
    start = end - timedelta(days=days_inclusive - 1)
    return start, end
