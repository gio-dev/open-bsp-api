"""Motor rule-based minimo apos ingresso WhatsApp (Story 5.5, FR26).

Grafos ciclo-free: BFS a partir do trigger. Limite de passos para prevenir loops
futuros (pre-mortem CS). Idempotencia de mensagens: chave
``engine:{source_id}:{node_id}`` em `outbound_whatsapp_messages` (NFR-INT-02).
"""

from __future__ import annotations

import logging
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contacts.outbound_prefs import outbound_preference_violation
from app.core.config import Settings, get_settings
from app.db.models import AuditEvent, TenantContactPreference
from app.db.models_flows import TenantFlowPublishActivation
from app.db.models_outbound import OutboundWhatsappMessage
from app.db.models_waba import WabaPhoneNumber
from app.inbox.handoff_sync import upsert_handoff_from_engine
from app.inbox.sync import derived_conversation_id
from app.inbox.tag_sync import append_conversation_tag_by_name
from app.services.flow_validation import coerce_flow_definition
from app.whatsapp.meta_send import normalize_whatsapp_to

log = logging.getLogger(__name__)

MAX_ENGINE_STEPS = 48

_DEFAULT_DISCLOSURE_SLUG = "baseline-v1"


def _audit_flow_bool(b: bool) -> str:
    return "true" if b else "false"


def _contact_key_digits(contact_wa_id: str) -> str | None:
    try:
        return normalize_whatsapp_to(contact_wa_id)
    except ValueError:
        try:
            return normalize_whatsapp_to("+" + contact_wa_id)
        except ValueError:
            return None


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
    preference_kind: str,
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

    to_digits = _contact_key_digits(contact_wa_id)
    if to_digits is None:
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
        preference_kind=preference_kind,
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


def _parse_send_text_preference_kind(
    node: dict[str, Any],
    *,
    request_id: str,
    node_id: str,
) -> str:
    raw = str(node.get("preference_kind") or "").strip().lower()
    if raw in ("", "transactional"):
        return "transactional"
    if raw in ("none", "marketing"):
        return raw
    if raw:
        log.warning(
            "flow_engine_unknown_preference_kind",
            extra={
                "request_id": request_id,
                "node_id": node_id,
                "preference_kind": raw,
            },
        )
    return "transactional"


async def _apply_update_preferences_action(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    contact_wa_id: str,
    request_id: str,
    node_id: str,
    marketing_opt_in: bool | None,
    transactional_allowed: bool | None,
    disclosure_copy_slug: str | None,
) -> None:
    """Persiste opt-in / transacional / versao de copy (Story 6.3 + fluxos 5.x)."""
    to_digits = _contact_key_digits(contact_wa_id)
    if to_digits is None:
        log.warning(
            "flow_engine_update_prefs_bad_recipient",
            extra={
                "tenant_id": str(tenant_id),
                "contact_wa_id": contact_wa_id,
                "request_id": request_id,
                "node_id": node_id,
            },
        )
        session.add(
            AuditEvent(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                actor_user_id=None,
                resource_type="flow_engine",
                summary=(
                    f"update_prefs_skipped_bad_recipient:{request_id}:{node_id}:"
                    f"{(contact_wa_id or '')[:80]!r}"
                )[:1024],
            ),
        )
        await session.flush()
        return

    now = datetime.now(timezone.utc)
    changed_keys: list[str] = []

    row = await session.scalar(
        select(TenantContactPreference).where(
            TenantContactPreference.tenant_id == tenant_id,
            TenantContactPreference.contact_id == to_digits,
        ),
    )

    slug_in = (
        disclosure_copy_slug.strip()[:128]
        if disclosure_copy_slug and disclosure_copy_slug.strip()
        else None
    )

    if row is None:
        old_m, old_t, old_s = False, True, _DEFAULT_DISCLOSURE_SLUG
        mk = marketing_opt_in if marketing_opt_in is not None else False
        tk = transactional_allowed if transactional_allowed is not None else True
        dc = slug_in if slug_in is not None else _DEFAULT_DISCLOSURE_SLUG
        row = TenantContactPreference(
            tenant_id=tenant_id,
            contact_id=to_digits,
            marketing_opt_in=mk,
            transactional_allowed=tk,
            disclosure_copy_slug=dc,
            marketing_consent_recorded_at=now if mk else None,
            updated_at=now,
        )
        session.add(row)
        if marketing_opt_in is not None:
            changed_keys.append("marketing_opt_in")
        if transactional_allowed is not None:
            changed_keys.append("transactional_allowed")
        if slug_in is not None:
            changed_keys.append("disclosure_copy_slug")
    else:
        old_m = row.marketing_opt_in
        old_t = row.transactional_allowed
        old_s = row.disclosure_copy_slug
        if marketing_opt_in is not None and marketing_opt_in != row.marketing_opt_in:
            row.marketing_opt_in = marketing_opt_in
            changed_keys.append("marketing_opt_in")
        if (
            transactional_allowed is not None
            and transactional_allowed != row.transactional_allowed
        ):
            row.transactional_allowed = transactional_allowed
            changed_keys.append("transactional_allowed")
        if slug_in is not None and slug_in != row.disclosure_copy_slug:
            row.disclosure_copy_slug = slug_in
            changed_keys.append("disclosure_copy_slug")
        if changed_keys:
            row.updated_at = now
        if row.marketing_opt_in and not old_m:
            row.marketing_consent_recorded_at = now

    if changed_keys:
        new_m, new_t, new_s = (
            row.marketing_opt_in,
            row.transactional_allowed,
            row.disclosure_copy_slug,
        )
        diff: list[str] = []
        if new_m != old_m:
            diff.append(f"m:{_audit_flow_bool(old_m)}->{_audit_flow_bool(new_m)}")
        if new_t != old_t:
            diff.append(f"t:{_audit_flow_bool(old_t)}->{_audit_flow_bool(new_t)}")
        if new_s != old_s:
            diff.append(f"slug:{old_s[:48]}->{new_s[:48]}")
        session.add(
            AuditEvent(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                actor_user_id=None,
                resource_type="contact_preferences",
                summary=(
                    f"flow_engine:{request_id}:{node_id}:{to_digits}:{'|'.join(diff)}"
                )[:1024],
            ),
        )
    await session.flush()


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

    definition_raw = await _load_latest_published_definition(
        session,
        tenant_id,
        runtime_env,
    )
    if not definition_raw:
        log.debug(
            "flow_engine_no_published_flow",
            extra={
                "request_id": request_id,
                "tenant_id": str(tenant_id),
                "environment": runtime_env,
            },
        )
        return []

    graph_model, coerce_err = coerce_flow_definition(dict(definition_raw))
    if coerce_err or graph_model is None:
        log.warning(
            "flow_engine_publish_snapshot_coerce_failed",
            extra={
                "request_id": request_id,
                "tenant_id": str(tenant_id),
                "environment": runtime_env,
                "errors": coerce_err[:8],
            },
        )
        return []

    definition = graph_model.model_dump(mode="python")

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
                    pk = _parse_send_text_preference_kind(
                        node,
                        request_id=request_id,
                        node_id=nid,
                    )
                    oid = await _queue_text_outbound(
                        session,
                        tenant_id=tenant_id,
                        environment=runtime_env,
                        phone_number_id=phone_number_id,
                        contact_wa_id=contact_wa_id,
                        text=body,
                        source_id=source_id,
                        node_id=nid,
                        preference_kind=pk,
                    )
                    if oid is not None:
                        out_deliver.append((oid, tenant_id))
                elif ax == "update_preferences":
                    m_raw = node.get("marketing_opt_in")
                    m_set = m_raw if isinstance(m_raw, bool) else None
                    t_raw = node.get("transactional_allowed")
                    t_set = t_raw if isinstance(t_raw, bool) else None
                    d_raw = node.get("disclosure_copy_slug")
                    d_slug: str | None = (
                        str(d_raw).strip()[:128]
                        if isinstance(d_raw, str) and str(d_raw).strip()
                        else None
                    )
                    await _apply_update_preferences_action(
                        session,
                        tenant_id=tenant_id,
                        contact_wa_id=contact_wa_id,
                        request_id=request_id,
                        node_id=nid,
                        marketing_opt_in=m_set,
                        transactional_allowed=t_set,
                        disclosure_copy_slug=d_slug,
                    )
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
