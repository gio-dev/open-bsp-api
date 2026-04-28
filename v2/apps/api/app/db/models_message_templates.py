"""Cache de message templates WhatsApp (Story 3.3)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WhatsappMessageTemplate(Base):
    __tablename__ = "whatsapp_message_templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    waba_id: Mapped[str] = mapped_column(String(128), nullable=False)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    meta_template_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    display_status: Mapped[str] = mapped_column(String(32), nullable=False)
    meta_status: Mapped[str] = mapped_column(String(64), nullable=False)
    status_detail: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    quality_score: Mapped[str | None] = mapped_column(String(32), nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class WhatsappChannelSnapshot(Base):
    """Ultimo snapshot de sinais de canal (qualidade / tier) por WABA+ambiente."""

    __tablename__ = "whatsapp_channel_snapshots"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    waba_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    environment: Mapped[str] = mapped_column(String(32), primary_key=True)
    quality_rating: Mapped[str | None] = mapped_column(String(32), nullable=True)
    messaging_limit_tier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signal_source: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
