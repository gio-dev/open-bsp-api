"""Agregados de uso por tenant (Story 8.1 FR41)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from app.db.base import Base

# Contrato MVP de metricas (OpenAPI / FR41); alinhar incrementos em usage_metering.
USAGE_METRIC_INBOUND_MESSAGES = "inbound_messages"
USAGE_METRIC_OUTBOUND_MESSAGES_ACCEPTED = "outbound_messages_accepted"

USAGE_METRIC_KEYS_KNOWN: frozenset[str] = frozenset(
    {
        USAGE_METRIC_INBOUND_MESSAGES,
        USAGE_METRIC_OUTBOUND_MESSAGES_ACCEPTED,
    },
)


class TenantMeteringDaily(Base):
    """Contadores diarios (UTC) por tenant; RLS por tenant_id."""

    __tablename__ = "tenant_metering_daily"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "bucket_date",
            "metric_key",
            name="uq_tenant_metering_daily_tenant_bucket_metric",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    bucket_date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_key: Mapped[str] = mapped_column(String(64), nullable=False)
    count: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
