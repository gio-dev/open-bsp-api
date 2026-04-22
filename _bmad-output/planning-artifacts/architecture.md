---
stepsCompleted:
  - step-01-init.md
  - step-02-context.md
  - step-03-starter.md
  - step-04-decisions.md
  - step-05-patterns.md
  - step-06-structure.md
  - step-07-validation.md
  - step-08-complete.md
inputDocuments:
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/prd-decisoes-registradas-gd-agk.md
  - _bmad-output/planning-artifacts/product-brief-autocontrollerbot.md
  - _bmad-output/planning-artifacts/product-brief-autocontrollerbot-distillate.md
  - _bmad-output/planning-artifacts/research/platform-MR-DR-TR-aprofundado-2026-04-17.md
  - _bmad-output/planning-artifacts/research/platform-openbsp-skus-MR-DR-TR-2026-04-17.md
  - docs/index.md
  - docs/modular/README.md
  - docs/modular/00-caso-e-escopo.md
  - docs/modular/01-arquitetura-reativa-visao-geral.md
  - docs/modular/02-rotina-whatsapp-webhook.md
  - docs/modular/03-rotina-mensagens-triggers-edge.md
  - docs/modular/04-rotina-agent-client.md
  - docs/modular/05-rotina-whatsapp-dispatcher.md
  - docs/modular/06-rotina-media-preprocessor.md
  - docs/modular/07-rotina-whatsapp-management.md
  - docs/modular/08-rotina-mcp-servidor-api.md
  - docs/modular/09-rotina-webhooks-saida-integracoes.md
  - docs/modular/10-rotina-deploy-ci-billing-vault.md
  - docs/modular/11-extensoes-rag-n8n-aprendizado.md
  - docs/modular/12-apendice-rotas-http-e-contratos.md
  - docs/modular/13-notify-webhook-semantica-e-riscos.md
  - docs/modular/14-contatos-onboarding-e-rls.md
  - docs/modular/15-mcp-servidor-catalogo-ferramentas.md
  - docs/modular/98-party-mode-perspectivas-rota.md
  - docs/modular/99-elicitacao-pre-mortem-e-riscos.md
  - docs/modular/100-elicitacao-metodos-adicionais.md
workflowType: architecture
lastStep: 8
status: complete
completedAt: '2026-04-17'
project_name: open-bsp-api
user_name: GD-AGK
date: '2026-04-17'
documentCounts:
  prd: 1
  uxDesign: 1
  research: 2
  productBriefs: 2
  projectDocs: 21
  projectContext: 0
elicitationArchitectureStep2:
  methods: "Mapeamento stress UX para requisitos de sistema (Mary); Party Mode (Sally, Winston, John); síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep3:
  methods: "Exploração de alternativas de baseline (Mary); Party Mode (Sally, Winston, John); síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep4:
  methods: "Inversão de pressupostos / tradeoffs de fronteira (Mary); Party Mode (Sally, Winston, John); síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep5:
  methods: "Análise de conflitos agente?agente / contratos (Mary, Advanced Elicitation); Party Mode (Sally, Winston, John); síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep6:
  methods: "Mapeamento fronteira módulo?FR / anti-confusão monorepo (Mary, Advanced Elicitation); Party Mode (Sally, Winston, John); síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep7:
  methods: "Validação de coerência, cobertura e *readiness* (Mary, Advanced Elicitation); Party Mode (Sally, Winston, John) sobre lacunas, riscos e *handoff*; síntese orchestrator"
  date: "2026-04-17"
elicitationArchitectureStep8:
  methods: "Encerramento do *workflow* e *next steps* (Mary, Advanced Elicitation); Party Mode (Sally, Winston, John) sobre *guardrails* pós-AD e *go-live* do documento; síntese orchestrator"
  date: "2026-04-17"
platformStack:
  decision: "O produto é implementado **exclusivamente** com **Python 3 + FastAPI**, **PostgreSQL**, e na consola **OAuth/OIDC** como **login base** e **SSO (SAML/OIDC *enterprise*)** para **login externo**; **não** se usa **Supabase**, **Deno** nem **Edge Functions** na arquitetura de entrega."
  excluded: "Supabase (Postgres gerido, Auth, CLI, funções), runtime Deno, e qualquer código de borda que não seja o processo FastAPI (ou *worker* Python do mesmo repositório)."
  legacy_in_repo: "Diretórios históricos (ex. `supabase/`, *plugins* em Deno) podem existir no Git apenas como **referência** ou para **migração pontual** de esquema/dados; **proibido** adicionar funcionalidade nova aí. O *refactor* aplica-se a **reimplementar** domínio em `apps/api` (e rotas HTTP em FastAPI)."
  authSurfaces: "Consola: **login base** via **OAuth 2.0 / OIDC**; **SSO** para **login externo** (federation com IdP do cliente, p.ex. SAML 2.0 e/ou OIDC *enterprise*). Iframe *Embedded*: **JWT** (ou equivalente) + **validação de domínio** (*allowlist* / *claims*); o detalhe do *Embedded* (variantes, rotação, opaco *vs* JWT) fica no **ADR** se existir opção *estritamente* melhor que o *baseline*."
  multitenancy: "Isolamento **lógico** de dados: **um** repositório PostgreSQL **partilhado** (mesmo *cluster* / instância alvo) com **tenant_id** em tabelas relevantes e **RLS** onde aplicável. **Não** é modelo **\"um banco de dados (instância) por cliente/organização\"**; essa opção (silos) só por **ADR** excecional (regulatório, *noisy neighbor*, requisito contratual) com custo de *migrations*, *backup* e *pool* explícito."
uxArchitectureAlignment:
  source: _bmad-output/planning-artifacts/ux-design-specification.md
  highlights:
    - "Split lista | thread (MVP) + Drawer para regra/sandbox; shell estável + rotas lazy"
    - "Chakra UI + tokens; WCAG 2.1 AA; correlation id e estados honestos (429, fila, Meta)"
    - "Superfícies: SPA, embed (iframe), futuro Capacitor ? paridade de contratos de erro e sessão"
---

# Architecture Decision Document

Este documento constrói-se por passos; as secções acumulam-se à medida que as decisões são tomadas.

---

## Project Context Analysis (passo 2)

*Entrada ampliada em relação ao ciclo anterior: **`ux-design-specification.md`** (passos 1?10 do `bmad-create-ux-design`), alinhado ao PRD e à documentação modular em `docs/modular/`.*

### Requirements Overview

**Requisitos funcionais (síntese PRD ? categorias):**

| Área | Implicação arquitetónica |
|------|---------------------------|
| **Organização / tenant / WABA** | Isolamento de dados e de contexto operacional (FR1?FR4); resolução inequívoca de tenant na ingestão (FR13). |
| **Identidade e credenciais** | Consola: **OAuth/OIDC** (login base) e **SSO** (login externo); **embed**: **JWT** + validação de domínio, ADR se houver alternativa preferível (ver D2); RBAC (FR6?FR7); API keys e webhooks (FR8?FR10). |
| **Canal WhatsApp** | Webhooks verificados, anti-replay/frescura (FR11?FR12), envio e política de templates (FR14?FR16). |
| **Inbox, filas, handoff** | Inbox unificada, triagem, handoff com contexto (FR17?FR21) ? exige modelo de conversação, filas e sinais **por tenant**. |
| **Automação por regras** | Construtor, sandbox, publicação, auditoria de versões, ações disparadas (FR22?FR26); F2/F27 e F3/FR28 explícitos como fases futuras. |
| **Embed e B2B2C** | Painel embutido com sessão adequada (FR29), transparência bot/humano (FR30), LGPD no fluxo (FR31?FR33), acessibilidade declarada (FR34). |
| **API pública e integração** | Idempotência, versionamento, sandbox, reconciliação de webhooks, erros documentados incl. 401/429 (FR35?FR40). |
| **Medição, planos, relatórios** | Eventos de uso, relatórios de valor, quotas (FR41?FR44). |
| **Governança e LGPD** | Finalidades, DSAR, retenção, consentimento (FR45?FR50). |
| **Suporte e auditoria** | Correlation / classificação de culpa, auditoria, break-glass (FR51?FR54). |

**Requisitos não funcionais (âmbito):** desempenho e latência (p95 por rota, **OBS-fresh** inbox), fiabilidade (**API-avail**, drenagem de backlog), segurança e dados, observabilidade, multitenant e fairness, conformidade ? com **SLI/SLO** no Anexo A do PRD como fonte primária de números.

**UX (spec) ? tradução para arquitetura:**

- **Superfícies múltiplas com um núcleo:** React + Chakra; mesma disciplina de **tokens**, estados de sistema e erros em **SPA**, **embed** e (futuro) **Capacitor** ? implica **APIs e contratos de sessão** consistentes, não só CSS.
- **Experiência definidora (spec passo 7):** continuidade **num único fio** (conversa + regra + handoff no mesmo contexto mental) ? backend e **modelo de eventos** devem suportar **visibilidade correlacionada** (?recibos?), não só CRUD desligado.
- **Direção visual (passo 9):** **split lista | thread** + **Drawer** para regra/sandbox ? encaixa em **layout estável + `Outlet` + code-splitting**; evita supor viewport infinito no embed (**min-width**, altura controlada).
- **Jornadas (passo 10):** recuperação em falha (sandbox vs publicação, handoff falho, OAuth, incidente Meta) ? arquitetura deve expor **estado de pipeline**, **correlation id** em erros e filas **acionáveis**, alinhado a NFRs e a FR40.
- **Acessibilidade:** WCAG 2.1 AA no baseline ? impacta componentes partilhados e testes, não só copy.

### Scale & Complexity

| Indicador | Avaliação |
|-----------|-----------|
| **Domínio principal** | Full-stack **SaaS B2B/B2B2B**: API + edge/webhooks + painel web + embed. |
| **Complexidade global** | **Alta** (multitenant, canal externo Meta, LGPD, integrações, observabilidade ponta a ponta). |
| **Tempo real** | Inbox com SLO de **frescura** (não necessariamente WebSockets no MVP ? mas **latência percecionada** e estados de fila são de primeira classe). |
| **Integração** | Meta BSP, OAuth, webhooks entrada/saída, API pública versionada. |
| **Componentes arquitetónicos estimados** | Borda (webhook/HTTP), domínio multitenant, motor de regras, mensagens/dispatcher, inbox/conversas, identidade, billing/uso, observabilidade, painel SPA/embed (front como consumidor de API). |

**Tamanho do requisito:** dezenas de FR materialmente rastreáveis (FR1?FR54) + NFRs por categoria; **UX** adiciona restrições de **superfície** e **honestidade operacional** sem alterar o enumerado do PRD, mas **refina prioridade** de APIs e de modelo de eventos.

### Technical Constraints & Dependencies

- **Stack única de entrega:** ver `platformStack` no frontmatter ? **FastAPI + PostgreSQL**; **sem Supabase, sem Deno**. Documentação em `docs/modular/` permanece como **especificação de domínio**; o código cumpre-se em **Python**.
- **Brownfield:** se existir código antigo no repo, a paridade (**MIG-parity**) aplica-se à **reimplementação** em FastAPI, não à manutenção de runtimes excluídos.
- **Meta como dependência:** indisponibilidade, 429, política de templates ? **fairness entre tenants** e mensagens **honestas** (UX + NFR); não assumir canal sempre saudável.
- **Embed:** **auth** distinta da consola (OAuth/SSO): *baseline* **JWT** (ou token opaco) + **validação de domínio**; injeção pelo host; sem OAuth/SSO *redirect* *dentro* do iframe; **SSO** permanece no **login da consola**; ADR *Embedded* para *baseline* e variantes.
- **LGPD:** fluxos no painel e no canal; retenção e DSAR ? modelo de dados e pipelines de exportação/eliminação.
- **Documentação interna:** rotinas em `docs/modular/` (webhook, dispatcher, RLS, notify, etc.) são **constraints de implementação** para decisões alinhadas.

### Cross-Cutting Concerns Identified

1. **Tenancy e isolamento** ? em toda a cadeia: ingestão, API, UI, relatórios, suporte N2.
2. **Observabilidade e correlation** ? SLIs, request/correlation id, culpa Meta vs plataforma vs cliente (FR51 + UX ?recibos?).
3. **Versionamento** ? regras/fluxos, API pública, eventos de webhook (FR25, FR36?FR37).
4. **Segurança operacional** ? rotação de credenciais, anti-replay, RBAC, break-glass.
5. **Consistência multi-superfície** ? mesmos contratos de erro e de sessão para web, embed e futuro mobile wrapper.
6. **Acessibilidade e densidade** ? tokens Chakra, modos Comfortable/Compact, alvos de toque ? afeta bundles e testes, não só CSS.

### Advanced Elicitation + Party Mode (passo 2 ? CA)

**Mapeamento stress UX ? sistema (Mary):** cada tensão explícita no UX spec (embed, 429, handoff, ?recibos?, incidente Meta) foi mapeada a **capacidades de backend**: estado de fila/pipeline visível, **IDs de correlação** em falhas, **frescura** observável na inbox, **idempotência e ordem** em webhooks ? para não tratar UX como ?só front?.

- **Sally (UX):** o **fio** (lista | thread) é a espinha dorsal; regra e sandbox são **lentes** (Drawer) ? a arquitetura deve servir **uma vista de conversa coerente**, com navegação previsível no embed.
- **Winston (arquitetura):** **401 sem loop**, **429 com Retry-After e backoff**, webhooks **fora de ordem** com idempotência explícita; **correlation id** em API, filas e resposta de erro; shell **React Router** + boundaries lazy alinhados ao split.
- **John (produto):** métricas de **tarefa** e anti-vanity do PRD exigem eventos **por tenant** e **outcomes** auditáveis ? ?dashboard genérico? não substitui **recibos** e gates de piloto.

---

## Starter Template Evaluation (passo 3)

*Stack de entrega: **apenas** **FastAPI (Python)** + **PostgreSQL** + **Vite/React/Chakra** no admin. **Deno e Supabase estão excluídos** ? ver `platformStack` no frontmatter. **Versões:** `npm view` / `uv` ou `pip` no arranque do projeto; não fixar números no spec sem verificação local.*

### Primary Technology Domain

| Camada | Domínio |
|--------|---------|
| **API / borda** | **FastAPI**: HTTP, webhooks WhatsApp, *workers* (Celery/RQ/ARQ, etc.) conforme ADR; **um** processo app ou *workers* irmãos no mesmo repositório. |
| **Dados** | **PostgreSQL** (instância própria ou cloud gerida **sem** Supabase); **RLS**; migrações com **Alembic**. |
| **Painel (UX spec)** | **SPA React** + **Chakra UI** + TypeScript; **Vite**; embutível em **iframe**; **Capacitor** futuro. Consome **só** a API OpenAPI/REST. |

**Conclusão:** **não** há ?backend interino? Deno/Supabase para novas entregas. O **scaffold** alvo é **`apps/api`** (FastAPI) + **`apps/admin-web`** (Vite) no mesmo monorepo, salvo ADR a separar repositórios.

### Starter Options Considered

| Opção | O que estabelece | Prós | Contras / riscos |
|-------|------------------|------|------------------|
| **A ? Supabase / Deno (histórico)** | *Não é opção de implementação* | ? | **Excluída** ? ver `platformStack.excluded`. |
| **B ? Vite + React + TS + Chakra UI v3** | SPA, embed, *design system* alinhado ao UX spec | Chakra oficial com Vite; a11y | Fixar versões no `package.json` ao criar. |
| **C ? Next.js** | SSR, rotas ficheiro | SEO | Pior para embed/cookies; **não** como default. |
| **D ? T3 / tRPC** | *Monólito* tipado | Rápido *greenfield* | Foge ao contrato REST/OpenAPI do produto. |
| **E ? OpenBSP UI (Tailwind)** | Referência noutro repo | Inspiração | **Chakra** no spec; só padrões de API. |

**Advanced Elicitation (Mary):** monorepo `apps/*` **vs** repositórios separados; **uv** *vs* **Poetry** / **pip-tools** (fixar no ADR *tooling* Python); *Storybook* opcional (Sally); **TanStack Router** *vs* **React Router** (MVP: React Router).

### Selected Starter(s)

**1) Backend: FastAPI (única borda de negócio)**

- **Racional:** **OpenAPI** nativo, **Pydantic v2**, async, ecossistema Python para integração Meta, filas e LGPD.
- **Scaffold (exemplo; ajustar à ferramenta escolhida):**

```bash
mkdir -p apps/api && cd apps/api
# Criar pyproject com FastAPI, uvicorn[standard], SQLAlchemy ou SQLModel, Alembic, httpx, pydantic-settings
# uv sync  OU  pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Webhooks, dispatcher, regras:** **routers** e **services** em `app/`, *não* ficheiros Deno.
- **Testes:** `pytest` em `apps/api/tests/`.

**2) Painel admin / embed: Vite + React + TypeScript + Chakra UI**

- **Racional:** alinha ao **UX Design Specification** (Chakra, WCAG, split lista | thread, Drawer, tokens); **Vite** mantém SPA simples, **adequada a iframe** e a futura embalagem Capacitor sem impor SSR.
- **Não** impor Next.js como default (opção C) para não complicar embed e política de sessão em terceiros sem necessidade explícita.

**Comando de scaffold (verificar flags na documentação Vite vigente):**

```bash
npm create vite@latest openbsp-admin -- --template react-ts
cd openbsp-admin
npm install
```

**Seguir a seguir:** guia oficial **Chakra UI × Vite** (instalação `@chakra-ui/react`, provider, tema; Node **20+** conforme requisitos Chakra v3).

**Versões:** antes de commitar, fixar com:

```bash
npm view vite version
npm view @chakra-ui/react version
npm view react version
```

*(Os números exatos mudam; o requisito do passo 3 é **não confiar em versões hardcoded** no spec ? validar no init.)*

### Architectural Decisions Provided by the Combined Starters

**Linguagem e runtime**

- **Borda (única):** **Python 3.x + FastAPI**; *workers* assíncronos (filas) em processo Python, não Deno.
- **Admin:** **TypeScript** estrito; **Vite** + **ESM**.

**Styling / UI**

- **Chakra UI v3** + tokens semânticos (spec UX); sem Tailwind como base do design system **deste** painel (diferente do companion Tailwind, se coexistir).

**Build e tooling**

- **Vite:** *dev* + *build*; *code splitting* (lista \| thread, *drawer*).
- **Backend:** *Dockerfile* + `uvicorn` / *orchestrator*; CI *lint* (Ruff), *test* (pytest), *typecheck*; ver `docs/modular/10-*` para princípios de deploy.

**Testes**

- Front: **Vitest** + **Testing Library**.
- API: **pytest** + *httpx* `TestClient` (ou equivalente) para rotas e serviços.

**Organização de código**

- **Backend:** **monólito modular FastAPI** (`routers/`, `services/`, `repositories/` ou padrão escolhido); domínios (webhook, dispatcher, regras, ?) como **módulos** Python; **SPA** por *features* com **layout estável** + `Outlet` (UX).

**Estado e dados**

- Cliente: estado de UI + **React Query (TanStack Query)** ou equivalente para cache de API (decisão fina no passo 4/5 se necessário).
- Servidor: Postgres + RLS; padrões em `docs/modular/14-contatos-onboarding-e-rls.md` etc.

### Flow Optimization Principles (starter)

- **Um contrato:** **OpenAPI** gerado pelo FastAPI como fonte para o *admin* e integradores (evitar *drift*).
- **Embed primeiro:** build Vite com `base` configurável se o admin for servido fora do origin da API.
- **Observabilidade desde o primeiro PR:** *correlation id* nos clientes HTTP do painel (FR51, UX *recibos*).

### Advanced Elicitation + Party Mode (passo 3 ? CA)

- **Advanced Elicitation (Mary):** **uv** *vs* **Poetry** e *layout* `app/` (evitar três estilos de *import* no mesmo repo); *webhook* como **router** FastAPI dedicado *vs* *subapp* (fixar no primeiro ADR de *routing*).
- **Party Mode ? Sally:** o *admin* consome **só** `/v1` OpenAPI; **consola** = OAuth (base) + SSO (externo); **embed** = *Bearer* + validação de domínio (JWT *baseline*); sem *SDK* *backend* no browser.
- **Party Mode ? Winston:** **um** `FastAPI()` (ou fábrica) com *lifespan*, *middleware* de `request_id`, CORS, *exception handlers* únicos; *workers* em módulo separado se necessário.
- **Party Mode ? John:** *scope* = **FastAPI** + *Postgres* + *Chakra*; **Deno/Supabase fora** do *delivery*.

---

## Core Architectural Decisions (passo 4)

*Decisões alinhadas a **`platformStack`:** **só** **Python (FastAPI) + PostgreSQL**; **excluídos Supabase e Deno**. **Multitenant:** base **partilhada** + **tenant_id** + **RLS** ? ver `multitenancy` no frontmatter (não **um** banco **por** cliente, salvo ADR excecional). **Auth (consola):** **OAuth/OIDC** (login base) e **SSO** (login externo). **Auth (embed):** **JWT** + **validação de domínio**; detalhe do *Embedded* no ADR se houver opção preferível ? ver `authSurfaces`. **Versões:** `npm view` (front) e `pyproject` / ambiente (API).*

### Decision Priority Analysis

**Críticas (bloqueiam implementação coerente):**

| ID | Decisão | Síntese |
|----|---------|---------|
| **D1** | Fonte de verdade dos dados | **PostgreSQL** (instância(s) alvo do produto) com **um único *schema* lógico de produto** partilhado: linhas com **`tenant_id`** e **RLS** por *tenant* onde aplicável (`docs/modular/14-*`). A individualidade de cada **cliente/organização** é **lógica** (política + aplicação), **não** ?uma base *Postgres* dedicada **por** cliente? ? essa variante (silos) só com **ADR** (motivo forte: compliance, *SLA* de isolamento, etc.) e *runbook* de *ops*. Capacidade de Postgres, não de *vendor* legado. |
| **D2** | Modelo de identidade | **Consola (FR5):** **login base** com **OAuth 2.0 / OIDC**; **login externo** com **SSO** (p.ex. **SAML 2.0** e/ou **OIDC** *enterprise*), *broker* e sessão na **app FastAPI** (ADR: fluxo, *scopes*, *mapping* de atributos). **Embed (FR29):** fluxo **separado** ? **validação de domínio** + **JWT** de curta duração (ou **token opaco** com a mesma política de *origin*); padrão exato e evolução no **ADR Embedded**, se o *baseline* não for a opção *estritamente* preferível. Sem OAuth/SSO *redirect* no *iframe*. **API keys** + webhooks (FR8?FR10); módulo Python de **emisão/validação** de credenciais *embed*. |
| **D3** | Superfície de API | **REST** (HTTP JSON) como contrato principal da API pública e interna; **OpenAPI** como fonte de verdade (FastAPI); **idempotência** em mutações (FR35); **sem GraphQL** no MVP. |
| **D4** | Erros e rastreio | Corpo JSON padronizado + **`X-Request-Id` / correlation id** em 4xx/5xx (FR40, FR51, UX *recibos*). |
| **D5** | Ingestão WhatsApp | Webhooks **verificados**, **anti-replay** / frescura (FR11?FR12); resolução de **tenant** antes de regras (FR13). |

**Importantes (formato da arquitetura):**

| ID | Decisão | Síntese |
|----|---------|---------|
| **D6** | Front admin | **React Router** (rotas lazy, shell + `Outlet` alinhado ao UX), **TanStack Query v5** para estado servidor/cache e reintentos **429**; **Chakra v3** para UI. |
| **D7** | Borda | **Só** **FastAPI** (e *workers* Python, filas, *cron* em processo) como borda HTTP e de negócio; **não** há Edge Deno no *delivery*. |
| **D8** | Observabilidade | Logs estruturados + métricas por rota; correlação **pedido ? evento Meta ? entrega** para suporte N2. |

**Diferidas (pós-MVP / gate explícito):**

| ID | Tema | Racional |
|----|------|----------|
| **X1** | **Dados de brownfield (opcional)** | Se existir *dump* ou repositório antigo, **migração one-time** + validação de *parity*; **não** reintroduzir Supabase/Deno no runtime. |
| **X2** | **SCIM / aprovisionamento de diretórios** | Opcional pós-piloto; *login* coberto por **OAuth (base) + SSO (externo)** antes de automatizar *lifecycle*. |
| **X3** | **GraphQL / BFF dedicado** | Só se REST deixar de escalar em casos de uso reais. |
| **X4** | **Message broker gerido** (Kafka, etc.) | Avaliar se filas em **Postgres** / workers Python deixarem de ser suficientes para backlog e fairness. |

### Data Architecture

**Modelo multitenant (decisão explícita):** O *delivery* alvo é **base partilhada** + **`tenant_id`** + **RLS** para isolamento. **Não** está arquivado como requisito ?**um banco/instância PostgreSQL por organização cliente**?. Se no futuro um **tenant** *enterprise* exigir **silos** de dados (base ou *schema* dedicados), a alteração de modelo é **excecional** e passa por **ADR** (impacto em Alembic, *backup*, *connection pool*, custo) e alinhamento com `platformStack.multitenancy`.

- **Base de dados:** **PostgreSQL** (instância gerida ou *self-hosted*); versão validada com `select version();` por ambiente.
- **Modelagem:** esquema **relacional**; **tenant_id** e **RLS**; documentação em `docs/modular/14-contatos-onboarding-e-rls.md`.
- **Validação nas fronteiras API:** **Pydantic** (v2) + modelos reutilizáveis; *schemas* SQLAlchemy ou tabelas cruas conforme ADR.
- **Migrações:** **Alembic** (ou ferramenta Python acordada) como *fonte* de *schema*; *snapshots* legados de `supabase/migrations/`, se existirem, só como **referência** para mapear para revisões Alembic ? **não** como pipeline de deploy ativo. Nunca editar revisões Alembic já aplicadas.
- **Caching:** **sem** Redis obrigatório no MVP; **cache HTTP** / **TanStack Query** no cliente; *freshness* da inbox (NFR **OBS-fresh**); WebSocket *só* quando o SLO o exigir.
- **Retenção / LGPD:** políticas de retenção e DSAR (FR45?FR50) como **jobs** e estados em Postgres.

### Authentication & Security

#### Superfícies de autenticação (humanos)

| Superfície | Mecanismo |
|------------|-----------|
| **Consola / SPA ? login base** (FR5) | **OAuth 2.0 / OIDC** (IdP da plataforma ou configurado): fluxo no *browser*; **FastAPI** + IdP (ADR: *client*, *PKCE* ou *confidential*, *scopes*). |
| **Consola / SPA ? login externo (SSO)** | **Federation** com IdP do **cliente/tenant** (p.ex. **SAML 2.0** e/ou **OIDC** *enterprise*): *single sign-on* após ligação confiada; *broker* e registo de *session* no mesmo modelo de *backend* que o login base (ADR). Não confundir com o *mecanismo* *embed* (tabela abaixo). |
| **Painel Embedded (iframe)** | **Fora** de OAuth/SSO com *redirect* no *iframe*. *Baseline:* **host** injeta **JWT** de **curta duração** (ou *token* opaco com política análoga) + **validação de domínio** (*Origin* / *Referer*, *allowlist*, claims `aud` / `embed_origin`). **ADR Embedded** (dedicado): fixa padrão e *alternatives* (p.ex. *opaco* *vs* *JWT* ou *rotation*) se forem *estritamente* preferíveis; sem duplicar OAuth/SSO no *iframe*. |

- **Máquinas / integrações:** **API keys** com rotação (FR8); **HMAC** em webhooks na **borda FastAPI** (rota dedicada de ingestão).
- **Autorização:** **RBAC** (FR6?FR7); **RLS** em dados sensíveis; **break-glass** com auditoria (FR53).
- **Segredos:** *Vault* / variáveis de ambiente do runtime (K8s, *platform* *PaaS*, etc.); **não** depender de *secrets* integrados a Supabase.
- **Encriptação:** TLS em trânsito; repouso conforme o *cloud* escolhido.

### API & Communication Patterns

- **Estilo:** **REST** + recursos versionados (FR36?FR37); documentação **OpenAPI** como contrato para integradores e para gerar clientes do admin quando útil.
- **Erros:** formato **estável** com `code`, `message`, `request_id` / `correlation_id`; **401** ? reautenticar; **429** ? `Retry-After` quando disponível (FR40, UX).
- **Idempotência:** chave de idempotência em operações mutáveis ? alinhado a FR35 e às garantias do canal Meta.
- **Webhooks entrada:** validação, deduplicação, ordenação **best-effort** com idempotência por ID de evento (UX jornada integrador).
- **Webhooks saída / notify:** semântica em `docs/modular/13-notify-webhook-semantica-e-riscos.md`; não duplicar garantias que o canal Meta não oferece.

### Frontend Architecture

- **Routing:** **React Router** v6+ com **rotas lazy** (split lista | thread, Drawer para regra/sandbox).
- **Estado servidor:** **TanStack Query (React Query) v5** ? *versão exata: `npm view @tanstack/react-query version` ao adicionar ao projeto* (ecossistema estável em v5 em 2026).
- **Estado local:** mínimo (UI, formulários); **React Hook Form** opcional para formulários longos (UX Comfortable).
- **Componentes:** **Chakra UI v3** + tokens semânticos; **a11y WCAG 2.1 AA** como requisito de implementação.
- **Performance:** code-splitting Vite; **skeleton** e **empty** como estados de sistema (UX); **embed:** `base` configurável e atenção a **bundle** no iframe.
- **Auth no front:** **consola** ? fluxos **OAuth (base)** e **SSO (externo)**; **embed** ? token do *host* (`Authorization: Bearer`); *roteamento* e *feature flags* no mesmo *bundle* (*flag* / *entry*).
- **Chamadas HTTP:** cliente único (*fetch* / *ky*) com *interceptor* para *correlation id* e 401/429; no **embed**, **401** ? renovar JWT via *host* (`postMessage`), sem redirect OAuth. **Validação de domínio** na **API**; o cliente envia o token.

### Infrastructure & Deployment

- **Hosting:** aplicação **FastAPI** (*workers* se necessário) em **contentores** ou VM; **PostgreSQL** gerido ou *self-hosted*.
- **CI/CD:** *lint* (Ruff), *test* (pytest), *build* de imagem; *deploy* separado do *admin* (Vite estático + CDN ou mesmo *origin* ? ADR). Ver `docs/modular/10-rotina-deploy-ci-billing-vault.md`; **não** aplicar *DDL* manual em *prod* fora do processo de revisões.
- **Ambientes:** dev / staging / prod com segredos e *webhooks* Meta distintos; *feature flags* independentes do *host*.
- **Monitorização:** logs estruturados (app + *reverse proxy*); **SLI/SLO** no anexo A do PRD; *métricas* por rota e filas.

### Decision Impact Analysis

**Sequência sugerida de implementação (dependências):**

1. Contratos **tenant + RLS** estáveis ? ingestão e API não vazam dados.
2. **Autenticação** + **API keys** ? *admin* e integradores nos mesmos princípios.
3. **Webhook** + **dispatcher** ? canal fechado ponta a ponta.
4. **REST** + erros + *correlation* ? painel e integrações alinhados.
5. **SPA** *inbox* (lista | thread) + TanStack Query ? **OBS-fresh** na prática.

**Dependências cruzadas:**

- **TanStack Query** depende de **formato de erro** estável (D4) para não mascarar falhas.
- **Embed** depende do **JWT de embed** + **validação de domínio** (D2), **CORS** alinhado às origens permitidas, **base URL** da API; não depender de *cookies* OAuth de terceiros no iframe.
- **Fairness 429** entre *tenants* depende de **filas** e **política** na borda **FastAPI** / *workers*, não só do *front*.

### Advanced Elicitation + Party Mode (passo 4 ? CA)

- **Inversão (Mary):** *E se o painel só lesse eventos já materializados?* ? reforça **pipeline assíncrono** (fila, frescura, *recibos*) *vs.* leitura síncrona do estado Meta; *integrador como cliente principal* ? manter **uma** API REST idempotente (D3), sem BFF só para o *admin* sem ADR.
- **Party Mode ? Sally:** **React Router** *lazy* = *split* + *Drawer*; **TanStack Query** *stale-while-revalidate* = *mesa única* sem *overpromise* quando o canal atrasa.
- **Party Mode ? Winston:** **uma** borda **FastAPI** (*routers* por domínio, *webhook* separado de *dispatcher*); **Postgres** + **RLS**; **sem GraphQL** até prova.
- **Party Mode ? John:** *admin* e integrador no **mesmo** contrato OpenAPI ? SLA e suporte; X1?X4 explícitos *vs.* *scope creep*.

---

## Implementation Patterns & Consistency Rules (passo 5)

*Padrões para **vários agentes** implementarem de forma **compatível** com o stack: **Postgres**, **FastAPI (Python)**, **React + Chakra + TanStack Query**. Foco em **consistência**; desvios ? PR ou ADR de padrões.*

### Pattern Categories Defined

**Pontos críticos de conflito (onde agentes decidem diferente sem regra):** ~**18** áreas cobertas abaixo (naming, formato JSON, `tenant_id`, idempotência, logs, estados de UI, testes, rotas versionadas, *embed* vs OAuth/SSO, etc.).

### Naming Patterns

**Base de dados (PostgreSQL):**

- Tabelas e vistas: **snake_case** plural sem prefixo de schema no nome lógico (`conversations`, `message_templates`), salvo padrão já existente no repo a migrar.
- Colunas: **snake_case** (`tenant_id`, `waba_id`, `created_at`); chaves estrangeiras `<tabela>_id`.
- Índices: `idx_<tabela>_<colunas_curtas>` (ex.: `idx_conversations_tenant_id_updated_at`).

**API HTTP (REST pública e interna):**

- Recursos: **plural** em inglês (`/v1/conversations`, `/v1/integrations/webhooks`).
- **Versionamento** no path: prefixo **`/v1/`**; mudança de *major* ? `/v2` (FR36).
- Parâmetros de rota: `:conversation_id` (documentação OpenAPI) / `{conversation_id}` coerente com gerador.
- **Query string:** `snake_case` (`include_archived`, `page_size`).
- **Cabeçalhos canónicos:** `Authorization`, `X-Request-Id` (ou `X-Correlation-Id` se único no projeto ? **um** nome fixado); **Idempotency-Key** em mutações idempotentes; **não** misturar `Idempotency-Key` e `X-Idempotency-Key`.

**Código Python (FastAPI):**

- Módulos e funções: **snake_case**; classes: **PascalCase**; constantes: **UPPER_SNAKE** (PEP 8).
- Ficheiros: **snake_case** (`webhook_ingest.py`).

**Código TypeScript / React (admin):**

- Componentes e tipos: **PascalCase** (`InboxList.tsx`, `type ConversationRow`).
- Ficheiros de componente: alinhar ao nome do export principal.
- **Hooks:** `use` + **camelCase** do domínio (`useInboxConversations`).
- **Variáveis e funções:** **camelCase**; constantes de config **UPPER_SNAKE** se globais.
- **Rotas (React Router):** segmentos em **kebab-case** no URL (`/inbox`, `/settings/integrations`) coerentes com o menu e com deep links do UX spec.

### Structure Patterns

**Repositório (alvo / evolutivo):**

- **Feature-first** no front: `src/features/<domínio>/` (inbox, rules, settings) com `components/`, `hooks/`, `api/`, `routes.tsx` por feature quando fizer sentido.
- **Partilhado:** `src/shared/` (primitivos Chakra, `lib/http`, formatadores) ? evitar *dump* de utilitários na raiz.
- **Testes front:** ficheiros `*.test.ts` / `*.test.tsx` **co-localizados** ao módulo ou `__tests__/` imediato; **Vitest** como runner (alinhado Vite).
- **Backend Python:** pacotes por domínio (`app/ingestion/`, `app/dispatch/`, `app/api/routers/`) com routers FastAPI agregados em `app/main.py` (ou equivalente); testes em `tests/` espelhando a árvore de módulos.

**Config e ambiente:**

- Nunca commitar segredos; **`.env.example`** (front) e variáveis documentadas; nomes de env em **UPPER_SNAKE** (`API_BASE_URL`, `OAUTH_CLIENT_ID`).

### Format Patterns

**JSON nas APIs (corpo e query):**

- Propriedades: **snake_case** no fio (Pydantic + Postgres + OpenAPI); o cliente TS pode mapear para **camelCase** **só** em memória de UI com *adapter* explícito ? **não** misturar os dois no mesmo objeto sem conversão.
- Datas/hora: **ISO 8601** em string UTC com sufixo `Z` ou offset explícito (`2026-04-17T12:00:00Z`); **nunca** epoch misturado com ISO no mesmo contrato sem campo nomeado.
- **Boolean** JSON: `true` / `false` apenas; **null** para opcional ausente.

**Resposta de sucesso (REST):**

- **Sem** envelope obrigatório `{"data": ...}` a menos que o OpenAPI o fixe em bloco; preferir corpo de recurso **direto** com **códigos HTTP** semânticos; listas com paginação padrão documentada: `{"items": [...], "next_cursor": ...}` (nomes em **snake_case**).

**Resposta de erro (alinhado D4):**

- Corpo mínimo: `{"code": "<string_estável_máquina>", "message": "<humana ou chave de i18n>", "request_id": "<uuid_ou_id>" }`; códigos HTTP conforme semântica (401, 403, 404, 409, 429, 5xx). **Códigos** reutilizáveis para suporte (John) e logs.

**Idempotência:**

- Mutações que exigem idempotência: **header** com nome **único** (ex. `Idempotency-Key`) + documentação; deduplicação no servidor; resposta 409 quando relevante, **não** silenciar duplicado como 200 com efeito diferente.

### Communication Patterns

**Eventos internos (logs, filas, métricas):**

- Nomes de evento: **namespace com pontos** e segmentos estáveis (ex. `whatsapp.message.acked`) ? **uma** taxonomia; evitar `MessageAcked` vs `message_acked` em paralelo.
- Payload: incluir `tenant_id`, `correlation_id`, `occurred_at` (ISO) quando aplicável.
- **Webhooks** de saída: eventos e payloads alinhados a `docs/modular/13-notify-webhook-*`.

**Estado no front (TanStack Query):**

- Chaves de *query* como **listas** estáveis: `['conversations', tenantId, filters]`; invalidação por domínio após mutação; **não** mutar cache à mão fora padrão documentado.
- Ações otimistas só com rollback e toasts de erro alinhados ao `code` do backend.

**Embeds autenticados (domínio + JWT, D2):**

- Nome e transporte do token **fixos** (`Authorization: Bearer`); claims e **validação de domínio** alinhados ao ADR *Embedded*; **nunca** trocar token por *cookie* silencioso no *iframe* como substituto de política explícita.

### Process Patterns

**Erros (UI + API):**

- **Consola:** redirect OAuth / refresh; mensagens de erro a partir de `code` + mapeamento de copy (Sally) ? *stack traces* nunca expostos ao operador.
- **Embed:** 401 ? renovação com **host** (`postMessage`); sem redirect OAuth.

**Carregamento:**

- Padrão UX: **skeleton** em listas densas, **spinner** só em ações curtas; flags `isLoading` / `isFetching` do Query **diferenciadas** onde a inbox precisa *freshness* (OBS-fresh).
- Nomes: `isLoading` para primeira carga, `isRefetching` para segundo plano ? não inventar terceiro sinónimo no mesmo módulo.

**Retries:**

- `429` / rede: respeitar `Retry-After` + *backoff* com *jitter* no cliente HTTP; **sem** *retry* ilimitado.

### Enforcement Guidelines

**Todos os agentes DEVEM:**

1. Respeitar **snake_case** no JSON de API e alinhar o OpenAPI a essa fonte.
2. Propagar **request_id** / **correlation** do erro ao utilizador (onde o UX o permita) e aos logs.
3. Incluir **tenant** em qualquer I/O de dados (header, *claim*, *path* ? o que o contrato fixar) **sem** deduzir só do corpo.
4. Não introduzir **novo** padrão de nomes de tabela, evento ou cabeçalho sem atualizar **este** documento ou ADR.
5. **Backend** = **módulos Python** por domínio; **não** adicionar runtimes alternativos (Deno, Edge) ao *delivery*; *pastas* legadas no repo, se existirem, **read-only** para migração de conceitos, não *extend*.

**Verificação:** lint (Ruff, ESLint), *schema* OpenAPI em CI, *golden tests* de payload de erro; revisão de PR a olhar para esta secção.

### Pattern Examples

**Bom:** `GET /v1/conversations?status=open` com 200, corpo com `items` e `next_cursor` em **snake_case**; 429 com `Retry-After` e `code: "rate_limit"`.

**Mau (anti-padrão):** mesmo endpoint devolver `userId` *camel* num recurso e `user_id` noutro; *retry* a enviar em loop sem ler `429`; *tenant* lido só do corpo em GET; dois nomes de cabeçalho de idempotência; logs sem `request_id`.

### Registo Advanced Elicitation + Party Mode (passo 5 ? CA)

- **Advanced Elicitation (Mary):** conflitos **snake (API/DB) *vs.* camel (TS)**, **versionamento** `/v1` *vs.* *header*, **idempotência** e 200/409, **timezone** e ISO, **query keys** TanStack com `tenant`, **eventos** e **códigos** de erro ? resolvidos pelas regras acima; **JWT de *embed***, **OAuth** (*consola*, login base), **SSO** (*consola*, login externo) como caminhos distintos.
- **Party Mode ? Sally (UX):** *loading* = *skeleton* na inbox *Compact*; erros = `code` ? copy estável; *focus* no *Drawer* e na troca lista|thread.
- **Party Mode ? Winston:** um **OpenAPI**; logs com o mesmo `request_id` que a resposta; **RLS** com política explícita.
- **Party Mode ? John:** `code` de erro estável em tickets; SLI alinhada entre *dashboard* e API; *scope* só com padrão ou ADR.

---

## Project Structure & Boundaries (passo 6)

*Estrutura **física** e **fronteiras** alinhadas ao repositório **open-bsp-api** (brownfield), ao *delivery* **FastAPI + Postgres + SPA** e às regras do passo 5. Árvore **típica** ? não listar ficheiro a ficheiro; o código **novo** vive em **`apps/`**.*

### Complete Project Directory Structure (estado atual + alvo alinhado)

**Entrega principal (alvo):**

```text
open-bsp-api/
??? README.md
??? CLAUDE.md                 # a atualizar se ainda referir Supabase/Deno
??? apps/
?   ??? admin-web/            # Vite + React + Chakra (consola + embed)
?   ?   ??? src/
?   ?   ?   ??? app/          # shell, router, providers
?   ?   ?   ??? features/     # inbox, rules, settings, ?
?   ?   ?   ??? shared/       # http, tokens Chakra, i18n
?   ?   ??? index.html
?   ?   ??? vite.config.ts
?   ??? api/                  # FastAPI
?       ??? app/
?       ?   ??? main.py
?       ?   ??? routers/      # v1, health, webhooks, auth, ?
?       ?   ??? services/
?       ?   ??? models/       # Pydantic (+ ORM se usado)
?       ??? tests/
?       ??? alembic/          # revisões de schema
?       ??? Dockerfile
?       ??? pyproject.toml
??? docs/
?   ??? modular/              # desenho e rotinas
??? _bmad-output/
    ??? planning-artifacts/
        ??? prd.md
        ??? architecture.md
        ??? ux-design-specification.md
```

**Legado (opcional, só referência / migração de dados ou ideias):** pastas `supabase/`, `plugin/` (Deno), etc., se ainda existirem no *clone* ? **sem** novas *features* nem *deploy* como caminho de produto; qualquer lógica útil reimplementa-se em `apps/api/`.

*Regra para agentes:* toda a **borda** e negócio novo em **`apps/api/`** e **`apps/admin-web/`**; **não** adicionar funções Deno/Edge ao pipeline de *release*.

### Architectural Boundaries

**API boundaries (HTTP):**

| Fronteira | Conteúdo |
|-----------|----------|
| **Pública integrador** | `/v1/...` REST versionado; OpenAPI; 401/429/erro padronizado. |
| **Borda da aplicação** | Uma app **FastAPI** com *routers* agregados; **um** CORS, **um** *middleware* de `request_id`, módulos de **OAuth + SSO (consola)** e de **validação *embed* (JWT + domínio, ADR)**. |
| **Webhooks Meta (entrada)** | Router(s) dedicados (ex. `routers/webhooks.py`) ? validação, *tenant*, *dedup*; *dispatch* e regras em *services*; **não** misturar lógica de regra no *handler* HTTP sem ADR. |

**Component boundaries (front, alvo):**

| Zona | Função |
|------|--------|
| **`app/`** | Layout, *Outlet*, *providers* (Query, Chakra, auth consola vs embed). |
| **`features/<x>/`** | Ecrãs, hooks e API client do domínio *x*; **sem** importar de `features/<y>` exceto via `shared/` ou contrato explícito. |
| **`shared/`** | UI genérica, cliente HTTP, formatadores, tipos de erro ? **não** lógica de negócio de um só tenant. |

**Data boundaries:**

| Zona | Função |
|------|--------|
| **Postgres (schemas + RLS)** | Tabelas e políticas RLS alinhadas a `docs/modular/14-*.md`; *revisões* **Alembic** como *fonte*; *dumps* legados só para *bootstrap* de dados. |
| **Sem DB direto no front** | *Admin* só via **API** (REST); exceção (se houver) em ADR. |

**Service boundaries (lógica de canal / agentes):**

- **Ingestão** (webhook) ? **normalização** ? **regras / dispatcher** ? **Meta** ? limites em `docs/modular/02-07`; integrações **MCP** / *agents* em pacotes **próprios** sob a API; **não** acoplar ao mínimo de *inbox* sem *gate* de produto.

### Requirements to Structure Mapping (FR ? local conceitual)

*Síntese por categorias do PRD; *epics* podem mapear 1:1 a `features/*` no *admin* e a `routers/` / `services/` na API.*

| Categoria PRD | Onde vive (FastAPI + SPA) |
|---------------|---------------------------|
| **Org / tenant / WABA (FR1?4)** | `routers/tenants`, `routers/waba` (ou *equivalente*); *admin:* `features/settings` / `organization`. |
| **Identidade / credenciais (FR5?10)** | `apps/api/routers/auth` (OAuth base, *brokers* SSO), `routers/integrations` (API keys); *admin:* `features/settings/integrations` + fluxos **SSO** onde o PRD exigir. |
| **Canal WhatsApp (FR11?16)** | *Routers* e *services* de *webhook*, *dispatcher*, mensagens/templates; tabelas em Postgres. |
| **Inbox / filas / handoff (FR17?21)** | *Services* de conversa / fila; *admin:* `features/inbox` (lista \| thread + *drawer*). |
| **Regras / sandbox / publish (FR22?26)** | Motor de regras (pacote *service*); *admin:* `features/rules` + *drawer* *sandbox*. |
| **Embed B2B2C (FR29?34)** | Mesmo *bundle* *admin* com *entry* *embed*; *API:* validação JWT + domínio (*middleware* ou *router* *embed*). |
| **API pública (FR35?40)** | `apps/api`; OpenAPI gerado; `docs/modular/12-*.md` como narrativa até *doc* 100% derivada. |
| **Medição / billing (FR41?44)** | Tabelas *billing* + *jobs*; *admin* `features/billing` se existir; `docs/modular/10-*.md`. |
| **LGPD (FR45?50)** | *Jobs* e estados em Postgres; *admin* consentimento / DSAR. |
| **Suporte / auditoria (FR51?54)** | *Correlation* + logs; *break-glass* em módulo **isolado** e auditável. |

### Integration Points

**Internos:** *admin* ? **API** (`/v1`) com contratos de erro alinhados; **FastAPI** ? **Postgres** (*driver* *async* / SQLAlchemy conforme ADR).

**Externos:** **Meta** (Graph / WhatsApp), **IdP** (OAuth *login* base, **SSO** *login* externo), *webhooks* de saída (`docs/modular/13-*.md`).

**Fluxo (resumo):** Meta ? *webhook* ? *persistência + fila* ? *regras* ? *resposta* / *dispatcher* ? Meta; *painel* lê via API com *tenant* e auth.

### File Organization (passo 6)

- **Config:** `pyproject.toml` e `apps/api/.env.example`; `vite.config.*` e `.env.example` em `apps/admin-web/`.
- **Testes:** `apps/api/tests` (pytest); `apps/admin-web` com Vitest *co-located*.
- **Documentação:** `docs/modular` + *OpenAPI* (export a partir de FastAPI em CI *opcional*).

### Development Workflow Integration

- **Local:** Postgres (Docker *ou* *dev* *cloud*), `uvicorn app.main:app` + *Vite* em paralelo.
- **CI:** *matrix* ou *jobs* separados: API (Ruff, pytest, *image*) e *admin* (ESLint, Vitest, *build* estático) ? *não* *merge* cego de passos.
- **Deploy:** *contentores* para `apps/api` (ADR); *assets* do *admin* em CDN / *static* *host*.

### Registo Advanced Elicitation + Party Mode (passo 6 ? CA)

- **Advanced Elicitation (Mary):** *fronteiras* **ingestão / dispatcher / management / integrações**; regra **não** pôr lógica de regra no *handler* de webhook ? *services*; **monorepo** `apps/*` preferido para um contrato e PRs *full-stack* estáveis.
- **Party Mode ? Sally (UX):** `features/inbox` agrega lista+thread+*estados de sistema*; *embed* como *route* ou *query* no mesmo *app*, não segundo repositório sem ADR.
- **Party Mode ? Winston:** *routers* finos + *services* gordos; **MCP** / *agent* isolado do SLA mínimo do canal WhatsApp.
- **Party Mode ? John (PM):** *feature flags* mapeáveis a módulos; suporte a localizar *incidentes* por `request_id` e `tenant_id` nos logs.

---

## Architecture Validation & Completion (passo 7)

*Validação de coerência, cobertura de requisitos e prontidão para implementação por agentes; alinhada a `step-07-validation.md` (BMAD). O passo 7 integrou **Advanced Elicitation (AE)** e **Party Mode (PM)** antes do encerramento documental.*

### Coherence Validation

**Compatibilidade de decisões:** O **`platformStack`** (FastAPI + PostgreSQL, sem Supabase/Deno), **`D1`?`D8`**, `X1`?`X4` e a árvore `apps/api` + `apps/admin-web` são **coerentes**: a borda é só Python; RLS e *tenant* vêm do modelo de dados; **OAuth (base)**, **SSO (externo)** e **embed** (JWT + domínio) estão **separados** e descritos em **D2** e tabelas, sem *redirect* OAuth/SSO no *iframe*.

**Consistência de padrões:** *Naming* (snake JSON ? DB, convenções de rotas), *enforcement* e *Embeds* alinham-se a **D3** e **D4**; *TanStack Query* e erros estáveis reforçam o mesmo contrato *front* / API.

**Alinhamento estrutural:** `apps/*`, fronteiras de *router* *vs* *service* e mapeamento FR ? pastas suportam as decisões de **passo 6** sem exigir um segundo *runtime* na entrega.

### Requirements Coverage Validation

**Cobertura por categorias (PRD):** As linhas de **Requirements to Structure Mapping** (passo 6) e a síntese **passo 2** cobrem org/tenant, identidade (OAuth, SSO, API keys, embed), canal WhatsApp, inbox, regras, *embed* B2B2C, API pública, *billing*, LGPD, suporte; lacunas *funcionais* conhecidas ficam em **X2**?**X4** (SCIM, GraphQL, *broker* gerido) com *gate* explícito.

**NFRs:** *Observabilidade* (**D8**, *correlation*), *fairness* 429, RLS, SLI/SLO no PRD e **LGPD** têm *hooks* em dados, borda e padrões de erro; pormenor de carga/CA *stress* **não** substitui ADRs operacionais quando o piloto apertar *SLO*.

### Implementation Readiness Validation

**Decisões documentadas:** *Stack* e *auth* no frontmatter; *critical path* em **D1**?**D2**; versões a validar com `npm view` / `pyproject` em vez de *pin* cego no spec.

**Estrutura e integrações:** Monorepo `apps/*`, Postgres, Meta, IdP; documentação viva em `docs/modular/` + OpenAPI a gerar a partir do FastAPI.

**Padrões:** *Checklist* do **passo 5** (naming, erros, *tenant*, *embed*); exemplos *bom* / *mau* para *review* de PR.

### Gap Analysis

| Prioridade | Lacuna / nota | Mitigação |
|------------|---------------|------------|
| **Crítica** | Nenhum bloqueio estrutural identificado *nesta* validação, desde que **ADR** *Embedded* e fluxos **SSO** *broker* fiquem escritos **antes** de *stories* de *auth* *enterprise* | *Gate* de *epic*: ADR aprovado |
| **Importante** | Reconciliar **histórico** `supabase/migrations` *vs* **Alembic** sem *drift* de *schema* em ambientes *brownfield* | *Runbook* de migração *one-time* + uma *fonte* de verdade (Alembic) |
| **Importante** | **OpenAPI** exportado/validado em CI (contrato = FastAPI) | *Job* CI com `openapi.json` (ou *lint* *spectral* quando existir) |
| **Desejável** | Testes *e2e* consola + *embed* + integrador; *load* e *chaos* além do MVP | *Backlog* pós-fecho de *MVP* |

### Validation Issues Addressed (durante o passo 7)

- **Coerência *auth*:** Confirmado: **login base (OAuth)**, **login externo (SSO)** e **embed** (JWT + domínio) permanecem **três** superfícies, com **SSO** na consola e **sem** *redirect* *OAuth*/*SSO* no *iframe* (*AE* reforçou o *happy path* e o *degrade*; *PM* alinhou mensagens de erro e *support*).
- **Borda única (FastAPI):** Reafirmada exclusão de Deno/Supabase na entrega; legado *read-only* para conceitos, não *extend*.

### Architecture Completeness Checklist (passo 7)

**Análise de requisitos**

- [x] Contexto e complexidade
- [x] Restrições técnicas e `platformStack`
- [x] Preocupações *cross-cutting* (tenancy, *observability*, *auth*)

**Decisões arquitetónicas**

- [x] Decisões críticas e *deferidas* (*X1*?*X4*)
- [x] *Stack* e integrações (Meta, IdP, API pública)
- [x] *Performance* / *fairness* na borda (sem números *hardcoded* no spec)

**Padrões de implementação**

- [x] *Naming* e formatação (JSON, DB, API)
- [x] *Structure* e *format* *patterns*
- [x] Erros, *idempotency*, *embed*, *enforcement*

**Estrutura do projeto**

- [x] Árvore *alvo* `apps/*`
- [x] Fronteiras e mapeamento FR
- [x] Pontos de integração explícitos

### Architecture Readiness Assessment

**Estado geral:** **PRONTO PARA IMPLEMENTAÇÃO** (com *gates*: ADR *Embedded*, ADR *SSO* *broker* conforme complexidade do tenant *piloto*).

**Confiança:** **Alta** na *stack* e nos padrões; **média-alta** no *first* *cut* de *SSO* *enterprise* até existir *matrix* de IdPs testada.

**Forças:** Um contrato OpenAPI; *multitenancy* + RLS explícitos; *embed* e consola *desacoplados*; *docs/modular* como *backbone* de domínio.

**Evolução futura:** SCIM; *GraphQL*; *Kafka*; *hardening* *SLO* e *DR*; *golden* *paths* *e2e*.

### Implementation Handoff

**Para agentes de implementação:** Seguir `platformStack`, **D1**?**D2** (incl. **OAuth** / **SSO** / *embed*), padrões do **passo 5** e a árvore do **passo 6**; *PRs* que introduzam *novo* padrão de nomes ou de *auth* **atualizam** este ficheiro ou um **ADR** ligado.

**Prioridade de arranque sugerida:** (1) *schema* *tenant* + RLS mínima + *health*; (2) *router* *auth* (OAuth base) + sessão; (3) *webhook* Meta + *dispatcher* *stub*; (4) *admin* *shell* + *OpenAPI* *client* gerado ou *handwritten* *aligned*; (5) *embed* + ADR; (6) **SSO** conforme *roadmap* do PRD *piloto*.

### Registo Advanced Elicitation + Party Mode (passo 7 ? CA)

- **Advanced Elicitation (Mary):** *Stress* ?e se??? na validação: **SSO** *IdP* indisponível *mid-session* ? sessão e *re-auth* na consola sem corromper API keys; **JWT** *embed* a expirar com *drawer* / *sandbox* abertos ? *refresh* via *host* (`postMessage`); **429** Meta *vs* **429** plataforma ? taxonomia de `code`; *migração* *dump* *brownfield* ? *parity checklist*. Síntese: *gaps* críticos fechados no desenho; *importantes* na tabela *Gap Analysis* (passo 7).
- **Party Mode ? Sally (UX):** mesmo vocabulário máquina (`code`) na consola (OAuth, SSO) e no *embed*; não confundir falha de IdP com *bug* interno; a11y pós-SSO.
- **Party Mode ? Winston (eng.):** RLS *vs* *claims*; um OpenAPI; *SSO* (SAML/OIDC) com o mesmo `request_id` / observabilidade que a API pública.
- **Party Mode ? John (PM):** piloto e suporte partilham o mesmo contrato; Alembic *vs* legado e OpenAPI em CI no *sprint* zero; SCIM depois de OAuth, SSO e **embed** estáveis.

---

## Architecture Completion & Handoff (passo 8)

*Última etapa do workflow* `bmad-create-architecture` (*step-08-complete*). Integrou **Advanced Elicitation (AE)** e **Party Mode (PM)** para fechar *guardrails* e *next steps* após a validação (passo 7).*

### Conclusão do *workflow* de arquitetura

O **CA** (*Architecture Decision Document*) do projeto **open-bsp-api** está **completo** nos passos 1 a 8: contexto, *starter* e restrições, decisões **D1**?**D8** e **X1**?**X4**, padrões de implementação, estrutura `apps/*`, **validação** (passo 7) e este **encerramento** (passo 8). O documento é a **fonte de decisão** para agentes e equipa alinhada a **FastAPI + PostgreSQL**, consola com **OAuth (base) + SSO (externo)** e **embed** (JWT + domínio, ADR *Embedded*), com **Deno/Supabase** fora do *delivery*.

### Próximos passos (implementação e produto)

1. **Arranque técnico:** criar/actualizar `apps/api` (FastAPI) e `apps/admin-web` (Vite) conforme o *tree* do passo 6; *health* + *schema* *tenant* + RLS; *router* *auth* (OAuth); *webhook* Meta *stub*; depois *embed* + **ADR**, e **SSO** segundo o PRD *piloto*.
2. **ADRs em aberto (gates):** *Embedded*; *SSO* *broker* (SAML/OIDC) quando o primeiro tenant *enterprise* *exigir*; reconciliação **Alembic** *vs* histórico se existir *brownfield*.
3. **CI:** *lint* (Ruff, ESLint), *test* (pytest, Vitest), *build*; **export** `openapi.json` a partir do FastAPI e/ou *lint* *contract* (quando existir política de *breaking changes*).
4. **Comunidade BMAD:** após o encerramento deste ficheiro, podes invocar o skill **`bmad-help`** no Cursor para *routing* a outras tarefas (PRD, *stories*, *dev*, *review*) ou dúvidas sobre este **CA**.
5. **Dúvidas:** qualquer questão sobre secções, **D2**, *embed*, ou limites *FastAPI* / *legado* pode ser resolvida com base neste documento e em `docs/modular/`.

### Registo Advanced Elicitation + Party Mode (passo 8 ? CA)

- **Advanced Elicitation (Mary):** pós-conclusão ? *e se* o repositório ainda tiver *código* legado (Deno) e *novos* *commits* a tocar nesse caminho? Regra: *read-only*; *cherry-pick* de lógica só vira PR em `apps/api`. *E se* dois ADRs (*Embedded* e *SSO*) entrarem em conflito de *scope*? Prioridade: segurança de dados *tenant* e *audit trail*; mediação num ADR *umbrella* de *auth*.
- **Party Mode ? Sally (UX):** o CA não substitui o **UX spec**; alterações de *copy* / *tokens* *embed* *vs* consola mantêm a disciplina *code* + *i18n*; não mudar sem actualizar padrão de erros (D4).
- **Party Mode ? Winston (eng.):** uso do CA na implementação: `platformStack` + *patterns*; evitar *parallel stacks*; *versionar* a API em `/v1` antes de *breaking changes* visíveis para integradores.
- **Party Mode ? John (PM):** *roadmap* do *piloto* ancorado em *FR* + este CA; *stakeholder* lê *readiness* (passo 7) e *próximos passos* (passo 8); compromisso com SCIM/GraphQL só reabre o CA ou ADR, sem *scope creep* silencioso.

---

*Fim do workflow de arquitetura (passos 1?8). **Estado (frontmatter):** `status: complete`, `lastStep: 8`.*
