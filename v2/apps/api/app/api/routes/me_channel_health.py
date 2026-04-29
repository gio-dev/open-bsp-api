"""GET /v1/me/channel-health - sinais de fila/Meta/plataforma (Story 4.4)."""

from __future__ import annotations

from typing import Annotated, Literal

import sqlalchemy.exc as sa_exc
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.errors import (
    CanonicalErrorResponse,
)
from app.db.session import tenant_session
from app.services.channel_health import (
    ChannelHealthCounts,
    ChannelHealthSignalData,
    build_channel_health,
)
from app.tenancy.deps import TenantUserContext, console_tenant_user_context

router = APIRouter(tags=["inbox"])


class ChannelHealthSignalOut(BaseModel):
    source: Literal["meta", "platform", "unknown"]
    severity: Literal["warning", "critical"]
    code: str
    summary: str
    next_step: str
    count: int = Field(ge=0)


class ChannelHealthCountsOut(BaseModel):
    outbound_failed_meta: int = Field(ge=0)
    outbound_failed_platform: int = Field(ge=0)
    outbound_rate_limited: int = Field(ge=0)
    outbound_stale_queued: int = Field(ge=0)
    handoff_failed: int = Field(ge=0)


class ChannelHealthResponse(BaseModel):
    """Telemetria minima para a consola; apenas dados do tenant autenticado."""

    healthy: bool = Field(
        description=(
            "False quando existe pelo menos um sinal de atencao ou critico "
            "(honesto: nao esconde falhas)."
        ),
    )
    incidents: list[ChannelHealthSignalOut]
    counts: ChannelHealthCountsOut


_CH_ERROR_RESPONSES = {
    401: {
        "model": CanonicalErrorResponse,
        "description": "Sessao/autenticacao em falta.",
    },
    403: {
        "model": CanonicalErrorResponse,
        "description": "Contexto de tenant em falta ou papel insuficiente.",
    },
    503: {
        "model": CanonicalErrorResponse,
        "description": "DATABASE_URL nao configurada ou servico indisponivel.",
    },
}


def _to_out(
    counts: ChannelHealthCounts, signals: list[ChannelHealthSignalData]
) -> ChannelHealthResponse:
    return ChannelHealthResponse(
        healthy=len(signals) == 0,
        incidents=[
            ChannelHealthSignalOut(
                source=s.source,
                severity=s.severity,
                code=s.code,
                summary=s.summary,
                next_step=s.next_step,
                count=s.count,
            )
            for s in signals
        ],
        counts=ChannelHealthCountsOut(
            outbound_failed_meta=counts.outbound_failed_meta,
            outbound_failed_platform=counts.outbound_failed_platform,
            outbound_rate_limited=counts.outbound_rate_limited,
            outbound_stale_queued=counts.outbound_stale_queued,
            handoff_failed=counts.handoff_failed,
        ),
    )


@router.get(
    "/me/channel-health",
    response_model=ChannelHealthResponse,
    responses=_CH_ERROR_RESPONSES,
    summary="Sinais de saude do canal (tenant)",
    response_model_exclude_none=True,
)
async def get_channel_health(
    response: Response,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> ChannelHealthResponse:
    """Agrega fila outbound, limites Meta e falhas de handoff (escopo RLS)."""
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    response.headers["Cache-Control"] = "private, max-age=15"
    try:
        async with tenant_session(ctx.tenant_id) as session:
            _, counts, signals = await build_channel_health(session)
            out = _to_out(counts, signals)
    except sa_exc.SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="database unavailable",
        ) from None
    return out
