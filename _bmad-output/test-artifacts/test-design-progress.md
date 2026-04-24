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
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/nfr-story-coverage-matrix.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/project-context.md
  - _bmad/tea/config.yaml
knowledgeFragmentsLoaded:
  - adr-quality-readiness-checklist.md
  - test-levels-framework.md
  - risk-governance.md
  - test-quality.md
  - probability-impact.md
  - test-priorities-matrix.md
detectedStack: backend-frontend-target
  # Monorepo apps/api + apps/admin-web ainda não materializado no repo; stack inferida do CDA.
---

# Test design ? progresso do workflow

## Step 01 ? Modo

- **Modo:** System-Level (PRD + `architecture.md` + `epics.md`; épicos já decompostos).
- **Razão:** CDA e FR/NFR completos; `sprint-status.yaml` existe mas o TD alvo é estratégia transversal antes de ATDD por história.

## Step 02 ? Contexto carregado

- **Config TEA:** `test_artifacts` ? `_bmad-output/test-artifacts`; Playwright utils ativo para E2E futuro; Pact desligado.
- **Stack alvo:** FastAPI + PostgreSQL + Alembic; `pytest` + httpx TestClient na API; Vitest + Testing Library no admin; OpenAPI como contrato.
- **Cobertura existente no repo:** sem `apps/api` / `apps/admin-web` no workspace ? suíte de produto a criar com `bmad-testarch-framework` + histórias.

## Step 03 ? Testabilidade e riscos (resumo)

- Ver matriz completa em `test-design-architecture.md`.
- **ASRs acionáveis:** RLS + resolução de `tenant_id` antes de negócio; erros canónicos (`code`, `message`, `request_id`); idempotência em mutações; três superfícies de auth (consola OAuth, embed JWT+origem, máquinas API key/HMAC).

## Step 04 ? Plano de cobertura (resumo)

- Pirâmide: **unit** (regras, parsers, políticas RLS em lógica pura) ? **integração** (API + DB de teste, webhooks assinados) ? **E2E** (jornadas críticas consola/embed quando UI existir).
- Estimativas e gates: ver `test-design-qa.md`.

## Step 05 ? Saídas finais

| Artefacto | Caminho |
|-----------|---------|
| Arquitetura / testabilidade | `_bmad-output/test-artifacts/test-design-architecture.md` |
| Receita QA | `_bmad-output/test-artifacts/test-design-qa.md` |
| Handoff BMAD | `_bmad-output/test-artifacts/test-design/open-bsp-api-handoff.md` |

**Próximo workflow recomendado:** `bmad-testarch-framework` (TF) ? `bmad-testarch-ci` (CI) ? por história `bmad-testarch-atdd` (AT) ? `bmad-dev-story` (DS).
