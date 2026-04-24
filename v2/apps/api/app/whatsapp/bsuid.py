"""Business-Scoped User ID (BSUID) - Meta WhatsApp Cloud API.

Formato (exemplos oficiais): ``US.13491208655302741918`` - prefixo ISO 3166-1
alpha-2 em maiusculas + ``.`` + identificador numerico (4-40 digitos; ajustar
se a Meta alargar formatos).

``normalize_bsuid`` faz strip e passa o prefixo de 2 letras para maiusculas.

Refs: https://developers.facebook.com/docs/whatsapp/business-scoped-user-ids/
"""

from __future__ import annotations

import re

# Regiao 2 letras + ponto + digitos (suffixo variavel; alargar max se necessario).
_BSUID_PATTERN = re.compile(r"^[A-Z]{2}\.[0-9]{4,40}$")


def normalize_bsuid(raw: str | None) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raw = str(raw)
    s = raw.strip()
    if not s:
        return None
    if "." in s:
        prefix, suffix = s.split(".", 1)
        prefix = prefix.strip().upper()
        suffix = suffix.strip()
        if len(prefix) == 2 and suffix:
            return f"{prefix}.{suffix}"
    return s


def is_valid_bsuid(raw: str | None) -> bool:
    """True se ``raw`` segue o padrao BSUID esperado (validacao sintatica)."""
    n = normalize_bsuid(raw)
    if not n:
        return False
    return bool(_BSUID_PATTERN.fullmatch(n))
