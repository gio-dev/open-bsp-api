"""Leitura de segredos de verificacao GET hub (Meta) por tenant. Story 2.4."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WebhookVerifySecret


def _hash_verify_token(plain: str) -> str:
    """SHA-256 com salt (GET hub rapido; nao usar para API keys)."""
    salt = os.urandom(16)
    dig = hashlib.sha256(salt + plain.encode("utf-8")).digest()
    blob = base64.urlsafe_b64encode(salt + dig).decode("ascii")
    return f"wv1${blob}"


def _verify_verify_token(plain: str, stored: str) -> bool:
    if not stored.startswith("wv1$"):
        return False
    try:
        raw = base64.urlsafe_b64decode(stored[4:].encode("ascii"))
    except (ValueError, OSError):
        return False
    if len(raw) < 16 + 32:
        return False
    salt, dig = raw[:16], raw[16:]
    cand = hashlib.sha256(salt + plain.encode("utf-8")).digest()
    return hmac.compare_digest(cand, dig)


def _now_utc() -> datetime:
    return datetime.now(UTC)


def generate_webhook_verify_token() -> str:
    """Token imprimivel para o utilizador colar no Meta (sem prefixo fixo)."""
    return "wvt_" + secrets.token_urlsafe(32)


async def match_verify_token(
    session: AsyncSession, tenant_id: UUID, plain: str
) -> bool:
    """True se o token corresponde a uma versao ainda valida (coexistencia)."""
    q = (
        select(WebhookVerifySecret)
        .where(WebhookVerifySecret.tenant_id == tenant_id)
        .order_by(WebhookVerifySecret.created_at.desc())
        .limit(64)
    )
    res = await session.execute(q)
    rows = res.scalars().all()
    now = _now_utc()
    for row in rows:
        if row.invalid_after is not None and row.invalid_after <= now:
            continue
        if _verify_verify_token(plain, row.secret_hash):
            return True
    return False


async def rotate_webhook_verify_secret(
    session: AsyncSession,
    tenant_id: UUID,
    coexistence_seconds: int,
) -> tuple[str, datetime | None, uuid.UUID]:
    """Gira o segredo: expira o actual (se existir) e cria um novo."""
    now = _now_utc()
    co_until = now + timedelta(seconds=coexistence_seconds)
    current = await session.scalar(
        select(WebhookVerifySecret)
        .where(
            WebhookVerifySecret.tenant_id == tenant_id,
            WebhookVerifySecret.invalid_after.is_(None),
        )
        .with_for_update()
    )
    prev_end: datetime | None = None
    if current is not None:
        current.invalid_after = co_until
        session.add(current)
        prev_end = co_until
    new_plain = generate_webhook_verify_token()
    new_id = uuid.uuid4()
    session.add(
        WebhookVerifySecret(
            id=new_id,
            tenant_id=tenant_id,
            secret_hash=_hash_verify_token(new_plain),
            invalid_after=None,
        )
    )
    return new_plain, prev_end, new_id


def row_status(row: WebhookVerifySecret, now: datetime) -> str:
    if row.invalid_after is None:
        return "active"
    if row.invalid_after > now:
        return "coexisting"
    return "expired"
