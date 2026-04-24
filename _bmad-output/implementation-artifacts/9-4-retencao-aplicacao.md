---
story_key: 9-4-retencao-aplicacao
epic: epic-9
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 9-3-lista-subprocessadores
code_location: v2/apps/api, v2/apps/admin-web
---

# Story Retencao e aplicacao

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Retencao tecnica + jobs.

**Requisitos:** FR48, FR49, NFR-LGPD-02

## Acceptance Criteria (testaveis)

- Config, jobs, relatorios agregados.

## Tasks / Subtasks

- [ ] Modelo + Alembic com `tenant_id` e RLS onde houver dados.
- [ ] API `/v1/...` + OpenAPI; erros canonicos (story 1.1).
- [ ] Admin-web quando houver UI (Chakra, UX-DR).
- [ ] pytest integracao; ATDD em `v2/apps/api/tests/atdd/test_epic9_story94_retention_atdd.py`

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

- `v2/apps/api/tests/atdd/test_epic9_story94_retention_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-9.md`

## Change Log

- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
