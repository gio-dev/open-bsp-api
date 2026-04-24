---
workflowType: testarch-test-design
document: architecture
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/epics.md
---

# Test design (arquitetura): open-bsp-api

**Propósito:** preocupações de testabilidade, riscos e NFR para alinhamento entre Arquitetura e QA antes de desenvolver a suíte.

**Data:** 2026-04-23  
**Autor:** TEA (Master Test Architect)  
**Estado:** Revisão de arquitetura pendente  
**Projeto:** open-bsp-api  
**PRD:** `_bmad-output/planning-artifacts/prd.md`  
**CDA / ADR:** `_bmad-output/planning-artifacts/architecture.md`

---

## Resumo executivo

**Âmbito:** plataforma B2B/B2B2C WhatsApp ? multitenancy, ingestão de webhooks, inbox, regras, API pública versionada, embed, LGPD e observabilidade.

**Contexto de negócio (PRD):** centralizar mensagens, reduzir trabalho manual, atendimento mensurável; dependência Meta volátil explícita; honestidade de estados na UX.

**Decisões arquitetónicas relevantes (CDA):**

- FastAPI + OpenAPI + PostgreSQL + RLS; REST `/v1/...`, snake_case no fio.
- Três superfícies de autenticação: OAuth/OIDC (consola), JWT + validação de origem (embed), API keys e HMAC webhooks (máquinas).
- Testes: `pytest` em `apps/api/tests/`; Vitest + Testing Library em `apps/admin-web`; validação/export de OpenAPI em CI quando política existir.

**Escala esperada:** pilotos multi-tenant; SLO numéricos no Anexo A do PRD (calibrar em produção piloto).

**Riscos (sumário):** 14 identificados; **6 com score ? 6**; esforço de testes MVP (desenvolvimento da suíte) estimado em **~9?18 semanas·pessoa** para P0+P1 (intervalos no doc QA).

---

## Guia rápido

### Bloqueadores ? decisão pré-implementação

1. **B-01 ? Hooks de dados de teste** ? Contrato para *seed*/*reset* de tenant/WABA em ambientes não produtivos (ex.: utilitários de teste ou *fixtures* de BD com transações). **Owner:** Backend. **Sem isto:** integração paralela e ATDD lenta/flaky.
2. **B-02 ? Contrato OpenAPI em CI** ? Job que falha em *breaking changes* não intencionais no `openapi.json`. **Owner:** Platform/Dev. **Sem isto:** *drift* entre admin e API.
3. **B-03 ? *Stubs* Meta / fila** ? Estratégia explícita para simular WhatsApp Cloud API e filas de saída nos testes de integração. **Owner:** Arquitetura + Backend.

### Alta prioridade ? validar com equipa

1. **R-004 / R-007** ? Semântica de erros (401/403/429), corpo canónico e `request_id` / `Retry-After` reproduzíveis em testes.
2. **R-014** ? Política de dados sintéticos vs PII em ambientes de teste (LGPD).

### Informativo ? já alinhado no CDA

- Pirâmide: lógica via API; E2E reservado a jornadas críticas.
- `request_id` no erro e nos logs para asserções de rastreio.
- Documentação de idempotência (`Idempotency-Key`) para casos de teste negativos/positivos.

---

## Para arquitetos e desenvolvimento

### Avaliação de riscos

**Total:** 14 (**6** alto **? 6**, **5** médio 3?5, **3** baixo 1?2).

#### Riscos altos (score ? 6)

| Risk ID | Categoria | Descrição | P | I | Score | Mitigação | Owner | Timeline |
| -------- | --------- | ----------- | - | - | ----- | --------- | ----- | -------- |
| R-001 | SEC | Vazamento cross-tenant (RLS mal configurada ou query sem `tenant_id`) | 2 | 3 | **6** | Testes de integração RLS obrigatórios; *code review* em todo acesso a dados; políticas nomeadas no DDL | Backend | Sprint 1-2 |
| R-002 | SEC | Webhook aceite sem verificação HMAC/replay | 2 | 3 | **6** | Testes com payload inválido, *replay*, *timestamp* fora da janela; rejeição documentada | Backend | Épico 3 |
| R-003 | DATA | Idempotência violada ? duplicação de efeitos | 2 | 3 | **6** | Contrato `Idempotency-Key`; testes de *double submit*; *dedup* ingest | Backend | Épico 3 / 7 |
| R-004 | BUS | «Falso enviado»: UI/integrador indica sucesso com falha de pipeline | 2 | 3 | **6** | Estados honestos (UX-DR4); testes de contrato de estado + API | Full-stack | Épico 3-4 |
| R-005 | PERF | Ingest ou envio fora de SLO sob carga | 2 | 3 | **6** | Testes de carga *smoke* em CI noturno; métricas p95 | Platform | Pós scaffold |
| R-006 | SEC | Embed: JWT válido mas origem não autorizada | 2 | 3 | **6** | Testes de `Origin` / *allowlist*; *postMessage* token conforme UX-DR7 | Backend + Front | Épico 6 |

#### Riscos médios (3?5)

| Risk ID | Categoria | Descrição | P | I | Score | Mitigação | Owner |
| ------- | --------- | ----------- | - | - | ----- | --------- | ----- |
| R-007 | OPS | `request_id` ausente ou não correlacionado nos logs | 2 | 2 | 4 | Middleware único; *golden tests* de erro | Backend |
| R-008 | TECH | Flakiness Meta (429/timeout) sem *backoff* testado | 2 | 2 | 4 | Retries com jitter; testes com *wire mock* | Backend |
| R-009 | LGPD | DSAR fora da janela operacional acordada | 2 | 2 | 4 | Testes de transição de estado + SLI | Backend |
| R-010 | PERF | Frescura inbox (NFR-PERF-02) não observável em teste | 1 | 3 | 3 | *Hooks* de métrica / contratos de *freshness* | Backend |
| R-011 | A11Y | Regressão WCAG no embed | 1 | 3 | 3 | Vitest + axe onde aplicável; roteiros manuais mínimos | Front |

#### Riscos baixos (1?2)

| Risk ID | Categoria | Descrição | Score | Acção |
| ------- | --------- | ----------- | ----- | ----- |
| R-012 | BUS | Copy de erro genérico demais para integrador | 2 | Monitorizar |
| R-013 | OPS | Ambiente local diverge de CI | 2 | Docker compose / *parity* documentada |
| R-014 | DATA | *Fixtures* com dados pessoais reais | 1 | Proibir; *faker* + RLS |

**Legenda:** TECH, SEC, PERF, DATA, BUS, OPS ? conforme `risk-governance.md`.

---

### Testabilidade: lacunas e pedidos à arquitetura

#### Bloqueadores de *fast feedback*

| Preocupação | Impacto | O que a arquitetura deve fornecer | Owner | Marco |
| ----------- | ------- | ----------------------------------- | ----- | ----- |
| Sem API/utilitário de *seed* controlado | ATDD lento, paralelo inviável | Factories + *setup* transaccional ou DB efémera por worker | Backend | Com 1-1 |
| Meta real nos testes de PR | Flaky, não determinístico | *Ports* internos para *fake* WhatsApp/fila | Backend | Épico 3 |

#### Pontos fortes (FYI)

- API-first: maior parte do valor testável com `pytest` + HTTP.
- OpenAPI como fonte de verdade para contrato e clientes TS.
- Erro canónico + `request_id` facilita asserções e *correlation*.

#### Trade-offs aceites (MVP)

- E2E Playwright completo consola/embed pode ficar **após** núcleo API + *smoke* UI ? documentado no CDA como desejável pós-MVP para alguns cenários.

---

### Mitigações detalhadas (riscos ? 6)

**R-001:** Políticas RLS versionadas com Alembic; *suite* «tenant A não lê B» em cada entidade nova; *break-glass* apenas com papel explícito (história 10-3).  
**R-002:** Vetor de testes: assinatura inválida, *nonce* repetido, *clock skew*.  
**R-003:** Mesmo `Idempotency-Key` ? mesma resposta; conflito ? 409 documentado.  
**R-004:** Contrato de máquina de estados na API alinhado a UX-DR4; sem 200 sem persistência quando o produto promete entrega visível.  
**R-005:** *k6* ou equivalente no *nightly*; orçamento de erro no PRD.  
**R-006:** Matriz de testes: JWT válido + `Origin` errado ? 403; renovação embed via *postMessage* mockada.

---

### Suposições e dependências

**Suposições:** Postgres disponível em CI; segredos de teste em variáveis de ambiente; equipe mantém `epics.md` e matriz NFR?história atualizados.

**Dependências:** *Scaffold* monorepo (história 1-1); política de export OpenAPI; acesso a *artifact* de schema em PRs.

**Risco do plano de testes:** atraso nos *stubs* Meta atrasa Épico 3 ? contingência: *contract tests* internos primeiro, E2E canal depois.

---

**Documento QA associado:** `test-design-qa.md` (cenários, níveis, execução).

**Próximos passos (arquitetura):** fechar B-01?B-03; atribuir donos às mitigações ? 6; validar suposições com PM.
