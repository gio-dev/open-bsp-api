"""Motor rule-based minimo apos ingresso WhatsApp (Story 5.5, FR26).

Grafos ciclo-free: BFS a partir do trigger. Limite de passos para prevenir loops
futuros (pre-mortem CS). Idempotencia de mensagens: chave
``engine:{source_id}:{node_id}`` em `outbound_whatsapp_messages` (NFR-INT-02).
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contacts.outbound_prefs import outbound_preference_violation
from app.core.config import Settings, get_settings
from app.db.models_flows import TenantFlowPublishActivation
from app.db.models_outbound import OutboundWhatsappMessage
from app.db.models_waba import WabaPhoneNumber
from app.inbox.handoff_sync import upsert_handoff_from_engine
from app.inbox.sync import derived_conversation_id
from app.inbox.tag_sync import append_conversation_tag_by_name
from app.whatsapp.meta_send import normalize_whatsapp_to

log = logging.getLogger(__name__)

MAX_ENGINE_STEPS = 48


def parse_flow_engine_environments(settings: Settings) -> frozenset[str]:
    raw = settings.flow_engine_environments or ""
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    return frozenset(parts)


def _extract_message_text(message: dict[str, Any]) -> str:
    if message.get("type") == "text":
        t = message.get("text")
        if isinstance(t, dict) and isinstance(t.get("body"), str):
            return t["body"]
    return ""


def _fixture_from_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": str(message.get("type") or "unknown"),
        "body": _extract_message_text(message),
    }


async def _resolve_runtime_environment(
    session: AsyncSession,
    tenant_id: UUID,
    phone_number_id: str | None,
) -> str | None:
    """Resolve `environment` da linha WABA. None se nao for seguro (sem phone/id)."""
    if not phone_number_id:
        log.warning(
            "flow_engine: phone_number_id ausente em metadata; motor nao corre "
            "(evita aplicar regra do ambiente errado)",
            extra={"tenant_id": str(tenant_id)},
        )
        return None
    wpn = await session.scalar(
        select(WabaPhoneNumber).where(
            WabaPhoneNumber.tenant_id == tenant_id,
            WabaPhoneNumber.phone_number_id == phone_number_id,
        ),
    )
    if wpn is None:
        log.warning(
            "flow_engine: waba phone nao encontrado; motor nao corre",
            extra={
                "tenant_id": str(tenant_id),
                "phone_number_id": phone_number_id,
            },
        )
        return None
    return str(wpn.environment)


async def _load_latest_published_definition(
    session: AsyncSession,
    tenant_id: UUID,
    environment: str,
) -> dict[str, Any] | None:
    """Ultima activacao publicada para (tenant, environment).

    Semantics: um grafo activo por par (tenant, environment) ? a linha com
    `activated_at` mais recente vence (ultimo publish material na 5.3).
    """
    stmt = (
        select(TenantFlowPublishActivation)
        .where(
            TenantFlowPublishActivation.tenant_id == tenant_id,
            TenantFlowPublishActivation.environment == environment,
        )
        .order_by(TenantFlowPublishActivation.activated_at.desc())
        .limit(1)
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    if row is None:
        return None
    return dict(row.definition_snapshot or {})


async def _resolve_sender_waba_phone(
    session: AsyncSession,
    tenant_id: UUID,
    environment: str,
    phone_number_id: str | None,
) -> WabaPhoneNumber | None:
    filters = [
        WabaPhoneNumber.tenant_id == tenant_id,
        WabaPhoneNumber.environment == environment,
        WabaPhoneNumber.status == "active",
    ]
    if phone_number_id:
        filters.append(WabaPhoneNumber.phone_number_id == phone_number_id)
    stmt = (
        select(WabaPhoneNumber)
        .where(*filters)
        .order_by(WabaPhoneNumber.created_at)
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def _queue_text_outbound(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    environment: str,
    phone_number_id: str | None,
    contact_wa_id: str,
    text: str,
    source_id: str,
    node_id: str,
) -> UUID | None:
    idem_key = f"engine:{source_id}:{node_id}"[:128]
    dup = await session.scalar(
        select(OutboundWhatsappMessage).where(
            OutboundWhatsappMessage.tenant_id == tenant_id,
            OutboundWhatsappMessage.idempotency_key == idem_key,
        ),
    )
    if dup is not None:
        return None

    try:
        to_digits = normalize_whatsapp_to(contact_wa_id)
    except ValueError:
        try:
            to_digits = normalize_whatsapp_to("+" + contact_wa_id)
        except ValueError:
            log.warning(
                "flow_engine_send_text_bad_recipient",
                extra={
                    "tenant_id": str(tenant_id),
                    "contact_wa_id": contact_wa_id,
                },
            )
            return None

    violation = await outbound_preference_violation(
        session,
        tenant_id,
        contact_key_digits=to_digits,
        preference_kind="transactional",
    )
    if violation is not None:
        log.warning(
            "flow_engine_outbound_blocked_by_preferences",
            extra={
                "tenant_id": str(tenant_id),
                "to_recipient": to_digits,
                "violation": violation,
            },
        )
        return None

    waba = await _resolve_sender_waba_phone(
        session,
        tenant_id,
        environment,
        phone_number_id,
    )
    if waba is None:
        log.warning(
            "flow_engine_send_text_no_sender",
            extra={
                "tenant_id": str(tenant_id),
                "environment": environment,
            },
        )
        return None

    row = OutboundWhatsappMessage(
        tenant_id=tenant_id,
        waba_phone_id=waba.id,
        to_recipient=to_digits,
        message_type="text",
        payload={"text": {"body": text[:4096]}},
        status="queued",
        idempotency_key=idem_key,
    )
    session.add(row)
    await session.flush()
    return row.id


async def run_flow_engine_for_inbound_message(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    request_id: str,
    waba_id: str,
    source_id: str,
    contact_wa_id: str | None,
    phone_number_id: str | None,
    message: dict[str, Any],
) -> list[tuple[UUID, UUID]]:
    """Executa publicacao mais recente para o ambiente da linha WABA.

    Devolve lista de (message_id, tenant_id) para `deliver_outbound_message` apos
    commit da transaccao do webhook.
    """
    settings = get_settings()
    if not settings.flow_engine_enabled:
        return []
    if not contact_wa_id:
        return []

    env_allowed = parse_flow_engine_environments(settings)
    runtime_env = await _resolve_runtime_environment(
        session,
        tenant_id,
        phone_number_id,
    )
    if runtime_env is None:
        return []
    if runtime_env.lower() not in env_allowed:
        log.debug(
            "flow_engine_skipped_env",
            extra={
                "request_id": request_id,
                "runtime_env": runtime_env,
                "allowed": sorted(env_allowed),
            },
        )
        return []

    definition = await _load_latest_published_definition(
        session,
        tenant_id,
        runtime_env,
    )
    if not definition:
        log.debug(
            "flow_engine_no_published_flow",
            extra={
                "request_id": request_id,
                "tenant_id": str(tenant_id),
                "environment": runtime_env,
            },
        )
        return []

    fixture = _fixture_from_message(message)
    log.debug(
        "flow_engine_start",
        extra={
            "request_id": request_id,
            "fixture_keys": list(fixture.keys()),
            "tenant_id": str(tenant_id),
            "environment": runtime_env,
        },
    )

    nodes_raw = definition.get("nodes") or []
    edges_raw = definition.get("edges") or []
    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes_raw:
        if isinstance(n, dict) and "id" in n:
            by_id[str(n["id"])] = n
    adj: dict[str, list[str]] = {}
    for e in edges_raw:
        if not isinstance(e, dict):
            continue
        src, tgt = str(e.get("source", "")), str(e.get("target", ""))
        if not src or not tgt:
            continue
        adj.setdefault(src, []).append(tgt)

    triggers = [nid for nid, n in by_id.items() if str(n.get("kind")) == "trigger"]
    if len(triggers) != 1:
        log.warning(
            "flow_engine_invalid_graph",
            extra={"request_id": request_id, "triggers": len(triggers)},
        )
        return []

    start = triggers[0]
    out_deliver: list[tuple[UUID, UUID]] = []
    steps = 0
    q: deque[str] = deque([start])
    seen: set[str] = set()

    conv_id = derived_conversation_id(tenant_id, waba_id, contact_wa_id)

    while q and steps < MAX_ENGINE_STEPS:
        steps += 1
        cur = q.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        if cur not in by_id:
            log.warning(
                "flow_engine_missing_node",
                extra={"request_id": request_id, "node_id": cur},
            )
            break
        node = by_id[cur]
        kind = str(node.get("kind") or "?")
        if kind == "trigger":
            pass
        elif kind == "action":
            ax = str(node.get("action_type") or "").strip().lower()
            nid = str(node.get("id") or cur)
            try:
                if ax == "send_text":
                    body = str(node.get("text_body") or "").strip()
                    if not body:
                        raise ValueError("text_body vazio")
                    oid = await _queue_text_outbound(
                        session,
                        tenant_id=tenant_id,
                        environment=runtime_env,
                        phone_number_id=phone_number_id,
                        contact_wa_id=contact_wa_id,
                        text=body,
                        source_id=source_id,
                        node_id=nid,
                    )
                    if oid is not None:
                        out_deliver.append((oid, tenant_id))
                elif ax == "apply_tag":
                    tname = str(node.get("tag_name") or "").strip()
                    if not tname:
                        raise ValueError("tag_name vazio")
                    await append_conversation_tag_by_name(
                        session,
                        tenant_id=tenant_id,
                        conversation_id=conv_id,
                        tag_name=tname,
                    )
                elif ax == "handoff":
                    intent = str(node.get("handoff_intent") or "").strip() or None
                    await upsert_handoff_from_engine(
                        session,
                        tenant_id=tenant_id,
                        conversation_id=conv_id,
                        handoff_state="queued",
                        intent_summary=intent,
                        bot_last_output=f"engine:{request_id}",
                        queue_id=None,
                    )
                elif ax:
                    log.warning(
                        "flow_engine_unknown_action_type",
                        extra={
                            "request_id": request_id,
                            "action_type": ax,
                            "node_id": nid,
                        },
                    )
            except Exception:
                log.exception(
                    "flow_engine_action_failed",
                    extra={
                        "request_id": request_id,
                        "node_id": nid,
                        "action_type": ax or "-",
                        "tenant_id": str(tenant_id),
                    },
                )
                break
        for nxt in adj.get(cur, ()):
            if nxt not in seen:
                q.append(nxt)

    if steps >= MAX_ENGINE_STEPS:
        log.warning(
            "flow_engine_step_cap",
            extra={"request_id": request_id, "cap": MAX_ENGINE_STEPS},
        )

    return out_deliver
