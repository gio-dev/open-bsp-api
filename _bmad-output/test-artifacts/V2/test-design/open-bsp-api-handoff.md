---
title: TEA Test Design para BMAD Handoff
version: V2
workflowType: testarch-test-design-handoff
projectName: open-bsp-api
generatedAt: '2026-04-23'
sourceFolder: _bmad-output/test-artifacts/V2
---

# TEA -> BMAD: handoff qualidade (open-bsp-api) V2

## Proposito

Ligar o test design as historias/epicos existentes (`epics.md`): gates, riscos, cenarios em AC ou suite ATDD.

## Inventario artefactos V2

| Artefacto | Caminho |
| --------- | ------- |
| Arquitetura | `_bmad-output/test-artifacts/V2/test-design-architecture.md` |
| QA | `_bmad-output/test-artifacts/V2/test-design-qa.md` |
| Progresso | `_bmad-output/test-artifacts/V2/test-design-progress.md` |
| CI / gates / ATDD | `_bmad-output/test-artifacts/V2/ci-pipeline.md` |
| NFR x historia | `_bmad-output/planning-artifacts/nfr-story-coverage-matrix.md` |

## Gates por epic (minimo)

| Epic | Gate |
| ---- | ---- |
| 1 | CI lint+test; prova RLS 1-2 |
| 2 | RBAC + rotacao segredos com testes negacao |
| 3 | Webhook happy + invalido + replay |
| 4 | Estados honestos UX-DR4 |
| 5 | Sandbox vs prod; motor deterministico |
| 6 | Origin + JWT embed |
| 7 | OpenAPI em PR; double-submit idempotente |
| 8-10 | Matriz NFR/historia |

## Cenarios P0 para AC / ATDD

1. Isolamento tenant: token A nunca acede recurso B.
2. Webhook: assinatura invalida -> 4xx documentado; replay rejeitado.
3. Idempotencia: segunda mutacao mesma chave nao duplica efeito.
4. Erro canonico: 401/403/429 com code, message, request_id (+ Retry-After se 429).
5. Embed: JWT valido + origem fora allowlist -> negado.

## Testabilidade UI

`data-testid` estavel em fluxos P0 (login, inbox, drawer regras) quando Playwright entrar.

## Risco -> historia (amostra)

| Risk | Scr | Historias / epic |
| ---- | --- | ---------------- |
| R-001 | 6 | 1-2-tenant-rls; dados em epics 2-10 |
| R-002 | 6 | 3-1-webhook-entrada |
| R-003 | 6 | 7-1-rest-versioned-idempotency; 3-2-enviar-mensagem |
| R-004 | 6 | 3-2; 4-4-sinais |
| R-005 | 6 | 3-1; 7-1; NFR-PERF |
| R-006 | 6 | 6-1-embed-autenticado |
| R-007 | 4 | 1-1-monorepo; golden erro rotas publicas |
| R-009 | 4 | 9-2-dsar |

## Sequencia recomendada

1. TD V2 (feito)
2. TF - framework pytest/Vitest (**convencoes e smoke:** `_bmad-output/test-artifacts/V2/test-framework.md`; execucao sempre Docker em `v2/`)
3. CI - Ruff pytest eslint vitest OpenAPI (**gates e ATDD:** `_bmad-output/test-artifacts/V2/ci-pipeline.md`)
4. CS/VS historia
5. AT - red
6. DS - implementacao
7. CR
8. TA/TR

## Gates fase

| De | Para | Criterio |
| -- | ---- | -------- |
| TD | Implementacao | B-01 a B-03 com dono; riscos >= 6 mitigados planeaveis |
| ATDD | Dev | Red reprodutivel P0 da historia |
| Dev | RC | P0 verde; P1 politica equipa |

---

**Consumidores:** refinement, `bmad-testarch-atdd`, owners epic.
