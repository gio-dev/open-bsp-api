"""Papeis tenant (Story 2.2) ? slugs estaveis na API."""

# Minimo PRD: admin, operador, atendente, leitura, financas, suporte
VALID_TENANT_ROLES: frozenset[str] = frozenset(
    {
        "org_admin",
        "operator",
        "agent",
        "viewer",
        "finance",
        "support",
    }
)

ORG_WRITE_ROLES: frozenset[str] = frozenset({"org_admin"})

WABA_WRITE_ROLES: frozenset[str] = frozenset({"org_admin"})

API_KEY_MANAGE_ROLES: frozenset[str] = frozenset({"org_admin", "operator"})

MESSAGE_SEND_ROLES: frozenset[str] = frozenset({"org_admin", "operator", "agent"})

# Editor de fluxos (Story 5.1): operador programa regras; admin total.
FLOW_EDITOR_ROLES: frozenset[str] = frozenset({"org_admin", "operator"})

# Publish em runtime (5.3): prod so org_admin; dev/staging admin ou operator.
_PUBLISH_TARGETS_NONPROD: frozenset[str] = frozenset({"development", "staging"})

# Historico material de publish (5.4): listagem e snapshot no GET detalhe; mesmo
# universo que edita rascunhos (limita exposicao a viewer/finance/support).
FLOW_PUBLISH_VERSION_READ_ROLES: frozenset[str] = FLOW_EDITOR_ROLES


def roles_may_publish_flow(
    roles: frozenset[str],
    *,
    environment: str,
) -> bool:
    """Story 5.3: producao so org_admin; dev/staging org_admin ou operator."""
    if environment == "production":
        return "org_admin" in roles
    if environment in _PUBLISH_TARGETS_NONPROD:
        return bool(roles & FLOW_EDITOR_ROLES)
    return False


# Etiquetas na inbox (Story 4.2): mesmo perfil que envia mensagens.
INBOX_TAG_ROLES: frozenset[str] = MESSAGE_SEND_ROLES

# Preferencias LGPD por contacto (Story 6.3): mesmo universo que edita inbox.
CONTACT_PREFERENCE_WRITE_ROLES: frozenset[str] = MESSAGE_SEND_ROLES
