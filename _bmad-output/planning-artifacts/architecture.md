---
stepsCompleted:
  - step-01-init.md
  - step-02-context.md
  - step-03-starter.md
  - step-04-decisions.md
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
runtimeTransition:
  status: "Supabase (Postgres gerido + Auth + Edge Functions/Deno) é legado e será removido; a plataforma alvo é Python (FastAPI) + PostgreSQL + OAuth/OIDC, sem dependência do produto Supabase."
  implication: "Novas decisões e implementações devem convergir para o stack Python; o que hoje vive em Edge/Deno e em APIs específicas do Supabase deve ser planeado como temporário até migração."
  authSurfaces: "OAuth/OIDC na consola SPA. No iframe Embedded: auth à parte (tipo analytics), tipicamente JWT de curta duração assinado pela plataforma, com validação de domínio (allowlist de origens permitidas por tenant e/ou claims no token, ex. embed_origin / aud), injetado pelo host; sem OAuth completo dentro do iframe."
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
| **Identidade e credenciais** | OAuth/OIDC na consola (FR5); **embed**: JWT + validação de domínio (ver D2); RBAC (FR6?FR7); API keys e webhooks (FR8?FR10). |
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

- **Transição de plataforma:** **Supabase (Auth, Edge/Deno, Postgres hospedado)** é **legado** e **será removido**; o **alvo** é **Python (FastAPI) + PostgreSQL + OAuth/OIDC** sem dependência do produto Supabase ? ver `runtimeTransition` no frontmatter e passos 3?4 deste documento.
- **Brownfield:** migração para stack alvo com paridade (**MIG-parity**); a UI não promete paridade visual antes dos gates ? a arquitetura deve manter **dois runtimes** ou fases até cutover, conforme docs modulares.
- **Meta como dependência:** indisponibilidade, 429, política de templates ? **fairness entre tenants** e mensagens **honestas** (UX + NFR); não assumir canal sempre saudável.
- **Embed:** **auth distinta da consola OAuth** ? **JWT** de embed + **validação de domínio** (allowlist por tenant, claims); injeção pelo host (query/`postMessage`); sem OAuth redirect no iframe (pendentes PRD: SSO enterprise só na consola).
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

*Avaliação alinhada ao **repositório real** (`open-bsp-api`), ao README e ao **UX spec** (React + Chakra, SPA + embed). **Transição:** **Supabase será removido**; a linha de chegada é **Python (FastAPI) + PostgreSQL + OAuth** ? o que está em **Deno + Supabase** é **legado operacional** até cutover, não arquitetura alvo. **Versões npm:** confirmar no scaffold com `npm view <pacote> version`; não fixar números sem verificação local.*

### Primary Technology Domain

| Camada | Domínio |
|--------|---------|
| **Borda e dados (hoje, legado)** | **Supabase Edge Functions (Deno)** + Postgres + webhooks ? materializado em `supabase/functions/*`, `config.toml`, schemas; **a substituir** por serviços **Python**. |
| **Borda e dados (alvo)** | **FastAPI** (HTTP API, webhooks, workers/async conforme necessidade), **PostgreSQL** (instância própria ou gerida **sem** Supabase), **OAuth/OIDC**; sem runtime Supabase na plataforma. |
| **Painel (UX spec)** | **SPA React** + **Chakra UI** + TypeScript; embutível em **iframe**; futuro **Capacitor** ? **independente** do backend ser Deno ou Python desde que o contrato REST seja estável. |

Conclusão: há **baseline front** (Vite+Chakra) e **dois momentos de backend**: (1) **interino** ? repo atual Supabase/Deno; (2) **alvo** ? Python; o trabalho de arquitetura deve **anti-acoplar** o admin às APIs do Supabase (Auth REST proprietário, etc.) para reduzir custo da remoção.

### Starter Options Considered

| Opção | O que estabelece | Prós | Contras / riscos |
|-------|------------------|------|------------------|
| **A ? Baseline repo atual (Supabase + Deno), legado** | Funções no `config.toml`, `deno.json` (Hono, Zod, etc.) | Permite operar até migração | **Será descontinuado**; não investir em padrões que não portem para FastAPI. |
| **B ? Vite + React + TS + Chakra UI v3** | SPA moderna, HMR, code-splitting, bundle adequado a **embed** | Bate com UX spec (Chakra, tokens, a11y); documentação Chakra oficial para **Vite** | Versões a fixar no `package.json` no init; migração v2?v3 Chakra se houver código legado. |
| **C ? Next.js App Router** | SSR/SSG, rotas por ficheiro | Útil se SEO/marketing forem centrais | **Embed** e cookies terceiros mais complexos; UX prioriza **SPA** e iframe ? **não recomendado** como default do piloto admin. |
| **D ? T3 / tRPC / full-stack monolith** | End-to-end types | Produtividade em greenfield | API pública e edge já têm contratos próprios; acoplamento desnecessário ao roadmap **open-bsp-api**. |
| **E ? Companion OpenBSP UI (React + Tailwind)** | UI existente noutro repositório (README) | Referência de produto | **Desalinhado** ao UX spec atual (**Chakra**); integrar só por **padrões de API**, não como stack de componentes do piloto Chakra. |

**Advanced Elicitation (Mary) ? alternativas não óbvias:** (1) **Monorepo** (`apps/admin`, `packages/ui`) vs repo admin separado ? trade-off CI e releases vs simplicidade; (2) **Storybook** no arranque ? útil para design system Chakra (Sally), custo de manutenção; (3) **TanStack Router** em vez de React Router ? ganho de tipos em rotas grandes; não obrigatório no MVP.

### Selected Starter(s)

**1) Borda / dados ? interino (Supabase + Deno), em vias de substituição por Python**

- **Estado atual:** repositório **open-bsp-api** + **Supabase CLI** para dev local (`supabase start`, `supabase functions serve`, migrações) ? válido **até remoção do Supabase**.
- **Alvo:** serviços **FastAPI** (e workers Python se necessário) com os mesmos contratos de negócio; **Postgres** fora do ecossistema Supabase quando a plataforma migrar.
- **Racional:** preservar continuidade operacional enquanto se implementa paridade (**MIG-parity**) e se migra autenticação, webhooks e jobs para Python.

**Inicialização local (legado ? referência Supabase):**

```bash
# Válido durante a fase Supabase; revisar quando o backend Python for a única borda.
supabase start
supabase functions serve --env-file supabase/.env.local
```

**Decisões já presentes (a reimplementar em Python no cutover):** funções por domínio, validação na borda; **evitar** dependência forte de APIs exclusivas do Supabase no front (preferir contratos REST/OpenAPI estáveis).

**2) Painel admin / embed ? Vite + React + TypeScript + Chakra UI**

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

- **Borda legado:** TypeScript sob **Deno** (Edge Supabase) ? **substituível** por **Python 3.x + FastAPI** na arquitetura alvo.
- **Borda alvo:** **FastAPI** (rotas REST, dependências tipadas, OpenAPI nativo); tarefas assíncronas/cron conforme necessidade (filas internas, Celery/RQ, etc. ? ADR quando fechar).
- **Admin:** **TypeScript** estrito no front; alvo **ESM** (Vite).

**Styling / UI**

- **Chakra UI v3** + tokens semânticos (spec UX); sem Tailwind como base do design system **deste** painel (diferente do companion Tailwind, se coexistir).

**Build e tooling**

- **Vite:** dev server rápido, code splitting alinhado a rotas lazy (shell + inbox).
- **Backend interino:** deploy Edge via Supabase; **backend alvo:** imagens **container** (ou equivalente) com app Python ? pipeline CI a atualizar no cutover (ver `docs/modular/10-*`).

**Testes**

- Front: **Vitest** + **Testing Library** (combinação usual com Vite ? adotar no primeiro epic de qualidade).
- Edge: testes por função / integração conforme prática do repo.

**Organização de código**

- **Backend:** de **funções Edge** para **módulos/serviços Python** (ou monólito modular FastAPI) ? o desenho por domínio (webhook, dispatcher, ?) mantém-se; **SPA** em árvore por features com **layout estável** + `Outlet` (UX).

**Estado e dados**

- Cliente: estado de UI + **React Query (TanStack Query)** ou equivalente para cache de API (decisão fina no passo 4/5 se necessário).
- Servidor: Postgres + RLS; padrões em `docs/modular/14-contatos-onboarding-e-rls.md` etc.

### Flow Optimization Principles (starter)

- **Menos surpresas entre repos:** contratos OpenAPI/REST estáveis entre **SPA** e **edge** antes de bibliotecas full-stack mágicas.
- **Embed primeiro:** build Vite com `base` configurável se o admin for servido fora do origin da API.
- **Observabilidade desde o primeiro PR:** correlation id nos clientes HTTP do painel alinhado a FR51 e UX ?recibos?.

### Advanced Elicitation + Party Mode (passo 3 ? CA)

- **Exploração de alternativas (Mary):** **Vite+Chakra** permanece o starter **front**; **Supabase+Deno** é aceite só como **ponte** até **FastAPI** ? qualquer feature nova deve antecipar o contrato HTTP final em Python.
- **Party Mode ? Sally:** o painel não deve depender do **Supabase Dashboard** nem de SDKs exclusivos no browser; **REST** estável; **OAuth** na consola; **embed** com mecanismo tipo analytics (ver `authSurfaces`).
- **Party Mode ? Winston:** **FastAPI + OpenAPI** como alvo facilita **um** contrato para admin e integradores; Edge Deno sai sem reescrever o modelo mental por domínio.
- **Party Mode ? John:** roadmap explícito **remover Supabase** evita débito de licença e de lock-in; métricas de piloto sobre APIs **neutras** em relação ao host.

---

## Core Architectural Decisions (passo 4)

*Decisões registadas após **Advanced Elicitation** e **Party Mode**. **Transição:** **Supabase será removido** da plataforma; o **estado alvo** é **Python (FastAPI) + PostgreSQL** (instância própria ou gerida **sem** produto Supabase). **Auth:** **OAuth/OIDC** na **consola SPA**; **iframe Embedded** com **JWT** (preferido) + **validação de domínio** (allowlist/claims), sem OAuth completo no iframe ? ver `authSurfaces`. O stack **Supabase** trata-se como **legado** até cutover. **Versões:** `npm view` para front; **Postgres** com `select version();` no ambiente alvo; **Python/FastAPI** no `pyproject` ou equivalente.*

### Decision Priority Analysis

**Críticas (bloqueiam implementação coerente):**

| ID | Decisão | Síntese |
|----|---------|---------|
| **D1** | Fonte de verdade dos dados | **PostgreSQL** (persistência alvo **sem** dependência Supabase); **RLS** por tenant onde aplicável (`docs/modular/14-*`) ? feature Postgres, não do vendor. |
| **D2** | Modelo de identidade | **OAuth/OIDC** na **consola web** (FR5). **iframe Embedded** (FR29): fluxo **distinto** ? **JWT** (preferido) ou token opaco, **curto**, assinado pela plataforma, com **validação de domínio**: *allowlist* de **origens** (domínios do site anfitrião) por tenant e/ou **claims** no JWT (`aud`, `embed_origin`, etc.); injeção pelo **host** (query/`postMessage`); sem OAuth redirect no iframe. **API keys** + webhooks (FR8?FR10). **Interino:** Supabase Auth na consola; **alvo:** OAuth/OIDC + **emisão/validação de JWT de embed** em **Python** (ADR). |
| **D3** | Superfície de API | **REST** (HTTP JSON) como contrato principal da API pública e interna; **OpenAPI** como fonte de verdade (natural em **FastAPI**); **idempotência** em mutações (FR35); **sem GraphQL** no MVP (complexidade vs equipa). |
| **D4** | Erros e rastreio | Corpo JSON padronizado + **`X-Request-Id` / correlation id** em 4xx/5xx (FR40, FR51, UX ?recibos?). |
| **D5** | Ingestão WhatsApp | Webhooks **verificados**, **anti-replay** / frescura (FR11?FR12); resolução de **tenant** antes de regras (FR13). |

**Importantes (formato da arquitetura):**

| ID | Decisão | Síntese |
|----|---------|---------|
| **D6** | Front admin | **React Router** (rotas lazy, shell + `Outlet` alinhado ao UX), **TanStack Query v5** para estado servidor/cache e reintentos **429**; **Chakra v3** para UI. |
| **D7** | Borda | **Interino:** **Supabase Edge (Deno)** conforme `config.toml`. **Alvo:** **FastAPI** (e workers Python conforme necessidade) como única borda de negócio; **Supabase removido** após paridade e migração de dados/auth. |
| **D8** | Observabilidade | Logs estruturados + métricas por rota; correlação **pedido ? evento Meta ? entrega** para suporte N2. |

**Diferidas (pós-MVP / gate explícito):**

| ID | Tema | Racional |
|----|------|----------|
| **X1** | **Cutover Supabase ? Python** | Migração explícita: Edge/Deno e dependências Supabase **desligadas** após **MIG-parity**; Postgres e RLS **preservados** na instância alvo. |
| **X2** | **SSO enterprise (SAML)** vs OAuth tenant | Pendente PRD; UI não assume fluxo único. |
| **X3** | **GraphQL / BFF dedicado** | Só se REST deixar de escalar em casos de uso reais. |
| **X4** | **Message broker gerido** (Kafka, etc.) | Avaliar se filas em **Postgres** / workers Python deixarem de ser suficientes para backlog e fairness. |

### Data Architecture

- **Base de dados:** **PostgreSQL** ? **alvo:** instância **independente do Supabase** (versão validada por ambiente com `select version();`).
- **Modelagem:** esquema **relacional**; **tenant_id** e **RLS**; documentação em `docs/modular/14-contatos-onboarding-e-rls.md`.
- **Validação:** **Interino:** Zod nas fronteiras Deno; **alvo:** **Pydantic** (v2) em FastAPI nas mesmas fronteiras ? manter equivalência de regras.
- **Migrações:** **Enquanto Supabase existir:** fluxo `supabase/schemas/` + migrações geradas (nunca editar migrações aplicadas ? `CLAUDE.md`). **Após cutover:** **Alembic** (ou ferramenta Python acordada) como fonte de migrações; plano de transição documentado no ADR de migração.
- **Caching:** **sem** camada Redis obrigatória no MVP; **cache HTTP** / **TanStack Query** no cliente para leituras; **freshness** da inbox guiada por NFR **OBS-fresh** (revalidação e/ou *polling* inteligente ? detalhe de transporte WebSocket fica para quando o SLO exigir).
- **Retenção / LGPD:** políticas de retenção e DSAR (FR45?FR50) como **jobs** e estados em Postgres, não como decisão de ?starter?.

### Authentication & Security

#### Superfícies de autenticação (humanos)

| Superfície | Mecanismo |
|------------|-----------|
| **Consola / SPA** (domínio da plataforma) | **OAuth 2.0 / OIDC** ? fluxo completo no browser (FR5). **Interino:** Supabase Auth; **alvo:** app **Python** + IdP (ADR). |
| **Painel Embedded (iframe)** | **Fora** do OAuth da consola. Modelo tipo **analytics**: o **host** injeta no iframe um **JWT** (recomendado) ou token opaco ? **curta duração**, claims de **escopo** (tenant, WABA, papel). O **backend** valida assinatura, `exp`, e **domínio**: cruzar **origem** do pedido (`Origin` / `Referer` onde aplicável) e/ou claims (`aud`, `embed_origin`) com **domínios autorizados** configurados no tenant. **Token opaco** exige validação servidor + mesma política de domínio. Sem OAuth redirect no iframe; sem cookies third-party como única base. Rotação, revogação, CSRF do embed no **ADR**. |

- **Máquinas / integrações:** **API keys** com rotação e coexistência (FR8); **HMAC / segredo** em webhooks na borda (**Deno interino** ou **FastAPI alvo**).
- **Autorização:** **RBAC** no produto (FR6?FR7); **RLS** em dados sensíveis; **break-glass** com auditoria (FR53).
- **Segredos:** **Vault / env** por ambiente (durante Supabase: secrets da plataforma; **alvo:** secrets do runtime Python/K8s ou equivalente).
- **Encriptação:** TLS em trânsito; repouso conforme política do **cloud/hosting** escolhido pós-Supabase.

### API & Communication Patterns

- **Estilo:** **REST** + recursos versionados (FR36?FR37); documentação **OpenAPI** como contrato para integradores e para gerar clientes do admin quando útil.
- **Erros:** formato **estável** com `code`, `message`, `request_id` / `correlation_id`; **401** ? reautenticar; **429** ? `Retry-After` quando disponível (FR40, UX).
- **Idempotência:** chave de idempotência em operações mutáveis (envio, certas configurações) ? alinhado a FR35 e a filas Meta.
- **Webhooks entrada:** validação, deduplicação, ordenação **best-effort** com idempotência por ID de evento (UX jornada integrador).
- **Webhooks saída / notify:** semântica em `docs/modular/13-notify-webhook-semantica-e-riscos.md`; não duplicar garantias que o canal Meta não oferece.

### Frontend Architecture

- **Routing:** **React Router** v6+ com **rotas lazy** (split lista | thread, Drawer para regra/sandbox).
- **Estado servidor:** **TanStack Query (React Query) v5** ? *versão exata: `npm view @tanstack/react-query version` ao adicionar ao projeto* (ecossistema estável em v5 em 2026).
- **Estado local:** mínimo (UI, formulários); **React Hook Form** opcional para formulários longos (UX Comfortable).
- **Componentes:** **Chakra UI v3** + tokens semânticos; **a11y WCAG 2.1 AA** como requisito de implementação.
- **Performance:** code-splitting Vite; **skeleton** e **empty** como estados de sistema (UX); **embed:** `base` configurável e atenção a **bundle** no iframe.
- **Auth no front:** ramo **consola** ? **OAuth/OIDC**; ramo **embed** ? **JWT** (ou token opaco) do host + **`Authorization: Bearer`** nas APIs; **dois caminhos** no mesmo bundle (flag ou entry).
- **Chamadas HTTP:** cliente único (fetch/ky) com **interceptor** para **correlation id** e **401/429**; no embed, **401** ? renovar JWT via host (`postMessage`), nunca redirect OAuth. A **validação de domínio** (allowlist / claims) é feita na **API**; o cliente só envia o token.

### Infrastructure & Deployment

- **Hosting (interino):** **Supabase** (Postgres + Auth + Edge) ? **a descontinuar**.
- **Hosting (alvo):** **FastAPI** (e workers) em **contentores** ou VM, com **PostgreSQL** gerido ou self-hosted; **sem** serviços proprietários Supabase no caminho crítico.
- **Cutover:** ADR dedicado + **MIG-parity** antes de desligar Supabase; rollback documentado.
- **CI/CD:** atualizar pipelines para **build/test/deploy Python** no alvo; enquanto houver Edge, manter deploy atual; ver `docs/modular/10-rotina-deploy-ci-billing-vault.md`; **não aplicar migrações manualmente em produção** (`CLAUDE.md`).
- **Ambientes:** dev / staging / prod com segredos e webhooks Meta distintos; feature flags (ex. terceira coluna inbox) independentes do host.
- **Monitorização:** **interino:** logs Edge (`CLAUDE.md`); **alvo:** logs estruturados da app Python + reverse proxy; **SLI/SLO** no Anexo A do PRD.

### Decision Impact Analysis

**Sequência sugerida de implementação (dependências):**

1. Contratos **tenant + RLS** estáveis ? ingestão e API não vazam dados.
2. **Autenticação** + **API keys** ? admin e integradores nos mesmos princípios.
3. **Webhook pipeline** + **dispatcher** ? canal fechado ponta a ponta.
4. **REST + erros + correlation** ? painel e integrações com o mesmo comportamento observável.
5. **SPA inbox** (lista | thread) + TanStack Query ? **OBS-fresh** na prática.

**Dependências cruzadas:**

- **TanStack Query** depende de **formato de erro** estável (D4) para não mascarar falhas.
- **Embed** depende do **JWT de embed** + **validação de domínio** (D2), **CORS** alinhado às origens permitidas, **base URL** da API; não depender de cookies OAuth de terceiros no iframe.
- **Fairness 429** entre tenants depende de **filas** e **política** na **borda** (Edge interino ou FastAPI alvo), não só do front.

### Advanced Elicitation + Party Mode (passo 4 ? CA)

- **Inversão de pressupostos (Mary):** *E se o painel só lesse eventos já materializados?* ? reforça **pipeline assíncrono** (fila, frescura, ?recibos?) em vez de assumir leitura síncrona perfeita do estado Meta; *e se o integrador fosse o cliente principal?* ? mantém **uma** API REST idempotente e documentada (D3), evitando BFF só para o admin.
- **Party Mode ? Sally:** **React Router** + **lazy** entrega o **split** e o **Drawer** sem recarregar o mundo; **TanStack Query** com **stale-while-revalidate** encaixa na sensação de ?mesa única? sem mentir quando o canal atrasa.
- **Party Mode ? Winston:** fronteira única de escrita para Meta **hoje** no Edge **Deno**, **amanhã** em **FastAPI/workers Python** ? o desenho por **rotina de domínio** mantém-se; **Postgres** + **RLS** permanecem; **sem GraphQL** até prova de necessidade.
- **Party Mode ? John:** admin e integrador no **mesmo contrato** simplifica **SLA**, suporte e narrativa de piloto; features **diferidas** (X1?X4) ficam explícitas para não **scope creep** no MVP.

---

<!-- Further architecture workflow steps append below -->
