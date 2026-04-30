"""Modelos DB: fluxos (5.1), runs sandbox (5.2), publish activo (5.3), versoes (5.4)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TenantFlowSandboxRun(Base):
    """Preview sandbox (Story 5.2); apenas environment=sandbox."""

    __tablename__ = "tenant_flow_sandbox_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    flow_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenant_flow_drafts.id", ondelete="SET NULL"),
        nullable=True,
    )
    flow_external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    fixture: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    trace: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class TenantFlowDraft(Base):
    __tablename__ = "tenant_flow_drafts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    definition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class TenantFlowPublishActivation(Base):
    """Versao publicada activa por ambiente runtime (Story 5.3).

    `flow_draft_id` referencia `tenant_flow_drafts`; ON DELETE CASCADE remove esta
    activacao se o rascunho for apagado (re-publish requer novo draft ou chave stub).
    """

    __tablename__ = "tenant_flow_publish_activations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    flow_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenant_flow_drafts.id", ondelete="CASCADE"),
        nullable=True,
    )
    flow_external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    definition_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    definition_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    activated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )


class TenantFlowPublishVersion(Base):
    """Historico append-only de cada publicacao material (Story 5.4).

    Sem UPDATE nem DELETE ao nivel de papel `app_runtime` (restricao concedida na
    migracao). Idempotencia de publish repetido na mesma fingerprint nao cria linha.
    """

    __tablename__ = "tenant_flow_publish_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    flow_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenant_flow_drafts.id", ondelete="CASCADE"),
        nullable=True,
    )
    flow_external_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    definition_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    definition_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    published_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    publish_activation_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenant_flow_publish_activations.id", ondelete="SET NULL"),
        nullable=True,
    )
