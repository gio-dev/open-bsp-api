"""Gates outbound envio segundo preferencias (Story 6.3 / FR33).

Choke points que aplicam `preference_kind` (marketing | transactional | none):

- ``POST /v1/me/messages/send`` (consola / integrador) chama
  :func:`gate_outbound_contact_preferences`.
- Motor de fluxos 5.5 (``send_text`` no grafo) enfileira outbound com categoria
  **transacional** via :func:`outbound_preference_violation` antes de criar linha
  na fila. Envios auto sem classificar continuam a **nao** passar por este gate
  (usar ``preference_kind=none`` no POST ou evoluir o motor com nos explicitos).

Outros caminhos (workers, SQL directo) estao fora do contrato ate ficarem
documentados; ver README Epic 6.3.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import TenantContactPreference


async def load_contact_preference_flags(
    session,
    tenant_id: UUID,
    contact_id_digits: str,
) -> tuple[bool, bool]:
    """(marketing_opt_in, transactional_allowed) com defaults implicitos."""
    pref = await session.scalar(
        select(TenantContactPreference).where(
            TenantContactPreference.tenant_id == tenant_id,
            TenantContactPreference.contact_id == contact_id_digits,
        ),
    )
    mk = pref.marketing_opt_in if pref is not None else False
    tk = pref.transactional_allowed if pref is not None else True
    return mk, tk


async def outbound_preference_violation(
    session,
    tenant_id: UUID,
    *,
    contact_key_digits: str,
    preference_kind: str,
) -> str | None:
    """None se envio permitido; senao codigo de detalhe (HTTP 409 ou log)."""
    if preference_kind == "none":
        return None
    if not contact_key_digits.isdigit():
        return "invalid_recipient_for_preference_kind"
    mk, tk = await load_contact_preference_flags(
        session,
        tenant_id,
        contact_key_digits,
    )
    if preference_kind == "marketing" and not mk:
        return "marketing_blocked_by_preferences"
    if preference_kind == "transactional" and not tk:
        return "transactional_blocked_by_preferences"
    return None


async def gate_outbound_contact_preferences(
    session,
    tenant_id: UUID,
    *,
    contact_key_digits: str,
    preference_kind: str,
) -> None:
    violation = await outbound_preference_violation(
        session,
        tenant_id,
        contact_key_digits=contact_key_digits,
        preference_kind=preference_kind,
    )
    if violation == "invalid_recipient_for_preference_kind":
        raise HTTPException(
            status_code=422,
            detail="preference_kind requires digit-only WhatsApp recipient",
        )
    if violation is not None:
        raise HTTPException(status_code=409, detail=violation)
