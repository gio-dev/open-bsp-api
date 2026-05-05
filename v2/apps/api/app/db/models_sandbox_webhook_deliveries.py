"""Registo por pedido HTTP ao processar webhook (Story 7.3 FR39)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TenantSandboxWebhookDelivery(Base):
    """Uma linha por (tenant, POST processado) para reconciliacao com ``request_id``."""

    __tablename__ = "tenant_sandbox_webhook_deliveries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('accepted')",
            name="ck_tenant_sandbox_webhook_deliveries_status",
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
    request_id: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    enqueued: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    deduplicated: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
