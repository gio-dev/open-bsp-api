"""Identidade de utilizador inbound: BSUID (preferido) vs wa_id / E.164."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.whatsapp.bsuid import is_valid_bsuid, normalize_bsuid


def _bsuid_candidate(raw: Any) -> str | None:
    """Normaliza e devolve BSUID apenas se passar validacao sintatica."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        raw = str(raw)
    n = normalize_bsuid(raw)
    if not n:
        return None
    return n if is_valid_bsuid(n) else None


@dataclass(frozen=True, slots=True)
class InboundUserIdentity:
    """Referencia a um utilizador WhatsApp num webhook (pos-BSUID).

    Meta pode enviar ``from_user_id`` / ``contacts[].user_id`` (BSUID) com ou sem
    ``from`` / ``wa_id``. Usar :meth:`stable_storage_key` como chave logica de contacto.
    """

    bsuid: str | None
    wa_id: str | None
    display_name: str | None = None

    def stable_storage_key(self) -> str | None:
        """Chave preferida: BSUID quando existir; caso contrario wa_id (telefone)."""
        if self.bsuid:
            return self.bsuid.strip()
        if self.wa_id:
            return self.wa_id.strip()
        return None


def resolve_inbound_identity(
    value: dict[str, Any],
    message: dict[str, Any],
) -> InboundUserIdentity | None:
    """Deriva identidade a partir de ``value`` (contacts) e ``message``.

    Campos Meta (BSUID): ``contacts[].user_id``, ``messages[].from_user_id``.
    Campos legados: ``contacts[].wa_id``, ``messages[].from``.
    ``user_id`` / ``from_user_id`` invalidos para BSUID ignoram-se (fallback wa_id).
    """
    msg_from = message.get("from")
    if isinstance(msg_from, str):
        msg_from = msg_from.strip() or None
    else:
        msg_from = None

    msg_from_user_id = _bsuid_candidate(message.get("from_user_id"))

    display_name: str | None = None
    matched_bsuid: str | None = None
    matched_wa: str | None = None

    contacts = value.get("contacts")
    if isinstance(contacts, list):
        for c in contacts:
            if not isinstance(c, dict):
                continue
            cid = _bsuid_candidate(c.get("user_id"))
            cwa = c.get("wa_id")
            if isinstance(cwa, str):
                cwa = cwa.strip() or None
            else:
                cwa = None
            prof = c.get("profile")
            name: str | None = None
            if isinstance(prof, dict):
                n = prof.get("name")
                if isinstance(n, str) and n.strip():
                    name = n.strip()
            matches = (msg_from_user_id and cid == msg_from_user_id) or (
                msg_from and cwa == msg_from
            )
            if matches:
                matched_bsuid = cid or matched_bsuid
                matched_wa = cwa or matched_wa
                display_name = name
                break

    bsuid = msg_from_user_id or matched_bsuid
    wa_id = msg_from or matched_wa

    if not bsuid and not wa_id:
        return None

    return InboundUserIdentity(bsuid=bsuid, wa_id=wa_id, display_name=display_name)
