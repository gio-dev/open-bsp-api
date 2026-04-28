"""Chaves de API: emissao, listagem, revogacao com janela (Story 2.3)."""

from __future__ import annotations

import os
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Self
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.api_key_crypto import generate_api_key_material, hash_api_secret
from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models import ApiKey, AuditEvent
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_api_key_manager_context

router = APIRouter(tags=["api-keys"])

_RESPONSES = {
    400: {"model": CanonicalErrorResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    429: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

# NFR-SEC-02: minimo 2s entre POST /me/api-keys por tenant.
_api_key_create_last: dict[UUID, float] = {}
_api_key_create_lock = threading.Lock()
_MIN_S_BETWEEN_API_KEY_CREATES = 2.0


def _throttle_api_key_create(tenant_id: UUID) -> None:
    if (
        get_settings().auth_dev_stub
        or os.environ.get("OPENBSP_SKIP_API_KEY_CREATE_THROTTLE") == "1"
    ):
        return
    with _api_key_create_lock:
        t = time.time()
        last = _api_key_create_last.get(tenant_id, 0.0)
        if t - last < _MIN_S_BETWEEN_API_KEY_CREATES:
            raise HTTPException(
                status_code=429,
                detail="api key issue rate limited; retry in a few seconds",
            )
        _api_key_create_last[tenant_id] = t


def _is_api_key_prefix_uniqueness_error(exc: IntegrityError) -> bool:
    o = exc.orig
    if o is None:
        return "uq_api_keys_tenant_prefix" in str(exc) or "api_keys" in str(exc).lower()
    text = f"{o}".lower()
    return "uq_api_keys_tenant_prefix" in text or (
        "unique" in text and "api_keys" in text
    )


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _api_key_status(row: ApiKey, now: datetime) -> str:
    if row.revoked_at is not None:
        return "revoked"
    if row.expires_at is not None and row.expires_at <= now:
        return "expired"
    if row.expires_at is not None and row.expires_at > now:
        return "scheduled_revocation"
    return "active"


def _row_valid_for_auth(row: ApiKey, now: datetime) -> bool:
    if row.revoked_at is not None:
        return False
    if row.expires_at is not None and row.expires_at <= now:
        return False
    return True


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    replace_key_id: UUID | None = None
    coexistence_seconds: int | None = Field(default=None, ge=60, le=30 * 24 * 3600)

    @model_validator(mode="after")
    def replace_pair(self) -> Self:
        if (self.replace_key_id is None) ^ (self.coexistence_seconds is None):
            raise ValueError(
                "replace_key_id and coexistence_seconds must both be set "
                "or both omitted"
            )
        return self


class ApiKeyCreatedResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    secret: str
    created_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    status: str


class ApiKeyListItem(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    created_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    status: str


class ApiKeyListResponse(BaseModel):
    items: list[ApiKeyListItem]


class ApiKeyRevokeBody(BaseModel):
    schedule_revoke_in_seconds: int | None = Field(
        default=None, ge=60, le=30 * 24 * 3600
    )
    revoke_immediately: bool = False

    @model_validator(mode="after")
    def need_action(self) -> Self:
        if not self.revoke_immediately and self.schedule_revoke_in_seconds is None:
            raise ValueError("provide revoke_immediately or schedule_revoke_in_seconds")
        return self


@router.get(
    "/me/api-keys",
    response_model=ApiKeyListResponse,
    responses=_RESPONSES,
)
async def list_api_keys(
    ctx: Annotated[TenantUserContext, Depends(console_api_key_manager_context)],
) -> ApiKeyListResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    now = _now_utc()
    async with tenant_session(ctx.tenant_id) as session:
        q = (
            select(ApiKey)
            .where(ApiKey.tenant_id == ctx.tenant_id)
            .order_by(ApiKey.created_at.desc())
        )
        res = await session.execute(q)
        rows = res.scalars().all()

    items = [
        ApiKeyListItem(
            id=r.id,
            name=r.name,
            key_prefix=r.key_prefix,
            created_at=r.created_at,
            expires_at=r.expires_at,
            revoked_at=r.revoked_at,
            status=_api_key_status(r, now),
        )
        for r in rows
    ]
    return ApiKeyListResponse(items=items)


@router.post(
    "/me/api-keys",
    response_model=ApiKeyCreatedResponse,
    status_code=201,
    responses={
        201: {"model": ApiKeyCreatedResponse},
        429: {"model": CanonicalErrorResponse},
        **_RESPONSES,
    },
)
async def create_api_key(
    body: ApiKeyCreate,
    ctx: Annotated[TenantUserContext, Depends(console_api_key_manager_context)],
) -> ApiKeyCreatedResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    _throttle_api_key_create(ctx.tenant_id)

    key_prefix, full_secret = generate_api_key_material()
    digest = hash_api_secret(full_secret)
    now = _now_utc()
    new_id = uuid.uuid4()

    try:
        async with tenant_session(ctx.tenant_id) as session:
            if body.replace_key_id is not None and body.coexistence_seconds is not None:
                old = await session.scalar(
                    select(ApiKey).where(
                        ApiKey.tenant_id == ctx.tenant_id,
                        ApiKey.id == body.replace_key_id,
                    )
                )
                if old is None:
                    raise HTTPException(status_code=404, detail="api key not found")
                if not _row_valid_for_auth(old, now):
                    raise HTTPException(
                        status_code=400,
                        detail="cannot schedule coexistence on inactive key",
                    )
                old.expires_at = now + timedelta(seconds=body.coexistence_seconds)
                session.add(old)
                session.add(
                    AuditEvent(
                        id=uuid.uuid4(),
                        tenant_id=ctx.tenant_id,
                        actor_user_id=ctx.actor_user_id,
                        resource_type="api_key",
                        summary=(
                            f"scheduled coexistence expiry key={body.replace_key_id} "
                            f"+{body.coexistence_seconds}s"
                        ),
                    )
                )

            row = ApiKey(
                id=new_id,
                tenant_id=ctx.tenant_id,
                name=body.name.strip(),
                key_prefix=key_prefix,
                secret_hash=digest,
                expires_at=None,
                revoked_at=None,
            )
            session.add(row)
            session.add(
                AuditEvent(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    actor_user_id=ctx.actor_user_id,
                    resource_type="api_key",
                    summary=f"issued name={body.name.strip()!r} prefix={key_prefix!r}",
                )
            )
    except IntegrityError as e:
        if _is_api_key_prefix_uniqueness_error(e):
            raise HTTPException(
                status_code=409,
                detail="api key prefix collision; retry the request",
            ) from e
        raise

    return ApiKeyCreatedResponse(
        id=new_id,
        name=body.name.strip(),
        key_prefix=key_prefix,
        secret=full_secret,
        created_at=now,
        expires_at=None,
        revoked_at=None,
        status="active",
    )


@router.patch(
    "/me/api-keys/{key_id}",
    response_model=ApiKeyListItem,
    responses=_RESPONSES,
)
async def patch_api_key(
    key_id: UUID,
    body: ApiKeyRevokeBody,
    ctx: Annotated[TenantUserContext, Depends(console_api_key_manager_context)],
) -> ApiKeyListItem:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    now = _now_utc()
    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(ApiKey).where(
                ApiKey.tenant_id == ctx.tenant_id,
                ApiKey.id == key_id,
            )
        )
        if row is None:
            raise HTTPException(status_code=404, detail="api key not found")

        if body.revoke_immediately:
            row.revoked_at = now
            row.expires_at = now
            summary = f"revoked immediately key={key_id}"
        else:
            assert body.schedule_revoke_in_seconds is not None
            row.expires_at = now + timedelta(seconds=body.schedule_revoke_in_seconds)
            summary = (
                f"scheduled revocation key={key_id} +{body.schedule_revoke_in_seconds}s"
            )

        session.add(row)
        session.add(
            AuditEvent(
                id=uuid.uuid4(),
                tenant_id=ctx.tenant_id,
                actor_user_id=ctx.actor_user_id,
                resource_type="api_key",
                summary=summary,
            )
        )

    now2 = _now_utc()
    return ApiKeyListItem(
        id=row.id,
        name=row.name,
        key_prefix=row.key_prefix,
        created_at=row.created_at,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
        status=_api_key_status(row, now2),
    )
