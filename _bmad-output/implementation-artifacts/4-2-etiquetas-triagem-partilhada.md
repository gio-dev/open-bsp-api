---
story_key: 4-2-etiquetas-triagem-partilhada
epic: epic-4
status: ready-for-dev
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

- [ ] Tabelas `tags` + associacao conversa-tag com `tenant_id`; RLS.
- [ ] Endpoints listar tags, aplicar a conversa; validar permissoes operador.
- [ ] Admin-web: chips/tags na inbox; optimistic UI com rollback em erro (UX-DR4).
- [ ] Testes; ATDD `test_epic4_story42_etiquetas_atdd.py`.

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

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 4.2

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic4_story42_etiquetas_atdd.py`.
