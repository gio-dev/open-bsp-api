---
story_key: f3-1-orquestrador-n8n-integracao-piloto
epic: epic-f3
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 7-3-sandbox-tenant-scoped
code_location: v2/apps/api, v2/apps/admin-web
---

# Story F3 Orquestrador piloto

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Orquestracao externa tenant-safe.

**Requisitos:** FR28 (gate F3)

## Acceptance Criteria (testaveis)

- ADR seguranca; uma integracao piloto acordada (ex. n8n).

## Tasks / Subtasks

- [ ] Modelo + Alembic com `tenant_id` e RLS onde houver dados.
- [ ] API `/v1/...` + OpenAPI; erros canonicos (story 1.1).
- [ ] Admin-web quando houver UI (Chakra, UX-DR).
- [ ] pytest integracao; ATDD em `v2/apps/api/tests/atdd/test_f3_story_f31_orchestrator_atdd.py`

## Party Mode (CS)

| Agente | Insight |
|--------|---------|
| **Winston** | OpenAPI e RLS; sem segunda forma de erro JSON. |
| **Mary** | Rastrear FR/NFR citados; dependencias no frontmatter. |
| **John** | Ordenar DS; flags se epico predecessor incompleto. |
| **Sally** | UX-DR4; sem stack ao operador. |
| **Amelia** | Docker CI; marcar `@pytest.mark.atdd`. |

## Advanced Elicitation (CS)

- **Pre-mortem:** dados de outro tenant visiveis - testes negativos RLS.
- **Red team:** segredos ou PII em audit/logs - mascarar e politica de retencao.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS** (batch epicos 7-10 / F2 / F3; rever pos-detalhe DS).

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Paths e contratos alinhados ao CDA. |
| **Amelia** | ATDD RED ligado ao ficheiro indicado. |
| **Mary** | AC cobrem FR citados. |

### Checklist BMad (sintese)

| Categoria | OK |
|-----------|-----|
| Regressao | Contrato erro 1.1 |
| RLS | `tenant_id` |
| Seguranca | RBAC em rotas sensiveis |

## Testing Requirements

- `v2/apps/api/tests/atdd/test_f3_story_f31_orchestrator_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-f2-f3.md`

## Change Log

- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
