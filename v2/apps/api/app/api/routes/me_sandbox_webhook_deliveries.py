"""Historico de entregas de ingresso webhook (Story 7.3 FR39).

Dados tenant-scoped; persistencia com RLS na tabela correspondente.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

import sqlalchemy.exc as sa_exc
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import desc, select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models_sandbox_webhook_deliveries import TenantSandboxWebhookDelivery
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_org_admin_context

router = APIRouter(tags=["sandbox-webhooks"])

_RESPONSES_LIST = {
    200: {},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class SandboxWebhookDeliveryItem(BaseModel):
    """Resumo por POST processado neste tenant (subconjunto do pedido Meta)."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    request_id: str = Field(
        description="Correlation id na resposta de ingresso (UX-DR6 / CDA).",
    )
    status: str
    enqueued: int
    deduplicated: int
    skipped: int
    created_at: datetime


class SandboxWebhookDeliveriesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[SandboxWebhookDeliveryItem]


_LIST_DESC = (
    "Lista MVP persistida quando o ingresso Meta e aceite para este tenant "
    "(request_id e contagens enqueue/dedupe/skip isoladas por tenant)."
)


@router.get(
    "/me/sandbox/webhook-deliveries",
    response_model=SandboxWebhookDeliveriesResponse,
    summary="Historico ingresso webhook (tenant sandbox scope)",
    description=_LIST_DESC,
    responses=_RESPONSES_LIST,
)
async def list_sandbox_webhook_deliveries(
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximo de entradas mais recentes"),
    ] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SandboxWebhookDeliveriesResponse:
    if not get_settings().database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    try:
        async with tenant_session(ctx.tenant_id) as session:
            stmt = (
                select(TenantSandboxWebhookDelivery)
                .order_by(desc(TenantSandboxWebhookDelivery.created_at))
                .limit(limit)
                .offset(offset)
            )
            rows = (await session.execute(stmt)).scalars().all()
    except sa_exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=503,
            detail="servico de dados indisponivel",
        ) from e

    items = [
        SandboxWebhookDeliveryItem(
            id=r.id,
            request_id=r.request_id,
            status=r.status,
            enqueued=r.enqueued,
            deduplicated=r.deduplicated,
            skipped=r.skipped,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return SandboxWebhookDeliveriesResponse(items=items)
