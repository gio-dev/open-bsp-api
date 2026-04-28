---
story_key: 4-2-etiquetas-triagem-partilhada
epic: epic-4
status: review
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 4-1-inbox-split-lista-thread
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 4.2 - Etiquetas e triagem partilhada

## Story

**Como** operador,  
**quero** **etiquetar** conversas com **etiquetas** de equipa,  
**para** triar e reportar sem planilha externa (FR18).

## Acceptance Criteria

1. **Dado** conversa, **quando** adiciono ou removo etiquetas, **entao** persistem; outros operadores com acesso veem o mesmo; restricao por **tenant**.
2. Modelo de tags partilhadas no tenant (nao por utilizador isolado sem regra).
3. API documentada (ex. `PATCH /v1/me/conversations/{id}/tags`); OpenAPI atualizado.

**Requisitos:** FR18.

## Tasks / Subtasks

- [x] Tabelas `inbox_tags` + `inbox_conversation_tags` com `tenant_id`; RLS.
- [x] Endpoints listar tags, criar tag, aplicar a conversa; permissoes `INBOX_TAG_ROLES` (org_admin, operator, agent).
- [x] Admin-web: chips/tags na inbox; TanStack Query mutation com optimistic update e rollback em erro.
- [x] Testes integracao; ATDD API e Vitest UI; gate OpenAPI.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Nomes de tag unicos por tenant; slug ou id estavel. |
| **Mary** | FR18; visibilidade partilhada e explicita no AC. |
| **John** | Base para reporting e filas futuras. |
| **Sally** | Feedback imediato ao adicionar/remover tag. |
| **Amelia** | PATCH idempotente onde fizer sentido; 404 conversa de outro tenant. |

## Advanced Elicitation (CS)

- **Pre-mortem:** limite de tags por conversa - politica documentada.
- **Red team:** tag com nome ofensivo em massa - RBAC para criar tags vs aplicar.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | RLS em tags e memberships de conversa. |
| **Amelia** | ATDD: PATCH tags retorna 200/204 apos DS. |
| **Mary** | Consistencia eventual aceitavel se UI refetch apos PATCH. |

### Advanced Elicitation (VS)

- **Socratic:** o que prova partilha? - segundo cliente ve mesma lista apos refresh.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| RLS | Tags e ligacoes sempre `tenant_id`. |
| Regressao | Inbox 4.1 continua a carregar. |

## Dev Notes - requisitos tecnicos

- Depende de **4.1** (conversa endereçavel).

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic4_story42_etiquetas_atdd.py`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-4.md`
- Vitest: `v2/apps/admin-web/src/atdd/epic4-story42-inbox-tags.atdd.test.tsx`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.2

## Dev Agent Record

### Agent Model Used

Composer (DS Story 4.2)

### Completion Notes List

- Migracao `016`: `inbox_tags`, `inbox_conversation_tags`, RLS, grants `app_runtime`.
- API: `GET/POST /v1/me/inbox/tags`, `PATCH /v1/me/conversations/{id}/tags` (replace `tag_ids`, max 20); lista e thread incluem `tags`.
- RBAC: `console_inbox_tag_context` (`INBOX_TAG_ROLES` = mesmos que envio de mensagens).
- Seed CI: tag `atdd-label` ligada a `atdd-conv-1`.
- Correcao: `GET /me/conversations/{id}/messages` tinha decorador `@router.get` em falta (4.1).
- Integracao 4.1: assercao do `display_name` do tenant flexivel (poluicao entre testes na mesma DB).
- Ruff/format: linhas longas corrigidas em varios modulos para CI com ruff 0.15.x.

### File List

- `v2/apps/api/alembic/versions/016_inbox_tags.py`
- `v2/apps/api/alembic/versions/015_inbox_conversations.py` (ruff line wrap)
- `v2/apps/api/app/db/models_inbox.py`
- `v2/apps/api/app/api/routes/me_inbox_tags.py`
- `v2/apps/api/app/api/routes/me_conversations.py`
- `v2/apps/api/app/main.py`
- `v2/apps/api/app/ci_seed.py`
- `v2/apps/api/app/tenancy/deps.py`
- `v2/apps/api/app/tenancy/rbac.py`
- `v2/apps/api/app/inbox/sync.py` (ruff wrap)
- `v2/apps/api/app/api/routes/me_message_templates.py` (ruff wrap)
- `v2/apps/api/app/whatsapp/templates_meta.py` (ruff wrap)
- `v2/apps/api/app/whatsapp/webhook_ingress.py` (ruff format)
- `v2/apps/api/tests/integration/test_story42_inbox_tags.py`
- `v2/apps/api/tests/integration/test_story41_inbox.py`
- `v2/apps/api/tests/atdd/test_epic4_story42_etiquetas_atdd.py`
- `v2/apps/api/tests/policy/test_openapi_gate.py`
- `v2/apps/admin-web/src/features/inbox/InboxPage.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story41-inbox-page.atdd.test.tsx`
- `v2/apps/admin-web/src/atdd/epic4-story42-inbox-tags.atdd.test.tsx`

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story42_etiquetas_atdd.py`.
- 2026-04-28: **[DS]** implementacao API + admin-web + testes; status `review`.
