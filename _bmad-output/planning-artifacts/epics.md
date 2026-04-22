---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/planning-artifacts/prd-decisoes-registradas-gd-agk.md
workflowNote: "Workflow bmad-create-epics-and-stories concluído em 2026-04-17; requisitos alinhados ao PRD, CA e UX spec."
---

# open-bsp-api ? Épicos e histórias

## Overview

Este documento decompõe o [PRD](prd.md), o [CDA (arquitetura)](architecture.md) e a [especificação UX](ux-design-specification.md) em épicos orientados a valor e histórias implementáveis com critérios de aceitação. **Fase 2 (agente, FR27) e Fase 3 (orquestrador, FR28)** ficam fora do núcleo MVP, com referência no inventário. O **Contexto B2B2C (LGPD no canal)**, a **migração legado ? stack alvo (MIG-parity)** e a **observabilidade (SLI/SLO)** são transversais e aparecem onde sustentam histórias de produto, não como épicos «só técnicos» desligados de utilizador.

## Requirements Inventory

### Functional Requirements

```
FR1: Administrador do tenant pode registar e gerir perfil e definições da organização.
FR2: Administrador do tenant pode associar e gerir uma ou mais contas comerciais WhatsApp (WABA) e números sob a organização, com estado operacional visível (ativo, pendente, suspenso, etc.).
FR3: A plataforma pode impor isolamento de dados por tenant em todas as áreas operacionais expostas a utilizadores e integrações.
FR4: Administrador do tenant pode utilizar ambientes distintos (ex.: desenvolvimento / staging / produção) quando o produto os expuser, sem misturar dados entre ambientes.
FR5: Utilizadores podem autenticar-se através de fluxos OAuth/OIDC suportados pelo produto.
FR6: Administrador do tenant pode atribuir papéis e permissões a utilizadores com princípio de menor privilégio.
FR7: Utilizadores só podem aceder a recursos permitidos pelo seu papel dentro da sua organização.
FR8: Operador autorizado pode rodar credenciais de API (criar novas, revogar antigas) com período de coexistência controlado para migração de integrações.
FR9: Operador autorizado pode rodar segredos de verificação de webhooks com janela de coexistência que não interrompa entregas válidas de forma imediata e não controlada.
FR10: Administrador do tenant pode emitir, rever e revogar chaves ou credenciais de integração conforme o modelo de acesso exposto pelo produto.
FR11: A plataforma pode receber eventos de entrada WhatsApp através de webhooks verificados e encaminhados ao tenant e contexto WABA/número corretos.
FR12: A plataforma pode recusar ou ignorar entregas de webhook que falhem proteção contra reenvio ou critérios de frescura acordados.
FR13: O pipeline de ingestão pode determinar de forma inequívoca o tenant (e, quando aplicável, WABA / ambiente) a partir do pedido recebido, antes de aplicar regras de negócio.
FR14: Atores autorizados podem enviar mensagens de saída WhatsApp através da plataforma segundo política e permissões do tenant.
FR15: Administrador do tenant pode gerir o ciclo de vida de mensagens de modelo (pedidos, estados de aprovação, uso) na medida exigida pelas políticas do canal, sem depender de ERP.
FR16: Tenant pode configurar e monitorizar sinais relevantes a opt-in, qualidade e limites do canal conforme políticas aplicáveis.
FR17: Operadores podem ver uma inbox unificada das conversas dos números a que têm acesso.
FR18: Operadores podem classificar conversas com etiquetas ou campos de triagem partilhados pela equipa.
FR19: Operadores podem transferir o atendimento entre automação e humano preservando contexto suficiente para continuidade.
FR20: Supervisor pode definir regras de encaminhamento, prioridade ou reatribuição entre filas ou agentes quando há handoff da automação para humanos.
FR21: Operadores podem ver sinais operacionais sobre atrasos ou falhas do canal relevantes ao seu tenant, sem expor dados de outros tenants.
FR22: Operadores podem construir e editar fluxos de conversa baseados em regras (sem motor LLM como núcleo no MVP).
FR23: Operadores podem testar fluxos em pré-visualização ou sandbox antes da publicação.
FR24: Operadores podem publicar fluxos com controlo de permissões e separação de ambiente.
FR25: A plataforma pode registar versões ou alterações materiais de fluxos de forma auditável.
FR26: A plataforma pode aplicar ações disparadas por regras (mensagens, etiquetas, handoff) segundo a configuração do tenant.
FR27 (F2): Operadores podem configurar e treinar um agente inteligente com políticas e limites no produto, quando a fase estiver ativa.
FR28 (F3): Organização pode orquestrar integrações externas através do módulo de orquestração quando a fase estiver ativa, incluindo pelo menos um percurso piloto acordado.
FR29: Tenant pode incorporar o painel operacional no workspace do cliente com contexto de sessão adequado.
FR30: Contacto final pode perceber de forma clara se interage com automação ou com humano durante a conversa, incluindo transições.
FR31: Contacto final pode receber explicação objetiva do tratamento de dados da conversa antes de interações que impliquem consentimento, quando aplicável.
FR32: Contacto final pode optar por mensagens proativas e retirar o consentimento, com confirmação registada de preferências.
FR33: Contacto final pode interromper categorias específicas de comunicação (ex.: marketing vs. transacional) sem perder canais essenciais de suporte acordados.
FR34: Contacto final pode utilizar o painel embutido com suporte a critérios de acessibilidade declarados pelo produto para os componentes suportados (ex.: alinhamento a WCAG 2.2 AA onde assumido).
FR35: Integrador pode invocar APIs documentadas de envio e operações expostas com semântica de idempotência em operações mutáveis.
FR36: Consumidor da API pode obter comportamento conforme uma versão declarada e suportada do contrato público.
FR37: Consumidor pode antecipar ciclo de vida de versões (suporte, descontinuação, coexistência) para API e, quando aplicável, para formatos de eventos de webhook.
FR38: Integrador pode usar ambiente de sandbox limitado ao tenant, sem acesso a dados de produção ou de outros tenants.
FR39: Integrador ou operador técnico pode consultar histórico de entregas de webhooks e alinhar reenvios ou reconciliação quando o produto expuser essa capacidade.
FR40: Consumidor da API pode receber semântica de erro documentada para falhas de autenticação, autorização e limitação de taxa, sem perda silenciosa de resultado para o tenant quando o produto se compromete com entrega visível.
FR41: A plataforma pode registar eventos de uso por tenant adequados a quotas e medição comercial (mensagens, operações-chave, agregações).
FR42: Comprador ou utilizador com papel de finanças pode aceder a relatórios orientados a valor (horas, capacidade, retrabalho) e evitar métricas exclusivamente vanity, quando o produto os expuser.
FR43: Administrador pode configurar limites de plano ou entitlements e receber alertas antes de bloqueios ou degradação quando configurado.
FR44: Utilizador autorizado pode exportar extratos de utilização e dados de faturação com identificadores estáveis para reconciliação com sistemas externos.
FR45: Tenant pode mapear finalidades e bases legais por fluxo ou tratamento conforme o modelo de governança suportado pelo produto.
FR46: Utilizador autorizado pode iniciar e acompanhar pedidos de direitos do titular (acesso, portabilidade, eliminação) com estados e trilho de auditoria; no MVP o percurso pode ser assistido por operações conforme passo 8.
FR47: Tenant pode apresentar lista de sub-processadores relevante com indicação de versão ou data de atualização.
FR48: Administrador do tenant pode configurar regras de retenção por categoria de dado dentro dos limites da política do produto.
FR49: A plataforma pode aplicar ou orquestrar aplicação de retenção e reportar resultados agregados sem exposição indevida de conteúdo.
FR50: Responsável de conformidade ou operador autorizado pode registar e consultar registo de consentimento, opt-in ou opt-out por contacto, para mensagens proativas e tratamento contínuo, além do fluxo de pedidos do titular.
FR51: Suporte da plataforma pode investigar incidentes no âmbito de um tenant com identificadores de correlação e classificação de culpa (Meta vs plataforma vs cliente).
FR52: Auditor autorizado pode consultar registos de auditoria filtrados por ator ou por capacidade para validar fronteiras de permissão.
FR53: Processo suportado pelo produto pode permitir acesso emergencial (break-glass) com aprovação, duração limitada e trilho de auditoria, alinhado a compliance.
FR54: Administrador da plataforma ou fluxo acordado pode executar ações de alto risco apenas com registo imutável ou apêndice auditável conforme política do produto.
```

### NonFunctional Requirements

```
NFR-PERF-01: Rotas críticas (ingest, envio, auth) com latência p95 alinhada ao SLO `API-lat` (Anexo A PRD).
NFR-PERF-02: Atraso evento de canal ? visibilidade no painel com SLO `OBS-fresh` (Anexo A).
NFR-PERF-03: Ingest de webhook (ack e persistência mínima) alinhada a `WH-ingest` / runbook de carga.
NFR-REL-01: API de produto com SLO `API-avail` e política de error budget (Anexo A).
NFR-REL-02: Falhas de entrega atribuíveis à plataforma conforme `CHAN-fail` (Anexo A).
NFR-REL-03: Drenagem de backlog de webhooks pós-falha com RTO e sem perda após persistência.
NFR-REL-04: Migração legado ? alvo com `MIG-parity` antes de cutover.
NFR-SEC-01: TLS 1.2+ em tráfego; sem endpoints de produção em TLS obsoleto.
NFR-SEC-02: Dados em repouso cifrados; segredos em KMS/secret manager.
NFR-SEC-03: Rotação programada e de emergência de segredos OAuth, webhooks e chaves.
NFR-SEC-04: Sessão com timeout; OAuth com refresh e revogação após logout administrativo forçado.
NFR-SEC-05: Rate limit por tenant com 429 documentado, Retry-After aplicável; quota em ingest.
NFR-SEC-06: Degradação Meta sem perda silenciosa; backpressure e alertas.
NFR-FAIR-01 a NFR-FAIR-04: Isolamento noisy-neighbor, enforcement de quota, atribuição de uso por tenant, headroom.
NFR-OPS-01 a NFR-OPS-05: Gates de SLO no release, caos/falha simulada Meta, retenção de logs de auditoria, alertas e separação de culpa.
NFR-LGPD-01 a NFR-LGPD-04: SLOs operacionais de DSAR, export, incidente de dados, subprocessadores.
NFR-A11Y-01 a NFR-A11Y-04: Foco, contraste, teclado, erros acessíveis (WCAG 2.1 AA mínimo embed).
NFR-INT-01 a NFR-INT-03: Retries 429, idempotência, compatibilidade de versão de API/contrato.
```

### Additional Requirements (Architecture)

- **Stack de entrega:** Python 3 + **FastAPI**, **PostgreSQL**, **Alembic**; borda de negócio **sem** Supabase, Deno ou Edge no pipeline de *delivery*; código novo em `apps/api` e `apps/admin-web` (Vite, React, Chakra alinhado ao UX).
- **Monorepo alvo:** `apps/api` + `apps/admin-web`; legado (ex.: `supabase/`) read-only exceto migração de esquema/dados mapeada para Alembic.
- **Multitenancy:** `tenant_id` + **RLS**; sem confiar no tenant inferido só pela URL; **OpenAPI** como fonte de contrato; REST `/v1/...` (versionado).
- **Auth: três superfícies** ? (1) consola: **OAuth 2.0 / OIDC** (login base) + **SSO** externo (SAML/OIDC) quando o piloto exigir; (2) **embed:** **JWT** (ou opaco) + **validação de domínio** / *allowlist* ? sem OAuth *redirect* dentro do *iframe*; (3) máquinas: **API keys** e **HMAC** de webhooks na borda FastAPI.
- **Erros e rastreio:** corpo JSON com `code`, `message`, `request_id` / *correlation*; cabeçalho canónico; **idempotência** com `Idempotency-Key` em mutações.
- **Webhooks:** validação, deduplicação, resolução de tenant (FR13) antes de regras; *outbound notify* alinhada a `docs/modular/13-*.md`.
- **CI:** Ruff, pytest, ESLint, Vitest; export ou validação de **openapi.json** quando política de contrato existir.
- **Gates pós-MVP (referência):** ADR *Embedded*; ADR *SSO broker*; SCIM/GraphQL/Kafka ? fora de escopo até ADR.

### UX Design Requirements

```
UX-DR1: Layout **split lista | thread** (MVP) com **Drawer** (ou coluna opcional) para regra, sandbox e estado, sem exigir três colunas em todos os *viewports* (direção A + UX spec passo 9).
UX-DR2: **Shell** de app estável (sidebar ou top) + **React Router** com rotas **lazy** e `Outlet` com inbox como rota principal; embed com entrada/rota e bundle o mais enxuto possível.
UX-DR3: **Tokens Chakra** semânticos: `status.*`, `inbox.*`, `status.channel`, `status.meta`, branding do tenant com `primary` + `logoUrl` sem desvirtuar grelha neutra.
UX-DR4: Estados de sistema **honestos**: fila, **429** com `Retry-After`, atraso Meta, frescura da inbox; **nunca** sucesso de UI com falha de pipeline sem indicação.
UX-DR5: **Cabeçalho de contexto** fixo: **tenant, WABA, número** em jornadas que cruzam configuração e inbox.
UX-DR6: **Recibos** / eventos: mostrar *correlation* / `request_id` em falhas e na linha de integração, alinhado a FR40 e *debugger* de integrador.
UX-DR7: **401** na consola e embed **sem loop cego**; no embed, renovação de token com **host** via `postMessage` quando acordado (sem OAuth dentro do *iframe*).
UX-DR8: Densidade **Comfortable** vs **Compact** com tokens (inbox = Compact) ? passo 8 UX.
UX-DR9: **WCAG 2.1 AA** mínimo para o embed onde o produto assume conformidade: foco, contraste, teclado, erros (alinhado a NFR-A11Y e FR34).
UX-DR10: Regras com blocos legíveis **gatilho ? condição ? ação ? teste**; validação antes de publicar; erros com campo e *copy* acionável (não *stack trace* crua ao operador).
```

### FR Coverage Map

| FR   | Épico | Nota breve |
|------|--------|------------|
| FR1  | Épico 1 | Perfil e definições da organização |
| FR2  | Épico 1 | WABA e números, estado visível |
| FR3  | Épico 1 (transversal) | RLS e validação de tenant em toda a matriz de entrega |
| FR4  | Épico 1 | Ambientes distintos sem mistura de dados |
| FR5  | Épico 2 | OAuth/OIDC consola |
| FR6, FR7 | Épico 2 | RBAC e autorização |
| FR8, FR9, FR10 | Épico 2 | Rotação API keys, segredos webhook, credenciais de integração |
| FR11?FR16 | Épico 3 | Ingest, anti-replay, resolução tenant, envio, templates, sinais de canal |
| FR17?FR21 | Épico 4 | Inbox, etiquetas, handoff, filas, sinais de atraso/falha |
| FR22?FR26 | Épico 5 | Regras, sandbox, publicação, auditoria, ações do motor |
| FR27 | Fase 2 | Fora do MVP: agente (história grelhada abaixo) |
| FR28 | Fase 3 | Fora do MVP: orquestrador (história grelhada abaixo) |
| FR29?FR34 | Épico 6 | Embed, transparência bot/humano, LGPD contacto, a11y |
| FR35?FR40 | Épico 7 | API pública, idempotência, versionamento, sandbox, erros |
| FR41?FR44 | Épico 8 | Uso, quotas, relatórios, extratos |
| FR45?FR50 | Épico 9 | Governança LGPD, DSAR, retenção, consentimentos |
| FR51?FR54 | Épico 10 | Suporte, auditoria, break-glass, ações de alto risco |

## Epic List

### Épico 1: Conta B2B, WABA e fundação da plataforma
Operador e **admin** dispõem de **organização estável, hierarquia org ? WABA ? número, ambientes separados e isolamento** comprovado ? base para o resto do produto, incluindo o **scaffold** FastAPI + admin web alinhado ao CDA.

**FRs:** FR1, FR2, FR3, FR4 + requisitos de *starter* (arquitetura, passo 3 CDA).

### Épico 2: Início de sessão, papéis e credenciais de integração
Utilizadores **entram** na consola com **OAuth/OIDC** (e preparação para **SSO** *enterprise*), têm **RBAC** claro, e a equipa **geres API keys, segredos de webhook e rotação** sem cortar o canal de forma incontrolada.

**FRs:** FR5, FR6, FR7, FR8, FR9, FR10.

### Épico 3: Canal WhatsApp de ponta a ponta
O **tenant** recebe e envia **mensagens** com **webhooks** verificados, **resolução inequívoca** de contexto, **gestão de templates** e **visibilidade** de sinais de **opt-in, qualidade e limites** ? confiança operacional no canal.

**FRs:** FR11, FR12, FR13, FR14, FR15, FR16.

### Épico 4: Inbox, triagem, filas e handoff
**Operadores** trabalham numa **mesa única** (lista | thread) com **etiquetas**, **handoff** com contexto, **filas e prioridades** e **sinais** de atraso/falha **por tenant** ? o OpenBSP como posto de operações.

**FRs:** FR17, FR18, FR19, FR20, FR21.

### Épico 5: Regras, sandbox e publicação
**Operadores** **constroem, testam, publicam e auditam** **fluxos por regras** (não LLM no MVP) e o **motor** aplica **ações** (mensagem, tag, handoff) conforme a configuração.

**FRs:** FR22, FR23, FR24, FR25, FR26.

### Épico 6: Painel embutido e confiança B2B2C
O **tenant** **incorpora** o painel no *workspace* do cliente; o **contacto final** e o **operador (embed)** têm **transparência** bot/humano, **tratamento de dados** e **a11y** alinhada ao compromisso (WCAG onde assumido).

**FRs:** FR29, FR30, FR31, FR32, FR33, FR34. **UX-DR1?10** (onde aplicável ao embed e à consola partilhada).

### Épico 7: API pública, integrador e contrato estável
**Integradores** têm **API versionada**, **idempotência**, **sandbox por tenant**, **histórico** de *webhooks* e **erros 401/403/429** com semântica **documentada** e **rastreio** (sem perda silenciosa).

**FRs:** FR35, FR36, FR37, FR38, FR39, FR40.

### Épico 8: Uso, entitlements e valor para comprador
A organização vê **eventos de uso** por **tenant**, **limites/alertas** e **relatórios** orientados a **valor** (não *vanity*), com **extratos** para **reconciliação**.

**FRs:** FR41, FR42, FR43, FR44.

### Épico 9: Governança de dados, DSAR e retenção
**Tenant** e **DPO/operador** cumprem **finalidades e bases legais**, **DSAR** com estados, **retenção**, **subprocessadores** e **consentimentos** de contacto ? requisito de **mercado B2B2C**.

**FRs:** FR45, FR46, FR47, FR48, FR49, FR50.

### Épico 10: Suporte, auditoria e acesso em emergência
**Suporte** investiga com **correlação** e **classificação de culpa**; **auditor** revê **trilho**; **break-glass** e **ações** de risco com **imutabilidade** mínima exigida.

**FRs:** FR51, FR52, FR53, FR54.

### Fase 2 e Fase 3 (grelha, fora do núcleo MVP)
- **Fase 2 (FR27):** agente inteligente com políticas e limites ? *gate* de produto e PRD de fase.
- **Fase 3 (FR28):** orquestrador (N8N ou similar) e integração **piloto** acordada.

---

## Épico 1: Conta B2B, WABA e fundação da plataforma

A organização **configura a sua conta, WABA e números** com **isolamento** e **environments** claros, sobre a **stack** acordada (FastAPI, Postgres, *admin* Vite + React + Chakra).

### Story 1.1: Monorepo alvo, saúde da API e contrato de erros mínimo

**Como** fornecedor da plataforma,  
**quero** o *scaffold* `apps/api` e `apps/admin-web` com *health* e padrão de erros alinhado ao CDA,  
**para** iniciar a entrega sem *drift* de *runtime* (sem novas *features* em legado excluído).

**Acceptance Criteria:**

**Dado** o repositório com a estrutura alvo do CDA,  
**Quando** a aplicação FastAPI inicia,  
**Então** um endpoint de *health* (e opcionalmente *readiness*) responde de forma previsível e a documentação OpenAPI básica está acessível.

**E** o formato de erro mínimo (`code`, `message`, `request_id`) aplica-se a erros 4xx/5xx geridos pela aplicação, em linha com o CDA (D4).

**E** a pipeline de CI mínima (ex.: *lint* + *test* vazios mas existentes) valida a `apps/api` (e front conforme o arranque).

**Requisitos:** fundação CDA; NFR-OPS (gate de fumo); padrão D4.  
**NFRs:** NFR-SEC-01 (TLS/ambiente *staging* alinhado a env).

---

### Story 1.2: Modelo de tenant, RLS mínima e prova de isolamento

**Como** administrador da plataforma,  
**quero** **organização/tenant** com **identificador estável** e **RLS** mínima no Postgres,  
**para** garantir **FR3** e base para WABA, inbox e integrações.

**Acceptance Criteria:**

**Dado** tabelas de base com `tenant_id` e políticas RLS,  
**Quando** dois *fixtures* de tenant são criados,  
**Então** testes (integração) demonstram que leitura/escrita *cross-tenant* é negada para papéis sem **break-glass**.

**E** a resolução de *tenant* segue a mesma fonte (claims/headers contratados, nunca só corpo) alinhada ao CDA e FR3.

**Requisitos:** FR3, D1.  
**NFRs:** NFR-SEC-02, NFR-FAIR-01 (base).

---

### Story 1.3: Perfil e definições da organização (FR1)

**Como** **admin** do *tenant*,  
**quero** **registar e editar** perfil e definições da minha **organização**,  
**para** operar a conta com metadados corretos (nome, fuso, contacto operacional, etc.).

**Acceptance Criteria:**

**Dado** um utilizador autenticado com papel que inclui *admin* de organização,  
**Quando** abre a área de definições,  
**Então** pode **ler e atualizar** os campos acordados no contrato de API, **só** no seu `tenant_id`.

**E** alterações gerais entram em *audit log* mínimo alinhado a FR52/FR54 (campos sensíveis).

**Requisitos:** FR1.

---

### Story 1.4: WABA, números e ambientes (FR2, FR4)

**Como** **admin** do *tenant*,  
**quero** **registar, listar e gerir o estado** de WABA(s) e número(s) **e** ambientes (dev/stage/prod) quando expostos,  
**para** alinhar a operação com o modelo org ? WABA ? número (sem confundir *datasets*).

**Acceptance Criteria:**

**Dado** uma organização existente,  
**Quando** o admin associa um **WABA** e número com IDs Meta estáveis,  
**Então** o estado (ativo, pendente, suspenso) é visível e persistido **com `tenant_id` e escopo** corretos.

**E** se **ambientes** forem oferecidos, dados de `dev` **não** misturam com `prod` (FR4).

**Requisitos:** FR2, FR4, FR3.

---

## Épico 2: Início de sessão, papéis e credenciais de integração

Utilizadores **acedem** à consola de forma **segura**; o **admin** **define papéis**; a equipa **geres credenciais** de **API** e **webhook** com **rotação** e coexistência.

### Story 2.1: OAuth / OIDC ? login base na consola (FR5)

**Como** utilizador,  
**quero** **iniciar sessão** com **OAuth 2.0 / OIDC** (login base) na consola,  
**para** aceder à aplicação com identidade *enterprise-grade* (preparação para SSO noutra história).

**Acceptance Criteria:**

**Dado** configuração de IdP/ cliente OAuth conforme *ADR*,  
**Quando** o utilizador conclui o *login*,  
**Então** a sessão da consola reflete a identidade e o **tenant** ativo, com **logout** a limpar estado sensível (NFR-SEC-04).

**E** a UI não expõe *stack trace*; erros têm *copy* mínima e `code` (UX-DR4, UX-DR6).

**Requisitos:** FR5.  
**NFRs:** NFR-SEC-01, NFR-SEC-04.  
**Nota:** **SSO** *enterprise* (SAML/OIDC) como extensão ? história distinta com *gate* de piloto (CDA D2); não bloquear 2.1.

---

### Story 2.2: Matriz de papéis e permissões (FR6, FR7)

**Como** **admin** do *tenant*,  
**quero** **atribuir papéis** (mínimo alinhado à matriz PRD: admin, operador, atendente, leitura, finanças, suporte) **a utilizadores** da minha org,  
**para** cumprir **menor privilégio** e **separar** operação, finanças e *break-glass* (FR53).

**Acceptance Criteria:**

**Dado** utilizador autenticado,  
**Quando** o admin cria/altera *membership* e papel,  
**Então** efeito é **só** dentro do `tenant_id` e **aplicam-se** negações em rotas/escopos de API (FR7).

**E** a API retorna 403 (não 200 vazio) com mensagem e `code` coerente ao tentar acesso a recurso proibido.

**Requisitos:** FR6, FR7.  
**UX:** alinhado a *TenantShell* e hierarquia (UX-DR5).

---

### Story 2.3: Chaves de API e emissão/revogação (FR8, FR10)

**Como** **operador** ou **admin** com permissão,  
**quero** **criar, revogar e listar** **chaves de integração** com **janela de coexistência** controlada,  
**para** migrar integrações sem *downtime* injustificado (FR8).

**Acceptance Criteria:**

**Dado** permissão explícita,  
**Quando** emito nova chave e marco a antiga para revogação *scheduled*,  
**Então** ambas as chaves têm *lifecycle* e datas visíveis; a revogação respeita a janela acordada.

**E** **não** se devolvem segredos *plain* após a criação (apenas *uma vez*).

**Requisitos:** FR8, FR10, FR7.  
**NFRs:** NFR-SEC-02, NFR-SEC-03.

---

### Story 2.4: Segredos de verificação de webhooks (FR9)

**Como** **operador** autorizado,  
**quero** **rodar o segredo** de verificação de **webhook** com **janela de coexistência**,  
**para** **Meta** e integrações continuarem a validar *callbacks* (FR9).

**Acceptance Criteria:**

**Dado** *webhook* com segredo *v1* e *v2* ativos no período de transição,  
**Quando** eventos com assinatura válida chegam,  
**Então** são aceites; eventos *inválidos* são rejeitados; após a janela, *v1* deixa de ser aceite (comunicação clara na UI *Integrações*).

**Requisitos:** FR9, FR11 (preparação).  
**NFRs:** NFR-INT-01, NFR-SEC-05.

---

## Épico 3: Canal WhatsApp de ponta a ponta

**Ingest** seguro, **resolução** de contexto, **envio** e **templates** e **sinais** de canal alinhados a Meta/BSP.

### Story 3.1: *Webhook* de entrada, verificação e encaminhamento (FR11, FR12, FR13)

**Como** *tenant* com WABA,  
**quero** **receber** eventos na plataforma via **webhook** verificável, **rejeitando reenvio** e **frescura** fora de política,  
**para** **FR11?13** e base do pipeline.

**Acceptance Criteria:**

**Dado** o *endpoint* de webhook (GET verificação, POST *payload*),  
**Quando** chega *payload* com assinatura e `tenant` / WABA mapeáveis,  
**Então** o evento é enfileirado **com `tenant_id` resolvido antes de regras** (FR13).

**E** *replay* fora de janela / critério é rejeitado (FR12) com telemetria e **não** persiste efeito duplicado indevidamente (NFR-INT-02).

**Requisitos:** FR11, FR12, FR13.  
**NFRs:** NFR-SEC-05, NFR-INT-02.  
**UX:** *correlation* visível (UX-DR6) nos detalhes técnicos.

---

### Story 3.2: Enviar mensagem de saída com fila e *retry* (FR14, NFR-INT-01)

**Como** ator **autorizado** (operador, integrador via API, motor de regras),  
**quero** **enviar** mensagem **WhatsApp** via plataforma com **política** de *retry* / **429**,  
**para** cumprir **FR14** e honestidade de entrega (sem *fake sent*).

**Acceptance Criteria:**

**Dado** conversa e permissões,  
**Quando** dispara *send*,  
**Então** o estado (pendente, entregue, falha) é persistido; **429** aplica *backoff* com `Retry-After` (NFR-INT-01).

**E** erros têm *correlation* e classificação de *culpa* plataforma vs Meta quando possível (FR51, UX-DR4).

**Requisitos:** FR14.  
**NFRs:** NFR-PERF-01, NFR-INT-01, NFR-SEC-05.

---

### Story 3.3: *Templates* e sinais de *opt-in* e qualidade (FR15, FR16)

**Como** **admin** do *tenant*,  
**quero** **acompanhar** o ciclo de *templates* e **sinais** de *opt-in*, *quality rating* e **limites** relevantes,  
**para** operar dentro das políticas Meta (FR15, FR16).

**Acceptance Criteria:**

**Dado** integração com API Meta,  
**Quando** o admin vê a lista de *templates* e *status*,  
**Então** estados mínimos (rascunho, submetido, aprovado, pausado) estão mapeados e justificam ações (ex.: pausa por baixa qualidade) ? ao nível alcançável pelo piloto, sem *ERP*.

**E** *dashboard* de sinais **não** é *vanity*: liga a incidentes/1k mensagens (PRD) quando dados existem.

**Requisitos:** FR15, FR16, FR21 (cruzamento mínimo).

---

## Épico 4: Inbox, triagem, filas e handoff

Mesa de operações **unificada** (lista | thread) com **etiquetas**, **handoff** e **sinais** de *health* do canal (UX-DR1, UX-DR4, UX-DR5).

### Story 4.1: Inbox com *split* lista | *thread* (FR17, UX-DR1, UX-DR5)

**Como** operador,  
**quero** **ver a lista** de conversas e o **fio** **no mesmo contexto** com **cabeçalho** *tenant* / *WABA* / *número*,  
**para** trabalhar a **tarefa** sem perder fio (UX passo 7 e 9).

**Acceptance Criteria:**

**Dado** permissões a números/filas,  
**Quando** abro a inbox,  
**Então** vejo a lista; ao selecionar, a *thread* carrega; **cabeçalho** mostra *context* (UX-DR5). **Abaixo de `md`**, *mobile* = lista a *fullscreen* e navegação para *thread* (UX spec 9).

**E** *loading* = *skeleton* + *stale-while-revalidate* (TanStack Query) sem mascarar erro (UX-DR4).

**Requisitos:** FR17, UX-DR1, UX-DR5, UX-DR8.  
**NFRs:** NFR-PERF-02 (OBS-fresh) ? mínimo verificável no piloto.

---

### Story 4.2: Etiquetas e triagem partilhada (FR18)

**Como** operador,  
**quero** **etiquetar** conversas com **etiquetas** de equipa,  
**para** **triar** e **reportar** sem planilha externa (FR18).

**Acceptance Criteria:**

**Dado** conversa,  
**Quando** adiciono/removo etiquetas,  
**Então** persistem; outros operadores com acesso veem o mesmo; restrição por *tenant*.

**Requisitos:** FR18.

---

### Story 4.3: Handoff e contexto mínimo (FR19, FR20)

**Como** operador,  
**quero** **passar** de automação **para humano** (e vice-versa) **com** **resumo** mínimo e **fila/roteamento** quando a automação gera *handoff*,  
**para** evitar o consumidor a repetir tudo (FR19, FR20, PRD Marina).

**Acceptance Criteria:**

**Dado** regra a emitir *handoff*,  
**Quando** o operador assume,  
**Então** vê **intenção** e **última saída do bot** e **estado** (aceite / *queued* / falhou) ? nunca *silêncio* se o pipeline falhou (UX-DR4).

**E** supervisão pode ajustar **fila/roteamento** conforme regras do tenant (FR20).

**Requisitos:** FR19, FR20.

---

### Story 4.4: Sinais de atraso/falha e *health* (FR21, UX-DR4)

**Como** operador,  
**quero** **ver** atraso/**falha** do *canal* **só** do meu *tenant* (e ações mínimas),  
**para** confiança operacional (FR21) sem ruído *cross-tenant*.

**Acceptance Criteria:**

**Dado** *incidente* ou atraso no pipeline,  
**Quando** abro a inbox,  
**Então** *banner* ou *badge* *honesto* (não «tudo verde») com *next step*; **distingue** *Meta* *vs* *plataforma* quando a taxonomia existir (PRD Anexo A, FR51 **preparação**).

**Requisitos:** FR21, FR51 (telemetria *UI* mínima).  
**NFRs:** NFR-OPS-05.

---

## Épico 5: Regras, sandbox e publicação

O **construtor** (gatilho ? condição ? ação) com **pré-visualização**/*sandbox*, **publicação** com *RBAC* e *ambiente*, **versões/auditoria** e **execução** do motor (FR22?26, UX-DR10).

### Story 5.1: Editor de fluxos e validação (FR22, UX-DR10)

**Como** operador,  
**quero** **criar/editar** *fluxos* por **regras** (sem LLM) com **validação** antes de testar,  
**para** **FR22** com erros *acionáveis* (campo, linha) (UX-DR10).

**Acceptance Criteria:**

**Dado** um fluxo em *draft*,  
**Quando** gravo,  
**Então** validação bloqueia *publish* de *draft* *inválido* com mensagem por campo/linha; **não** mostrar *stack* do servidor ao operador (UX-DR4).

**Requisitos:** FR22, UX-DR10.

---

### Story 5.2: *Sandbox* / *preview* (FR23)

**Como** operador,  
**quero** **testar** o fluxo em **sandbox** (*preview*) antes de *publish*,  
**para** **FR23** (Rafael no PRD).

**Acceptance Criteria:**

**Dado** fluxo *validado*,  
**Quando** executo *teste* em *sandbox* com *fixture* (mensagem, contacto *stub* se necessário),  
**Então** o resultado (sucesso, falha, log mínimo) fica *traceável* e **não** envia a *produção* (FR4).

**E** o *Drawer* de *sandbox* segue a direção *lista|thread* + *lente* (UX-DR1).

**Requisitos:** FR23, FR38 (preparar ligação a *ambiente* de teste *tenant-scoped* quando existir *sandbox* global).

---

### Story 5.3: *Publish* com permissão e *ambiente* (FR24)

**Como** operador com permissão,  
**quero** **publicar** fluxo com **permissão** e **separação** *dev/stage/prod* quando aplicável,  
**para** **FR24** e **Rafael** *publish* (PRD *Scoping* DoD *publish*).

**Acceptance Criteria:**

**Dado** *draft* aprovado e *sandbox* OK,  
**Quando** *publish* é confirmado,  
**Então** a versão **ativa** no *ambiente* alvo muda, com *audit* mínimo (quem, quando) (conexão com FR25).

**E** quem *não* tem papel, recebe 403 (FR7).

**Requisitos:** FR24, FR6/FR7.

---

### Story 5.4: Versão e *audit* de materialidade (FR25)

**Como** *auditor* ou *admin*,  
**quero** **histórico** de *versions* (ou *diff* mínimo) de alterações **materiais**,  
**para** **FR25** (compliance e *debug*).

**Acceptance Criteria:**

**Dado** *publish* ocorre,  
**Então** registo *append* com identidade e *timestamp*; *rollback* *one-click* fica fora *salvo* flag de produto ? **não** obrigatório no MVP; *diff* *visual* *TBD*.

**Requisitos:** FR25.

---

### Story 5.5: *Engine* aplica ações (FR26)

**Como** *tenant* com regra **publicada**,  
**quero** que a plataforma **aplique** *ações* (mensagem, *tag*, *handoff*) de acordo com a **regra** e o **estado** da conversa,  
**para** **FR26** (sem LLM *core*).

**Acceptance Criteria:**

**Dado** *inbound* após 3.1,  
**Quando** o motor *match* a regra,  
**Então** *ações* executam; erros *handling* não *silenciosos* (UX-DR4); liga a **3.2** e **4.3** sem dependência inversa indevida (histórias *anteriores* do canal + inbox *stub* mínimo podem *mock* até 4.1).

**E** a ordem e *idempotência* de *efeito* *side-effect* (mensagens) respeitam a política (NFR-INT-02).

**Requisitos:** FR26, NFR-INT-02.

**Nota de dependência mínima:** 5.5 precisa *pipeline* mínimo de conversa; **3.1** e **inbox* de leitura básica** (pode *subset* mínimo da 4.1) devem **preceder** a integração fim a fim em *QA*; na **história**, aceitar *feature flag* *«motor em staging»* antes do *inbox* completo, desde que o *DoD* *brownfield* do projecto o permita.

---

## Épico 6: Painel embutido e confiança B2B2C

**FR29 a FR34** e *embed* (JWT *baseline*, domínio, *postMessage*) (CDA D2, UX-DR2, 7, 9).

### Story 6.1: *Embed* autenticado (JWT/ opaco) e validação de origem (FR29, D2)

**Como** *tenant* que integra,  
**quero** **incluir** o painel no *workspace* com **token** e **validação** de *embed origin*,  
**para** **FR29** e isolamento (sem OAuth *redirect* no *iframe*; CDA D2).

**Acceptance Criteria:**

**Dado** *host* e *allowlist* de origem,  
**Quando** o *iframe* carrega com *Bearer* válido,  
**Então** a *session* *embed* funciona; se inválido, erros claros; **401** inicia *fluxo* de renovação *via* *host* (*postMessage*) sem loop infinito (UX-DR7, D2 *ADR*).

**Requisitos:** FR29, CDA D2, UX-DR7.  
**NFRs:** NFR-SEC-01.

---

### Story 6.2: *Copy* e estados *bot* / *humano* (FR30)

**Como** **contacto final** (canal) e **operador** (vista),  
**quero** **saber** *quem* fala (bot *vs* *humano*) e **transições** claras,  
**para** **FR30** (PRD *B2B2C*). **Copy** aprovada no *tenant*.

**Acceptance Criteria:**

**Dado** *handoff* e respostas automáticas,  
**Então** *templates* *WhatsApp* respeitam a política *UX*; no *painel*, rótulo de *modo* *bot*/*humano* e *timeline* (UX-DR4, PRD *Marina*).  
**E** o canal: conforme o desenho do *chatbot* por regras; o **mínimo** aceitável é o operador ver o modo (bot/humano) no painel.

**Requisitos:** FR30.  
*Dependência com FR31?FR33: ver histórias 6.3 e Epico 9.*

---

### Story 6.3: *Disclosure* de tratamento e *opt-in* *granular* (FR31, FR32, FR33) ? mínimo viável

**Como** operador,  
**quero** *flows* e *templates* a **recolher/confirmar** finalidade, *opt-in* e *categorias* com registo,  
**para** cumprir **FR31 a FR33** (LGPD e políticas) **no MVP mínimo** (PRD: percurso de DSAR híbrido/assistido; **nesta história** *copy* e *estado* no produto; *self-serve* completo de titular fica fora se o piloto o exigir). 

**Acceptance Criteria:**

**Dado** o desenho de fluxo,  
**Quando** o contacto entra percurso que requer *consentimento* ou *opt-out* categoria,  
**Então** o sistema *persiste* preferências mínimas e respeita *opt-out* de *marketing* sem bloquear *transacional* acordado (FR33, FR32).

**E** a *copy* padrão é **revisível** **pelo** *tenant* (política de produto). 

**Requisitos:** FR31, FR32, FR33, FR50 (cruzado **Epico 9** mínimo).

---

### Story 6.4: *Acessibilidade* do *embed* (FR34, UX-DR9, NFR-A11Y)

**Como** utilizador com necessidades *a11y*,  
**quero** **operar** a parte *embed* com **foco, contraste, teclado** e **erros** *acessíveis* **onde** o produto *assume* **WCAG 2.1/2.2 AA** (anexo a decisão *product* *legal* *UX* 8),  
**para** **FR34** e *NFR-A11Y*.

**Acceptance Criteria:**

**Dado** *embed* e roteiros prioritários,  
**Então** *Tab* *order* lógica; *focus ring*; contraste *AA*; erros *ligados* a campos. **0** *blockers* *críticos* *auditados* nas jornadas prioritárias (NFR-A11Y-01 a 04, FR34).

**Requisitos:** FR34, UX-DR9.  
**NFRs:** NFR-A11Y-01 a NFR-A11Y-04.

---

## Épico 7: API pública, integrador e contrato estável

*Integrator journey* (PRD + arquitetura D3, D4, padrões *snake_case*, OpenAPI, *sandbox*; **FR35 a FR40**).

### Story 7.1: *REST* *versioned* e *idempotency* (FR35, FR36, FR40)

**Como** *integrador*,  
**quero** recursos em **/v1** com *mutations* **idempotentes** e **erros** **documentados** (401/403/429) com *correlation* visível no corpo (JSON) da resposta,  
**para** cumprir **FR35, FR36, FR40** e *time-to-first-success* (PRD, integrador).

**Acceptance Criteria:**

**Dado** *OpenAPI* publicado,  
**Quando** chamo *send* com e sem `Idempotency-Key`,  
**Então** duplicados retornam o *mesmo* efeito lógico (409 ou 200 *consistent* conforme política) **sem efeito duplicado indevido**; **401** e **429** com `Retry-After` (NFR-SEC-05).

**E** o documento *OpenAPI* declara a versão (FR36).

**Requisitos:** FR35, FR36, FR40.  
**NFRs:** NFR-INT-01, NFR-SEC-05.

---

### Story 7.2: *Lifecycle* e *deprecation* *policy* pública (FR37)

**Como** *integrador*,  
**quero** *policy* *comunicada* de *sunset* *e* *coexistência* **de* **API* *e* *formatos* *de* *webhook***,  
**para** *FR37* (planeamento) **sem* *surpresa***.

**Acceptance Criteria:**

**Dado** *site* *docs* **ou* *header* *Deprec* *conform* *padrão*,  
**Então** *datas* e *janela* mínima documentada; *CI* *opcional* *lint* *OpenAPI* *breaking* *not* *fails* *silently* (CDA *gap* *importante*).

**Requisitos:** FR37.  
*Processo* em *docs* é *aceitável* no *MVP* com *CHANGELOG* e *versão* de *API* sem *automação* *plena*.

---

### Story 7.3: *Sandbox* *tenant* *scoped* (FR38, FR39)

**Como** *integrador*,  
**quero** *ambiente* *sandbox* **sem* *outros* *tenants* *nem* *prod* *data**,  
**para* *FR38*; *e* *consulta* *histórico* *de* *entregas* *webhook* *recebidas* *e* *reenvios* *mínimo*, *FR39*.

**Acceptance Criteria:**

**Dado** *chaves* *sandbox*,  
**Quando** *eventos* e *sends* ocorrem,  
**Então* *isolamento*; *tabela* *de* *deliveries* *com* *request_id* *e* *estado* *para* *reconcile* (FR39) *básica* *no* *MVP*.

**Requisitos:** FR38, FR39, FR3.

---

## Épico 8: Uso, entitlements e valor para comprador

Eventos de uso, limites e alertas, relatórios que não sejam *vanity*, exportação (FR41 a FR44).

### Story 8.1: *Metering* mínimo (FR41)

**Como** *sponsor* (comprador),  
**quero** **registar eventos de uso** por *tenant* com agregação adequada,  
**para** faturação futura e governança de carga (FR41) e NFR-FAIR-03.

**Acceptance Criteria:**

- Os eventos agregam mensagens inbound/outbound e operações-chave definidas no contrato.
- O MVP **não** exige módulo de faturação completo nem NRR; pode-se cobrar fora do produto, desde que o **uso** fique medido (PRD, *scoping*).
- O piloto **não** fica bloqueado por *billing* completo; só por falta de **medição mínima** se isso for critério explícito do piloto.

**Requisitos:** FR41.  
**NFRs:** NFR-FAIR-03.

---

### Story 8.2: Relatórios de valor *anti-vanity* (FR42) ? corte MVP

**Como** *comprador* ou *finanças*,  
**quero** **relatórios** com *horas libertadas* (proxy) e *resolução* sem *ranking* vaidoso de volume isolado,  
**para** FR42 (PRD, compradora financeira).

**Acceptance Criteria:**

- *Report* exportável; liga *uso* a *outcomes* quando as definições do piloto existirem.
- NRR / expansão **só** citados quando houver dado; no MVP, **não** vender *vanity* como prova (PRD).

**Requisitos:** FR42.

---

### Story 8.3: *Entitlements* e alertas (FR43)

**Como** *admin* do *tenant*,  
**quero** **configurar** limites de plano (ou *entitlements*) e **receber** alerta antes de bloqueio ou degradação,  
**para** FR43 e o *gate* comercial (PRD, *Innovation* / passo 6).

**Acceptance Criteria:**

- *Threshold* **configurável**; *notificação* in-app mínima.
- **Não** surpresa de upgrade: alterações sensíveis com registo mínimo de *audit* (PRD, *Governo comercial*).
- MVP mínimo: **exibir** e **registar** evento de aproximação/estouro de *entitlement* conforme política de produto.

**Requisitos:** FR43 (cruz. FR25 para trilha de *audit*).

---

### Story 8.4: Export de uso e faturação (FR44)

**Como** *utilizador* com papel de *finanças*,  
**quero** *export* **CSV** (ou equivalente) com identificadores estáveis e *período*,  
**para** reconcilição (FR44; PRD, micro-jornada financeiro).

**Acceptance Criteria:**

- Export com totais e linhas *auditáveis*; checksum ou *line count* validável.
- Não expor PII desnecessária fora de DSAR; **pacote** de *titular* alinha-se ao Epico 9 e a NFR-LGPD-02.

**Requisitos:** FR44.  
**NFRs:** NFR-LGPD-02 (coordenação com Epico 9 se o export coincidir com direitos de titular).

---

## Épico 9: Governança de dados, DSAR e retenção

LGPD e *governança* B2B2C (FR45 a FR50); *DSAR* no MVP com percurso **híbrido/assistido** (FR46; PRD, passo 8).

### Story 9.1: Finalidades e bases legais por fluxo (FR45)

**Como** *DPO* **ou** *admin* com permissão,  
**quero** mapear **finalidade e base legal** ao nível de *fluxo/regra* ou *tratamento* suportado,  
**para** ROPA/PRD (FR45).

**Acceptance Criteria:**

- Registos *versionáveis*; o modelo *jurídico* exato fica a cargo *legal* + produto; a história entrega a **capacidade** no produto, não o parecer jurídico.

**Requisitos:** FR45.

---

### Story 9.2: *DSAR* com estados e *ACK* (FR46, NFR-LGPD-01) ? MVP híbrido

**Como** *utilizador* autorizado,  
**quero** **abrir** pedido de direitos (acesso, portabilidade, eliminação) com **estados** e *ACK* interno,  
**para** FR46 e NFR-LGPD-01; o piloto pode ter processo **assistido** por *ops* (PRD, passo 8).

**Acceptance Criteria:**

- Pedido com *ACK* dentro da janela *operacional* acordada (NFR-LGPD-01).
- Se o *pack* automático não for total, *runbook* e trilha **no produto** documentados; *meta* 95% **calibrar** com piloto, não *hardcode* no código sem decisão de produto.

**Requisitos:** FR46, NFR-LGPD-01.

---

### Story 9.3: Lista de *subprocessadores* (FR47, NFR-LGPD-04)

**Como** *admin* do *tenant*,  
**quero** **listar subprocessadores** com *versão* ou *data* de *atualização*,  
**para** **FR47** e processo de notificação (NFR-LGPD-04).

**Acceptance Criteria:**

- Tabela/ registo; aviso a clientes de mudança *material* pode ser processo *comercial* + e-mail; no MVP, **exibir** última *alteração* e *versão*.

**Requisitos:** FR47, NFR-LGPD-04.

---

### Story 9.4: Retenção e aplicação (FR48, FR49)

**Como** *admin* do *tenant*,  
**quero** **regras de retenção** por categoria no limite da política da plataforma, e *estado* agregado de aplicação (sem *dump* indevido de conteúdo),  
**para** FR48 e FR49.

**Acceptance Criteria:**

- *Config* persistida; *jobs* a aplicar retenção com relatórios *agregados*; *DPIA* não é âmbito *desta* história (produto/ legal).

**Requisitos:** FR48, FR49, NFR-LGPD-02 (se export/titular cruzar).

---

### Story 9.5: Registo de consentimento e *opt* in/out (FR50), alinhado à Story 6.3

**Como** *operador* *de* *compliance* (ou *admin* com permissão),  
**quero** *registos* *de* *consentimento* *e* *preferências* *por* *contacto* (marketing, *transacional*),  
**para** **FR50** e coerência com FR32, FR33 (Story 6.3).

**Acceptance Criteria:**

- *Log* de *consentimento* *e* *preferências* *consultáveis*; liga a pedidos *DSAR* quando aplicável (FR32, FR33, FR50).

**Requisitos:** FR50, FR32, FR33.

---

## Épico 10: Suporte, auditoria e acesso em emergência

*Suporte* N2 e *compliance* operacional (FR51 a FR54).

### Story 10.1: *Correlação* e classificação de *culpa* (FR51) ? *tool* mín. interna ou *query* guiada

**Como** *suporte* N2,  
**quero** **pesquisar** por *tenant* + *janela* + *request_id* e **classificar** *incidente* (*meta* / *plataforma* / *cliente*),  
**para** **FR51** e o *Anexo* A (separação de *culpa*).

**Acceptance Criteria:**

- Ferramenta mínima *interna* **ou** *query* guiada com RBAC; **não** expor dados P1 fora de política; *ticketing* externo fica fora do *MVP* se não fizer parte do contrato.

**Requisitos:** FR51, NFR-OPS-05.

---

### Story 10.2: Consulta de *audit* *log* (FR52)

**Como** *auditor* com papel e *tenant* corretos,  
**quero** **filtrar** *registos* de *auditoria* por *ator*, *recurso* e *capacidade*, e **ver** *linha* *do* *tempo* mín. na *UI*,  
**para** **FR52** e NFR-OPS-03.

**Acceptance Criteria:**

- *P95* de *query* documentado; *não* *full* *text* de *mensagem* com PII sem máscara conforme *policy*.

**Requisitos:** FR52, NFR-OPS-03.

---

### Story 10.3: *Break-glass* e ações de *alto* *risco* (FR53, FR54)

**Como** *engenharia* *de* *suporte* (com *política* *de* *acesso* *emergencial* *e* *aprovação* *do* *cliente* *quando* *contr*),  
**quero** *acesso* *temporário* a *dados* *do* *tenant* *para* *diagnóstico* *com* *registo* *imutável* *ou* *apêndice* *e* *expiração* *forçada* *e* *notificação* *mínima* *ao* *cliente* *quando* *aplicável*,  
**para** *FR53* e *FR54*; *DPO* *e* *jur* *definem* *go-live* (NFR-LGPD-03 *cruz* *se* *incidente* *dados*). 

**Acceptance Criteria:**

- Não *há* acesso *oculto*; *sempre* *trilho* de *audit*; duração *finita*; *revogação* na *expiração*; *alerta* *P1* a *ops*; *conforme* *pol* da *empresa* e *DPO* antes de *produção*.

**Requisitos:** FR53, FR54, NFR-LGPD-03 (cruz. incidente *dados* *quando* *relevante*).

---

## Fase 2 e Fase 3 ? histórias grelhadas (fora do *DoD* do núcleo MVP)

### Story F2.1: Agente inteligente com políticas (FR27) ? *gate* F2

Aguarda *gate* e PRD de fase. **Não** bloqueia *ship* do *MVP*; custo por conversa e políticas ficam nas ACs de F2.

**Requisitos:** FR27.

### Story F3.1: Orquestrador (N8N ou similar) e integração piloto (FR28) ? *gate* F3

Aguarda PRD F3; *escopo* e *segurança* N8N via *ADR* e *D3*; **mínimo** uma integração piloto acordada com o cliente.

**Requisitos:** FR28.

---

## Notas de validação final (passo 4)

- **Cobertura de FR:** FR1 a FR26 (MVP) e FR29 a FR54 mapeados a pelo menos uma história; **FR27** e **FR28** estão na secção F2/F3.
- **Cobertura UX:** *UX-DR* (split, *drawer*, *tokens*, *recibos*, 429 honesto, *a11y*) distribuídos pelas histórias dos épicos 1, 4, 5, 6 e 7; *shell* *lazy* e *router* alinham 1.1 e 4.1.
- **NFRs e SLOs:** *baseline* e números exatos a calibrar com o piloto; *MIG-parity* (NFR-REL-04) em *stories* de migração / *runbook* após o *core* do MVP, não duplicada como épico à parte.
- **Dependências:** *histórias* ordenadas; a **5.5** requer 3.1 e *inbox* mínimo para E2E; *feature flag* «motor em *staging*» é aceitável até 4.1 *ready*.
- **Starter (CDA, passo 3):** a história *1.1* cobre *scaffold* FastAPI + *admin* Vite; a *1.2* aplica *RLS* mínima ? alinhado à recomendação de arranque do CDA (passo 8).

---

Fim do documento de épicos e histórias (v1) ? **open-bsp-api**. Próximos passos sugeridos: **Sprint planning** `bmad-sprint-planning` ([SP]), verificação opcional **Implementation readiness** `bmad-check-implementation-readiness` ([IR]) e, para orientação no ecossistema BMad, a skill `bmad-help`. Ver também [matriz NFR ? histórias](nfr-story-coverage-matrix.md) e [contexto do projeto para agentes](../project-context.md).
