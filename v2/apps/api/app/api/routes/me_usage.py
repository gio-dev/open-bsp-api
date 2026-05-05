"""GET /v1/me/usage/summary (Story 8.1 FR41)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

import sqlalchemy.exc as sa_exc
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models_usage import USAGE_METRIC_KEYS_KNOWN
from app.db.session import tenant_session
from app.services.usage_metering import (
    default_usage_period_utc,
    sum_usage_by_metric,
)
from app.tenancy.deps import TenantUserContext, console_org_admin_context

router = APIRouter(tags=["usage"])

_RESPONSES = {
    200: {},
    400: {"model": CanonicalErrorResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_MAX_RANGE_DAYS = 366


class UsageMetricTotal(BaseModel):
    """Contagem agregada no periodo (somente metricas conhecidas no contrato MVP)."""

    model_config = ConfigDict(extra="forbid")

    metric_key: str = Field(
        description=(
            "Chave estavel: inbound_messages (nova mensagem webhook); "
            "outbound_messages_accepted (envio aceite Meta/Graph)."
        ),
    )
    count: int = Field(ge=0)


class UsageSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period_start: date
    period_end: date
    metrics: list[UsageMetricTotal]


@router.get(
    "/me/usage/summary",
    response_model=UsageSummaryResponse,
    summary="Resumo de uso por tenant (metering MVP)",
    description=(
        "Agregacao diaria UTC (FR41). Sem PII; totais por metrica no intervalo. "
        "Predefinicao: ultimos 30 dias (inclusive)."
    ),
    responses=_RESPONSES,
)
async def get_usage_summary(
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
    since: Annotated[
        date | None,
        Query(description="Inicio do intervalo (UTC date); omissao = fim - 29d"),
    ] = None,
    until: Annotated[
        date | None,
        Query(description="Fim do intervalo (UTC date); omissao = hoje UTC"),
    ] = None,
) -> UsageSummaryResponse:
    if not get_settings().database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    d_end = until or default_usage_period_utc()[1]
    d_start = since or (d_end - timedelta(days=29))
    if d_start > d_end:
        raise HTTPException(
            status_code=400,
            detail="since must be on or before until",
        )
    if (d_end - d_start).days + 1 > _MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=400,
            detail=f"range must not exceed {_MAX_RANGE_DAYS} days",
        )
    try:
        async with tenant_session(ctx.tenant_id) as session:
            by_metric = await sum_usage_by_metric(
                session,
                tenant_id=ctx.tenant_id,
                period_start=d_start,
                period_end=d_end,
            )
    except sa_exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=503,
            detail="servico de dados indisponivel",
        ) from e

    metrics = [
        UsageMetricTotal(metric_key=k, count=int(by_metric.get(k, 0)))
        for k in sorted(USAGE_METRIC_KEYS_KNOWN)
    ]
    return UsageSummaryResponse(
        period_start=d_start,
        period_end=d_end,
        metrics=metrics,
    )
