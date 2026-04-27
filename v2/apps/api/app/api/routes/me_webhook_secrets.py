"""Segredo de verificacao GET webhook Meta: rotacao e listagem (Story 2.4)."""

from __future__ import annotations

import os
import threading
import time
import uuid
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models import AuditEvent, WebhookVerifySecret
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_api_key_manager_context
from app.whatsapp.webhook_verify_db import (
    rotate_webhook_verify_secret,
    row_status,
)

router = APIRouter(tags=["webhook-secrets"])

_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    429: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

# Em producao (sem AUTH_DEV_STUB): minimo 2s entre rotacoes por tenant (NFR-SEC).
_rotate_last: dict[UUID, float] = {}
_rotate_lock = threading.Lock()

_MIN_S_BETWEEN_ROTATES = 2.0


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _throttle_webhook_rotate(tenant_id: UUID) -> None:
    if get_settings().auth_dev_stub or os.environ.get(
        "OPENBSP_SKIP_WEBHOOK_ROTATE_THROTTLE"
    ) == "1":
        return
    with _rotate_lock:
        t = time.time()
        last = _rotate_last.get(tenant_id, 0.0)
        if t - last < _MIN_S_BETWEEN_ROTATES:
            raise HTTPException(
                status_code=429,
                detail="webhook secret rotation rate limited; retry in a few seconds",
            )
        _rotate_last[tenant_id] = t


class WebhookSecretListItem(BaseModel):
    id: UUID
    created_at: datetime
    invalid_after: datetime | None
    status: str


class WebhookSecretListResponse(BaseModel):
    items: list[WebhookSecretListItem]


class WebhookSecretRotateBody(BaseModel):
    coexistence_seconds: int = Field(
        default=24 * 3600,
        ge=300,
        le=30 * 24 * 3600,
    )


class WebhookSecretRotateResponse(BaseModel):
    verify_token: str
    """Mostrado uma vez; configurar no Meta e guardar com seguranca."""
    previous_token_invalid_after: datetime | None
    """Apos este instante o segredo anterior deixa de ser aceite no GET hub."""


@router.get(
    "/me/webhook-secrets",
    response_model=WebhookSecretListResponse,
    responses=_RESPONSES,
)
async def list_webhook_secrets(
    ctx: Annotated[TenantUserContext, Depends(console_api_key_manager_context)],
) -> WebhookSecretListResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    now = _now_utc()
    async with tenant_session(ctx.tenant_id) as session:
        q = (
            select(WebhookVerifySecret)
            .where(WebhookVerifySecret.tenant_id == ctx.tenant_id)
            .order_by(WebhookVerifySecret.created_at.desc())
        )
        res = await session.execute(q)
        rows = res.scalars().all()

    items = [
        WebhookSecretListItem(
            id=r.id,
            created_at=r.created_at,
            invalid_after=r.invalid_after,
            status=row_status(r, now),
        )
        for r in rows
    ]
    return WebhookSecretListResponse(items=items)


@router.post(
    "/me/webhook-secrets/rotate",
    response_model=WebhookSecretRotateResponse,
    status_code=201,
    responses={201: {"model": WebhookSecretRotateResponse}, **_RESPONSES},
)
async def rotate_webhook_secrets(
    body: WebhookSecretRotateBody,
    ctx: Annotated[TenantUserContext, Depends(console_api_key_manager_context)],
) -> WebhookSecretRotateResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    _throttle_webhook_rotate(ctx.tenant_id)

    async with tenant_session(ctx.tenant_id) as session:
        new_plain, prev_end, new_id = await rotate_webhook_verify_secret(
            session,
            ctx.tenant_id,
            body.coexistence_seconds,
        )
        session.add(
            AuditEvent(
                id=uuid.uuid4(),
                tenant_id=ctx.tenant_id,
                actor_user_id=ctx.actor_user_id,
                resource_type="webhook_verify_secret",
                summary=f"rotated webhook verify secret new_id={new_id}",
            )
        )

    return WebhookSecretRotateResponse(
        verify_token=new_plain,
        previous_token_invalid_after=prev_end,
    )
