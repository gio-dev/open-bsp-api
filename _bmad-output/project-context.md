---
project_name: open-bsp-api
user_name: GD-AGK
date: '2026-04-17'
generated: '2026-04-17'
sections_completed:
  - technology_stack
  - delivery_boundaries
  - multitenancy_auth_api
  - frontend_ux
  - testing_ci
  - legacy_migrations
sources:
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - CLAUDE.md
---

# Contexto do projeto para agentes de IA

Ficheiro enxuto com regras e padrões que **devem** ser seguidos na implementação. Detalhe óbvio de Python/React foi omitido em favor do que o CDA e o domínio WhatsApp exigem.

---

## Stack alvo e fronteira com legado

- **Entrega (novo código):** Python 3, **FastAPI**, **PostgreSQL**, **Alembic**; consola em **Vite + React + Chakra UI** (tokens semânticos alinhados à UX). Monorepo alvo: `apps/api` e `apps/admin-web`.
- **Proibido** para **funcionalidade nova:** Supabase Auth/Edge, Deno, ou expandir a lógica de negócio em `supabase/functions` legado, salvo migração pontual de esquema/dados mapeada para Alembic.
- **Legado** (`supabase/`, *plugins* Deno, Edge Functions) permanece **read-only** operacionalmente até *cutover*; desviar *drift* de *runtime* para a stack alvo.
- **Contrato público:** **OpenAPI** como fonte de verdade; REST sob prefixo versionado (ex. `/v1/`), *snake_case* onde o CDA assim define.

## Multitenancy e segurança

- Dados: **`tenant_id`** em tabelas relevantes; **RLS** no PostgreSQL onde aplicável. **Nunca** inferir *tenant* só por URL/corpo sem validação alinhada a claims/headers contratados (FR3, CDA).
- **Superfícies de autenticação (resumo CDA):** (1) consola: **OAuth 2.0 / OIDC** + preparação **SSO** *enterprise*; (2) **embed** (*iframe*): **JWT** (ou token opaco) + **validação de origem**/*allowlist* ? **sem** fluxo OAuth com *redirect* dentro do *iframe*; (3) máquinas: **API keys** e **HMAC** de webhooks na borda FastAPI.
- **Erros JSON:** corpo mínimo com `code`, `message`, e **`request_id`** (ou *correlation id*); cabeçalho canónico quando existir política. **Idempotência:** `Idempotency-Key` em mutações, semântica documentada.
- **Webhooks (entrada):** verificação de assinatura, deduplicação, resolução de **tenant** antes de regras de negócio (FR11?13). *Outbound notify* alinhada a `docs/modular/13-*.md` quando aplicável.
- **Segurança e limites:** TLS 1.2+; segredos em *secret manager*; **rate limit** por *tenant* com **429** e `Retry-After` documentado; degradação *upstream* (Meta) sem perda silenciosa de estado visível ao cliente.

## Front-end e UX (consola e embed)

- **Shell** estável: **React Router** com rotas *lazy*; padrão **lista | thread** + *Drawer* para regras/sandbox (MVP), sem exigir três colunas em todos os *viewports*.
- **Estados honestos (UX-DR4):** filas, 429, atraso Meta, frescura da inbox ? a UI **não** mostra sucesso falso com falha de *pipeline* sem indicação.
- **Acessibilidade:** onde o produto **assume** conformidade, alinhar a **WCAG 2.1 AA** mínima no *embed* (foco, contraste, teclado, erros) ? cruzar com NFR-A11Y.
- **401 no embed:** sem *loop* cego; renovação de token *via* **postMessage** com o *host* quando acordado (UX-DR7).

## Testes e CI (alvo CDA)

- **API:** Ruff, pytest; **front:** ESLint, Vitest.
- Incluir validação ou export de **OpenAPI** quando a política de contrato existir (evitar *breaking changes* silenciosos em CI).

## Migração e desempenho (NFR)

- **Migração legado ? alvo:** paridade e integridade cobertas por runbook/testes (NFR-REL-04 / `MIG-parity`) antes de *cutover*; não tratar *parity* como épico de produto isolado.
- **SLOs** (p95 latência, disponibilidade, *fresh* da inbox, etc.): valores numéricos vivem no PRD/Anexos; implementação deve expor *hooks* de métrica e deixar *baseline* calibrável com o piloto.

## Onde aprofundar

- CDA completo: `_bmad-output/planning-artifacts/architecture.md`
- Requisitos e SLIs: `_bmad-output/planning-artifacts/prd.md`
- Padrões de UI: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Cobertura NFR ? histórias: `_bmad-output/planning-artifacts/nfr-story-coverage-matrix.md`
- Plano de entrega: `_bmad-output/planning-artifacts/epics.md`
