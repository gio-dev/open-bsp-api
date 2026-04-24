---
workflowType: testarch-test-design
document: architecture
version: V2
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
---

# Test design (arquitetura): open-bsp-api - V2

**Proposito:** testabilidade, riscos e NFR para alinhamento Arquitetura/QA antes da suite.

**Data:** 2026-04-23  
**Autor:** TEA (Master Test Architect)  
**Estado:** Revisao de arquitetura pendente  
**Projeto:** open-bsp-api  
**PRD:** `_bmad-output/planning-artifacts/prd.md`  
**CDA:** `_bmad-output/planning-artifacts/architecture.md`

---

## Resumo executivo

**Ambito:** B2B/B2B2C WhatsApp: multitenancy, webhooks, inbox, regras, API publica versionada, embed, LGPD, observabilidade.

**CDA (decisoes relevantes):** FastAPI + OpenAPI + PostgreSQL + RLS; REST `/v1/`; tres superficies de auth (OAuth/OIDC consola, JWT + origem no embed, API keys e HMAC webhooks); pytest em `apps/api/tests/`; Vitest + Testing Library em `apps/admin-web`; OpenAPI validado em CI quando politica existir.

**Riscos:** 14 identificados; **6** com score >= 6. Esforco indicativo suite MVP P0+P1: **~9-18 semanas-pessoa** (intervalos no doc QA).

---

## Guia rapido

### Bloqueadores (pre-implementacao)

1. **B-01** - Seed/reset tenant/WABA em ambientes nao produtivos (fixtures transacionais ou utilitarios). **Owner:** Backend.
2. **B-02** - Job CI que falhe em breaking changes nao intencionais em `openapi.json`. **Owner:** Platform/Dev.
3. **B-03** - Stubs Meta + fila de saida para integracao deterministica. **Owner:** Arquitetura + Backend.

### Alta prioridade (validar equipa)

1. **R-004 / R-007** - Erros 401/403/429, corpo canonico, `request_id`, `Retry-After` reproduziveis em testes.
2. **R-014** - Politica dados sinteticos vs PII em ambientes de teste (LGPD).

### Informativo (ja no CDA)

- Logica testavel via API; E2E para jornadas criticas.
- Idempotencia (`Idempotency-Key`) documentada para casos positivos/negativos.

---

## Avaliacao de riscos

**Total:** 14 (6 alto >= 6, 5 medio 3-5, 3 baixo 1-2).

### Altos (score >= 6)

| Risk ID | Cat | Descricao | P | I | Scr | Mitigacao | Owner | Quando |
| ------- | --- | ---------- | - | - | --- | ---------- | ----- | ------ |
| R-001 | SEC | Cross-tenant (RLS/query sem tenant_id) | 2 | 3 | 6 | Integracao RLS; review em todo acesso a dados | Backend | Sprint 1-2 |
| R-002 | SEC | Webhook sem HMAC/replay | 2 | 3 | 6 | Payload invalido, replay, timestamp; 4xx documentados | Backend | Epic 3 |
| R-003 | DATA | Idempotencia violada | 2 | 3 | 6 | Idempotency-Key; double submit; dedup ingest | Backend | Epic 3/7 |
| R-004 | BUS | Falso enviado / UX mentirosa | 2 | 3 | 6 | UX-DR4; contrato de estado API+UI | Full-stack | Epic 3-4 |
| R-005 | PERF | Ingest/envio fora SLO sob carga | 2 | 3 | 6 | Carga smoke noturna; p95 | Platform | Pos scaffold |
| R-006 | SEC | Embed JWT ok, origem nao autorizada | 2 | 3 | 6 | Origin/allowlist; postMessage UX-DR7 | BE+FE | Epic 6 |

### Medios (3-5)

| ID | Cat | Desc | Scr | Mitigacao |
| -- | --- | ---- | --- | ---------- |
| R-007 | OPS | request_id ausente nos logs | 4 | Middleware; golden erro JSON |
| R-008 | TECH | Meta 429/timeout sem backoff testado | 4 | Retry+jitter; wire mock |
| R-009 | LGPD | DSAR fora janela | 4 | Estados + SLI |
| R-010 | PERF | Frescura inbox nao observavel | 3 | Metricas/contratos freshness |
| R-011 | A11Y | Regressao WCAG embed | 3 | Vitest+axe; roteiros |

### Baixos (1-2)

| ID | Cat | Desc | Scr | Accao |
| -- | --- | ---- | --- | ----- |
| R-012 | BUS | Copy erro generico integrador | 2 | Monitorizar |
| R-013 | OPS | Local diverge CI | 2 | Docker compose parity |
| R-014 | DATA | Fixtures com PII real | 1 | Proibir; faker+RLS |

---

## Testabilidade

### Bloqueadores fast feedback

| Problema | Impacto | O que fornecer | Owner |
| -------- | ------- | ---------------- | ----- |
| Sem seed controlado | ATDD lento | Factories + DB efemera/worker | Backend |
| Meta real em PR | Flaky | Fake WhatsApp/fila | Backend |

### Pontos fortes

- API-first; pytest + HTTP cobre maior parte do valor.
- OpenAPI como contrato para admin e integradores.

### Trade-off MVP

- Playwright completo consola/embed pode seguir o nucleo API + smoke UI (CDA).

---

## Mitigacoes (riscos >= 6) - resumo

- **R-001:** RLS em Alembic; suite "A nao le B"; break-glass com papel (historia 10-3).
- **R-002:** Assinatura invalida, nonce repetido, clock skew.
- **R-003:** Mesma chave idempotente -> mesma resposta; conflito -> 409.
- **R-004:** Maquina de estados alinhada UX-DR4.
- **R-005:** k6 noturno; error budget PRD.
- **R-006:** JWT valido + Origin errado -> 403.

---

## Suposicoes e dependencias

Postgres em CI; segredos em env; `epics.md` e matriz NFR/historia atualizados. Scaffold 1-1; export OpenAPI; stubs Meta atrasam Epic 3 -> contract tests internos primeiro.

**Doc QA:** `test-design-qa.md` (mesma pasta V2).
