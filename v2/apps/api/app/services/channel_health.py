"""Agregacao tenant-scoped de sinais de canal / fila (Story 4.4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_inbox import InboxConversationHandoff
from app.db.models_outbound import OutboundWhatsappMessage

StaleQueuedMinutes = 15


@dataclass(frozen=True, slots=True)
class ChannelHealthCounts:
    outbound_failed_meta: int
    outbound_failed_platform: int
    outbound_rate_limited: int
    outbound_stale_queued: int
    handoff_failed: int


@dataclass(frozen=True, slots=True)
class ChannelHealthSignalData:
    source: Literal["meta", "platform", "unknown"]
    severity: Literal["warning", "critical"]
    code: str
    summary: str
    next_step: str
    count: int


def _build_signals(counts: ChannelHealthCounts) -> list[ChannelHealthSignalData]:
    signals: list[ChannelHealthSignalData] = []

    if counts.outbound_failed_platform > 0:
        signals.append(
            ChannelHealthSignalData(
                source="platform",
                severity="critical",
                code="outbound_failed_platform",
                summary=(
                    f"{counts.outbound_failed_platform} envio(s) falharam por "
                    "configuracao ou servico interno."
                ),
                next_step=(
                    "Erro da plataforma: contacte suporte com o request_id deste "
                    "pedido."
                ),
                count=counts.outbound_failed_platform,
            )
        )

    if counts.handoff_failed > 0:
        signals.append(
            ChannelHealthSignalData(
                source="unknown",
                severity="warning",
                code="handoff_failed",
                summary=(
                    f"{counts.handoff_failed} conversa(s) com handoff em estado "
                    "falhado."
                ),
                next_step=(
                    "Revise filas e estado de roteamento na inbox; reabra handoff se "
                    "aplicavel."
                ),
                count=counts.handoff_failed,
            )
        )

    if counts.outbound_stale_queued > 0:
        signals.append(
            ChannelHealthSignalData(
                source="platform",
                severity="warning",
                code="outbound_stale_queued",
                summary=(
                    f"{counts.outbound_stale_queued} mensagem(ns) de saida presas na "
                    "fila alem do tempo esperado."
                ),
                next_step=(
                    "Verifique se o processamento da fila (sweep/worker) esta ativo e "
                    "se ha erros repetidos nos logs."
                ),
                count=counts.outbound_stale_queued,
            )
        )

    if counts.outbound_failed_meta > 0:
        signals.append(
            ChannelHealthSignalData(
                source="meta",
                severity="warning",
                code="outbound_failed_meta",
                summary=(
                    f"{counts.outbound_failed_meta} envio(s) falharam na API Meta "
                    "(ex.: politica, template, numero)."
                ),
                next_step=(
                    "Confirme templates aprovados, limites da WABA e codigo de erro "
                    "nas mensagens falhadas."
                ),
                count=counts.outbound_failed_meta,
            )
        )

    if counts.outbound_rate_limited > 0:
        signals.append(
            ChannelHealthSignalData(
                source="meta",
                severity="warning",
                code="outbound_rate_limited",
                summary=(
                    f"{counts.outbound_rate_limited} envio(s) em espera por limite "
                    "de taxa (429) da Meta."
                ),
                next_step=(
                    "Aguarde o retry automatico ou reduza o ritmo de envio; verifique "
                    "quotas na Meta Business."
                ),
                count=counts.outbound_rate_limited,
            )
        )

    crit = [s for s in signals if s.severity == "critical"]
    warn = [s for s in signals if s.severity == "warning"]
    return crit + warn


async def compute_channel_health_counts(
    session: AsyncSession,
) -> ChannelHealthCounts:
    """Contadores apenas sobre linhas visiveis ao tenant (RLS + sessao)."""
    failed_meta = await session.scalar(
        select(func.count())
        .select_from(OutboundWhatsappMessage)
        .where(
            OutboundWhatsappMessage.status == "failed",
            OutboundWhatsappMessage.upstream_fault == "meta",
        )
    )
    failed_platform = await session.scalar(
        select(func.count())
        .select_from(OutboundWhatsappMessage)
        .where(
            OutboundWhatsappMessage.status == "failed",
            or_(
                OutboundWhatsappMessage.upstream_fault.is_(None),
                OutboundWhatsappMessage.upstream_fault != "meta",
            ),
        )
    )
    rate_limited = await session.scalar(
        select(func.count())
        .select_from(OutboundWhatsappMessage)
        .where(OutboundWhatsappMessage.status == "rate_limited")
    )
    stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=StaleQueuedMinutes)
    stale_queued = await session.scalar(
        select(func.count())
        .select_from(OutboundWhatsappMessage)
        .where(
            OutboundWhatsappMessage.status == "queued",
            OutboundWhatsappMessage.created_at < stale_cutoff,
        )
    )
    handoff_failed = await session.scalar(
        select(func.count())
        .select_from(InboxConversationHandoff)
        .where(InboxConversationHandoff.handoff_state == "failed")
    )

    return ChannelHealthCounts(
        outbound_failed_meta=int(failed_meta or 0),
        outbound_failed_platform=int(failed_platform or 0),
        outbound_rate_limited=int(rate_limited or 0),
        outbound_stale_queued=int(stale_queued or 0),
        handoff_failed=int(handoff_failed or 0),
    )


async def build_channel_health(
    session: AsyncSession,
) -> tuple[bool, ChannelHealthCounts, list[ChannelHealthSignalData]]:
    """Contadores via RLS da sessao (`app.tenant_id`)."""
    counts = await compute_channel_health_counts(session)
    signals = _build_signals(counts)
    healthy = len(signals) == 0
    return healthy, counts, signals
