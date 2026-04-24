---
workflowStatus: completed
totalSteps: 5
stepsCompleted:
  - step-01-detect-mode
  - step-02-load-context
  - step-03-risk-and-testability
  - step-04-coverage-plan
  - step-05-generate-output
lastStep: step-05-generate-output
nextStep: ''
lastSaved: '2026-04-23'
workflowType: testarch-test-design
mode: system-level
version: V2
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/nfr-story-coverage-matrix.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/project-context.md
  - _bmad/tea/config.yaml
---

# Test design (progresso do workflow) - V2

## Step 01 - Modo

- **Modo:** System-Level (PRD + architecture.md + epics.md).
- **Motivo:** Estrategia transversal de testes antes de ATDD por historia.

## Step 02 - Contexto

- **TEA:** artefactos em `_bmad-output/test-artifacts`; Playwright ativo para E2E futuro.
- **Stack alvo:** FastAPI, PostgreSQL, pytest + httpx na API; Vitest no admin; OpenAPI como contrato.
- **Repo:** monorepo `apps/api` e `apps/admin-web` ainda a materializar; suite de produto nasce com TF + historias.

## Step 03 - Riscos (resumo)

- 14 riscos registados; 6 com score >= 6. Detalhe em `test-design-architecture.md`.

## Step 04 - Cobertura (resumo)

- Piramide: unit -> integracao (API + DB, webhooks) -> E2E (jornadas criticas quando UI existir).

## Step 05 - Saidas V2

| Artefacto | Caminho |
|-----------|---------|
| Arquitetura | `V2/test-design-architecture.md` |
| QA | `V2/test-design-qa.md` |
| Handoff BMAD | `V2/test-design/open-bsp-api-handoff.md` |

**Proximo:** `bmad-testarch-framework` (TF) -> `bmad-testarch-ci` (CI) -> por historia `bmad-testarch-atdd` (AT) -> `bmad-dev-story` (DS).
