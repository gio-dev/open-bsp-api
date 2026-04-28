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

# Etiquetas na inbox (Story 4.2): mesmo perfil que envia mensagens.
INBOX_TAG_ROLES: frozenset[str] = MESSAGE_SEND_ROLES
