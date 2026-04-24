---
story_key: 7-1-rest-versioned-idempotency
epic: epic-7
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 2-3-chaves-api-emissao-revogacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story REST versionado e idempotencia

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** Contrato integrador; headers e JSON de erro com correlation.

**Requisitos:** FR35, FR36, FR40; NFR-INT-01, NFR-SEC-05

## Acceptance Criteria (testaveis)

- OpenAPI /v1; mutacoes com Idempotency-Key; 401/429 com Retry-After documentados.
- Duplicados sem efeito indevido (politica 200/409 consistente).

## Tasks / Subtasks

- [ ] Modelo + Alembic com `tenant_id` e RLS onde houver dados.
- [ ] API `/v1/...` + OpenAPI; erros canonicos (story 1.1).
- [ ] Admin-web quando houver UI (Chakra, UX-DR).
- [ ] pytest integracao; ATDD em `v2/apps/api/tests/atdd/test_epic7_story71_rest_idempotency_atdd.py`

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

- `v2/apps/api/tests/atdd/test_epic7_story71_rest_idempotency_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `_bmad-output/test-artifacts/V2/atdd-checklist-epic-7.md`

## Change Log

- 2026-04-24: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
