---
stepsCompleted:
  - step-01-init.md
  - step-02-discovery.md
  - step-02b-vision.md
  - step-02c-executive-summary.md
  - step-03-success.md
  - step-04-journeys.md
  - step-05-domain.md
  - step-06-innovation.md
  - step-07-project-type.md
  - step-08-scoping.md
  - step-09-functional.md
  - step-10-nonfunctional.md
  - step-11-polish.md
  - step-12-complete.md
workflowNext:
  step: complete
  skillStepFile: null
  note: "Workflow `bmad-create-prd` concluído. Artefacto: este ficheiro."
prdCompletedAt: "2026-04-17"
platformTarget:
  stack: "Python (FastAPI) + PostgreSQL + OAuth 2.0 / OIDC"
  migrationFrom: "Deno + Supabase (legado até cutover documentado)"
  decided: "2026-04-17"
inputDocuments:
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
documentCounts:
  productBriefs: 2
  research: 2
  brainstorming: 0
  projectDocs: 21
workflowType: prd
classification:
  projectType: saas_b2b_primary_b2c_optional
  projectTypeNotes: >
    Posicionamento principal B2B/B2B2B (organizações, parceiros, multitenant).
    Uso B2C é possível mas mais raro; oferta B2C prevista para fase posterior,
    conduzida por marketing (não é o núcleo do go-to-market inicial).
  domain: general_horizontal
  domainProductEmphasis: AITech
  domainNotes: >
    Domínio de negócio horizontal (Tech / ênfase em capacidades de IA aplicadas ao produto).
    Segmentação por vertical de cliente é opcional e comercial ? o núcleo do produto não assume um setor específico.
  complexity: medium
  projectContext: brownfield
  elicitationSession: "2026-04-17 ? Advanced Elicitation + Party Mode (classificação)"
  journeyElicitationPasso4: "Advanced Elicitation + Party Mode (User Journeys)"
  domainComplexityNote: "CSV general=low; PRD complexity=medium; passo 5 = LGPD/Meta/BSP para todos os tenants (sem âncora setorial)"
  domainElicitationPasso5: "Advanced Elicitation + Party Mode (Domain-Specific Requirements)"
  partyModeSynthesis:
    matrixRecommendation: "Domínio do produto = plataforma horizontal com ênfase AITech; nenhuma vertical obrigatória no núcleo. GTM B2B primeiro; B2C = segunda linha de venda com escopo/PRD próprio quando existir."
    firstPrinciplesMustDocument: "Default B2B explícito; matriz titular/finalidade; entitlements que bloqueiam modo B2C sem contrato; KPIs separados se B2C entrar no roadmap."
    investorWording: "Evitar 'AITech' vazio; preferir job-to-be-done + métricas; horizontal = multi-segmento com núcleo comum, não 'para todos'."
    preMortemGuardrails: "Dados com legal_basis/purpose/tenant; SKUs B2B vs B2C; SLO do funil público; isolamento/RLS no canal B2C."
  visionPartyMode2026_04_17:
    methods: "Mary: Stakeholder Round Table; John: Socratic; Victor: Red vs Blue; Winston: What If"
    centralTension: "Governança/compliance institucional vs agilidade operacional/integrador vs confiança do contato final."
    wordingHardening: "Camada operacional multi-tenant para o canal; abstração e resiliência à volatilidade Meta; IA como camada opcional sobre fluxos/dados do tenant."
    architecturalHonesty: "Meta como dependência volátil; multi-tenant vs dedicado como ofertas distintas; correção vs escala explícitas."
  visionSocraticAnswers2026_04_17:
    audience: "B2B inicial; clientes usam com consumidor final (B2B2C)."
    problemMeasured: "Centralizar mensagens; reduzir trabalho manual em ERP; canal 24h; medir sem vanity."
    killerPremise: "Integração Meta OK; agente com qualidade e custo (modelos locais/externos)."
    successAlert: "Crescimento com churn; incapacidade de medir uso."
    redLines: "UX; modelo de uso de agentes; regras de negócio."
    differentiation: "Agente treinável + orquestrador de integrações vs chatbots genéricos."
  visionAEafterAnswers2026_04_17:
    maryRefinedBullets: 8
    johnPRDMapAndMetrics: "Subseções mapeadas; 5 proxies mensuráveis; B2B2C exige SLAs e governança consumidor."
    victorProofTypes: "Especificação verificável do treino; contratos de orquestração; piloto baseline vs pós."
    winstonNFRThemes: "Confiabilidade Meta; custo/latência agente; observabilidade ponta a ponta."
  validatedCheckpoint2026_04_17:
    icpSizing: "Indefinido - priorizar primeiros pilotos e refinar ICP com dados."
    mvpScope: "BSP + chatbot + painel embedded; F2 agente inteligente; F3 orquestrador (N8N ou similar)."
    channelV1: "WhatsApp apenas; outras fontes/canais - posterior."
    orchestrationTooling: "N8N ou similar nas fases de orquestração."
    bmadAgentBuilderNote: "Skill repo: .cursor/skills/bmad-agent-builder - agentes BMAD no IDE; políticas do bot no produto = FRs próprios."
  projectTypeInnovationSignals2026: "saas_b2b (CSV): Workflow automation; AI agents ? passo 6: diferenciação de produto + subtítulo explícito de decisões arquitetônicas (stack/agentes)"
  innovationElicitationPasso6: "Advanced Elicitation + Party Mode (Innovation ? anti-vanity, gates, pré-mortem F2)"
  projectTypeDeepDive: "saas_b2b (CSV project-types.csv): tenant_model; rbac_matrix; subscription_tiers; integration_list; compliance_reqs"
---

# Product Requirements Document - open-bsp-api

**Autor:** GD-AGK  
**Data:** 2026-04-17

## Estado do workflow (CP / `bmad-create-prd`)

- **Workflow Create PRD:** **concluído** (passos 01 a 12 no frontmatter); artefacto: este documento (`prdCompletedAt` no YAML).
- **Conteúdo entregue:** Executive Summary, Success Criteria (incl. Anexo A), Product Scope, User Journeys, Domain, Innovation, SaaS B2B (passo 7), Project Scoping (passo 8), Functional Requirements, Non-Functional Requirements, Classificação, Checkpoint, Polish (passo 11), Conclusão (passo 12).
- **Próximos passos (fora deste workflow):** ver **Conclusão do workflow PRD (passo 12)** no fim do ficheiro.

---

## Mapa do documento (leitura rápida)

Ordem das secções de nível 2 (âncoras estáveis no repositório):

| Ordem | Secção | Conteúdo |
|-------|--------|----------|
| 1 | Estado do workflow | Estado do workflow `bmad-create-prd` e ponteiros para o fim do documento. |
| 2 | Executive Summary | Objetivo, stack alvo, classificação resumida. |
| 3 | Success Criteria | Utilizador, negócio, técnico; Anexo A (SLI/SLO). |
| 4 | Product Scope | MVP / Growth / Vision (síntese). |
| 5 | User Journeys | Narrativas, requisitos de jornada. |
| 6 | Domain-Specific Requirements | LGPD, Meta, restrições técnicas. |
| 7 | Innovation & Novel Patterns | Diferenciação, validação, riscos. |
| 8 | SaaS B2B (passo 7) | Tenant, RBAC, planos, integrações, compliance. |
| 9 | Project Scoping (passo 8) | MVP estratégico, fases, riscos, DoD. |
| 10 | Functional Requirements | Contrato de capacidades (FR1+). |
| 11 | Non-Functional Requirements | Atributos de qualidade (NFR+); alinha ao Anexo A. |
| 12 | Classificação do produto | GTM, domínio, contexto brownfield. |
| 13 | Checkpoint de decisões | Tabela canónica MVP/Fases GD-AGK, KPIs, papéis. |
| 14 | Polish do documento (passo 11) | O que mudou no passe de coerência e rastreabilidade. |
| 15 | Conclusão do workflow PRD (passo 12) | Encerramento BMAD, próximos passos e validação. |

**Leitura sugerida:** **Resumo executivo** (secções 2?4) e **Checkpoint** para decisões; **Journeys + FR + NFR** para desenho e implementação; **Scoping passo 8** para limites MVP/piloto.

---

## Executive Summary (2c)

- **Objetivo:** plataforma multitenant B2B/B2B2B para WhatsApp Business (BSP), com visão unificada de conversas, **chatbot por regras** e **painel embedded** no MVP; canal **WhatsApp** na v1; evolução para **agente inteligente** (Fase 2) e **orquestrador de integrações** com N8N ou similar (Fase 3).
- **Problema:** centralizar mensagens, reduzir trabalho manual em ERPs, atender 24h com qualidade mensurável (sem métricas vanity); risco de crescimento com churn se não houver uso e observabilidade.
- **Diferenciação:** agente treinável + orquestrador de integrações vs chatbots genéricos; honestidade arquitetural sobre dependência **Meta** (volatilidade, SLAs) e multi-tenant vs dedicado como ofertas distintas.

### Decisão de plataforma (2026-04-17)

- **Stack alvo:** **Python (FastAPI) + PostgreSQL + OAuth 2.0 / OIDC** para API, dados e autenticação/autorização entre tenants e painéis.
- **Legado:** implementação atual **Deno + Supabase** permanece até cutover; documentação e operação do repositório podem ainda refletir esse stack durante a migração.
- **Inalterado:** GTM, fases MVP/F2/F3, checkpoint de papéis (comprador/operador/consumidor final), KPIs de piloto e requisitos de produto já alinhados.

### What Makes This Special

- Plataforma **horizontal** com ênfase **AITech**; clientes em qualquer setor usam o mesmo núcleo (orquestração WhatsApp, fluxos, embed) ? **sem** modelagem de domínio vertical no MVP.
- **B2B** no núcleo; **B2B2C** explícito; **B2C** possível em fase posterior com motion e PRD próprios.
- **Governança** (LGPD, políticas do bot no produto) equilibrada com **agilidade operacional** dos integradores e confiança do contacto final.

### Project Classification (resumo)

| Dimensão | Classificação |
|----------|----------------|
| Tipo / GTM | SaaS B2B primário; B2B2B; B2C opcional e posterior |
| Domínio | Horizontal (Tech / AITech) |
| Complexidade | Média |
| Contexto | Brownfield (OpenBSP + docs modulares no repo) |

---

## Success Criteria (passo 3)

Critérios derivados do alinhamento GD-AGK, Executive Summary e checkpoint; **SMART** onde há baseline ou meta explícita; restantes com **critério de medição** e calibragem nos primeiros pilotos.

### User Success

| Papel | O que é "sucesso" | Como medir |
|--------|-------------------|------------|
| **Consumidor final (B2B2C)** | Obter resposta útil rapidamente; não ficar preso num loop de bot quando precisa de humano | **Tempo até primeira resposta útil** (p50 e p90), em piloto com baseline antes/depois; taxa de **handoff** quando aplicável |
| **Operador** | Uma visão das conversas e estados no WhatsApp; configurar fluxos/regras e políticas sem depender de engenharia para cada mudança pequena | **Conversas abertas/fechadas**, **handoffs**, tempo até primeira resposta humana (opcional); conclusão de tarefas de configuração em tempo acordado (definir no piloto) |
| **Comprador** | Ver que a plataforma reduz trabalho manual e dá confiança no canal (não só "adoption" vaga) | Inquérito estruturado: **horas/semana** de trabalho manual antes vs. depois; revisão trimestral de utilização **por tenant** (mensagens, conversas, erros de canal) |

**Nota (refinamento AE + Party Mode):** telemetria e volume **não** substituem sozinhos a prova de valor; acoplar utilização a **antes/depois** em tempo útil ou horas manuais. No MVP, incidentes Meta e logs são **gates de confiança**, não prova isolada da proposição distintiva (isso entra com F2/F3).

### Business Success

- **Piloto (primeiros 1-2 tenants):** estabelecer **baseline** nas métricas da tabela "Measurable Outcomes" e melhoria documentada ao fim de um período acordado (ex.: 60-90 dias), com dono de métrica no lado cliente.
- **North Star (piloto):** definir **uma** métrica que ligue produto a **valor económico ou custo evitado por tenant** (ex.: minutos de trabalho humano evitados por conversa resolvida sem escalonamento, ou proxy acordado no contrato de piloto), com **fórmula, denominador, janela temporal e cohorte**; as demais métricas operacionais subordinam-se a esta para evitar "teatro de crescimento".
- **Critérios de saída de piloto:** além de "N tenants", acordar **gates** (ex.: decisão de compra/expansão, uso semanal mínimo, volume mínimo para amostra válida) e **definição operacional de tenant** (organização vs WABA vs ambiente) ao calibrar com o primeiro cliente.
- **Receita / retenção:** quando houver dados contratuais, acompanhar **churn de logo**, **churn de receita**, **NRR** e alerta de **"crescimento mau"** (definições no checkpoint) ? sem meta numérica fixa neste PRD até existir histórico; idealmente **uma proxy de receita/custo** no contrato de piloto, não só métricas de canal.
- **Go-to-market:** sucesso inicial B2B = tenants em piloto ou produção com critérios de seleção explícitos (WhatsApp oficial, dono do projeto, volume suficiente para medir ? a calibrar com o primeiro cliente).

### Technical Success

- **Stack alvo:** evolução controlada para **FastAPI + PostgreSQL + OAuth/OIDC** com **isolamento por tenant** e políticas de acesso coerentes com o modelo B2B2C.
- **Migração (legado ? alvo):** sucesso técnico inclui **marcos** (paridade de dados, read-only no legado, cutover, rollback verificável) para evitar "dois sistemas de verdade" sem critério de saída.
- **Canal Meta:** confiança operacional medida por **incidentes de integração** (webhooks falhados / mensagens não entregues) **por 1k mensagens**, com tendência monitorizada; complementar com **SLIs** explícitos (ex.: ack de webhook, taxa de erro por tenant, backpressure) e **separação de culpa** Meta vs plataforma em dashboards.
- **SLO / desempenho:** definir alvos numéricos (ex.: disponibilidade da API, p95/p99 em jornadas críticas), **janela, owner e consequência** (alerta vs página); observabilidade com **correlação** (ex.: trace_id, tenant_id) e **frescor** evento Meta ? painel interno acima de só contadores.
- **OAuth:** escopos mínimos, ciclo de vida de tokens, rotação/revogação e matriz permissão ? tenant documentados como critério de aceite.
- **Observabilidade mínima v1:** por tenant (e agregado): mensagens inbound/outbound, conversas abertas/fechadas, handoffs, erros de envio/API Meta ? **sem substituir** SLAs comerciais, mas permitindo prova de valor e debug.
- **Dados e conformidade:** LGPD com critérios **verificáveis** onde aplicável (retenção, export, bases legais nos fluxos do canal), além de políticas configuráveis.
- **Detalhamento operacional:** tabela **SLI/SLO**, error budget, matriz estendida de stakeholders e ligação ao passo 4 ? ver **Anexo A** abaixo (após o refinamento AE + Party Mode).

### Measurable Outcomes

Resultados mensuráveis para **piloto** (antes/depois, baseline explícito); metas numéricas **acordadas por tenant** quando o desenho permitir. Cada indicador deve ter **definição operacional**, **fonte de verdade** (evento/query) e **denominador** auditável ? evitar vanity (volume sem qualidade, "N tenants" sem amostra mínima).

1. **Tempo até primeira resposta útil** (p50, p90) ? perspetiva consumidor final; **definir "útil"** (estado da conversa / critério operacional) para ser reprodutível.
2. **Taxa de conversas resolvidas só com fluxo/regra** (sem humano), quando mensurável ? com máquina de estados / regra de encerramento explícita.
3. **Incidentes de integração Meta** por 1k mensagens (classificação consistente de falha vs tentativa).
4. **Horas/semana** de trabalho manual reportadas pelo cliente (inquérito estruturado com baseline; metodologia = critério de aceite).
5. **MVP (opcional, qualidade de fluxo):** proxies de **abandono após primeira interação** ou **loops antes de handoff**, alinhados ao chatbot por regras.
6. **A partir da Fase 2 (agente):** custo médio por conversa (LLM + infra), taxa de correção humana, **tempo até nova versão do comportamento em produção** (treinabilidade).
7. **Fase 3 (orquestrador):** **lead time** de processo ponta a ponta, taxa de falha em integrações piloto, satisfação do comprador no processo (a detalhar no PRD de fase).

**Observabilidade de "uso" (v1):** por tenant e por dia (ou hora): mensagens, conversas, handoffs, erros de envio/API; opcional: tempo médio de fila antes da primeira resposta humana. **Perturbações mínimas de piloto** a documentar: picos 429/503 Meta, webhooks duplicados/fora de ordem, skew de relógio, domínio de um tenant sobre filas (impacto em p90).

### Refinamento ? Advanced Elicitation + Party Mode (2026-04-17)

Ronda facilitada com métodos **mesa de stakeholders**, **pre-mortem técnico**, **first principles / JTBD (PM)**, **challenge tipo investidor** e **testabilidade (QA)**. Vozes BMAD: Mary (analyst), John (PM), Victor (estratégia), Winston (arquiteto), Murat (test architect). **Síntese:** critérios passam a exigir **auditoria** (definições, donos, gates de piloto, North Star, SLO/migração/OAuth/LGPD verificável, anti-vanity e cenários de caos mínimos). Extratos das vozes:

- **Mary:** falta auditar stakeholder estendido (compliance Meta, financeiro, suporte, DPO, integrador); calibrar tenant/cohort; SLAs internos e gates de go-live.
- **John:** no MVP, prova de valor = experiência + redução de trabalho manual; telemetria não substitui valor distintivo de F2/F3 ? subsecções de sucesso por fase.
- **Victor:** North Star económica e critérios de saída de piloto; evitar métricas dispersas sem ligação a renovação/expansão.
- **Winston:** pre-mortem de split-brain na migração; SLI/SLO, marcos de cutover/rollback, OAuth e LGPD como engenharia verificável.
- **Murat:** cada outcome amarrado a evento e teste de consistência; SLO de frescor; caos mínimo (Meta indisponível, duplicados, pico por tenant).

### Anexo A ? SLI/SLO e matriz de stakeholders (formalização)

**Uso:** contrato interno de engenharia e operações; **alvos numéricos** abaixo são **rascunho** ? calibrar baseline no primeiro piloto e rever trimestralmente. **Ligação ao passo 4 (User Journey Mapping):** cada jornada deve indicar que atores tocam que SLIs (quem sofre impacto quando o SLO quebra).

#### Tabela SLI / SLO

| ID | SLI (o que medimos) | Janela | SLO alvo (inicial) | Como medir | Dono | Falha ? |
|----|---------------------|--------|-------------------|------------|------|---------|
| **API-avail** | Razão de respostas HTTP 2xx (ou equivalente) da API de produto vs pedidos válidos | rolling 30d | ? 99,5% (piloto); meta prod ? 99,9% (rever após dados) | API gateway / logs | Eng prod | **Página** se duas janelas consecutivas abaixo do alvo |
| **API-lat** | Latência p95 em rotas críticas (ex.: ingest webhook, envio mensagem, auth) | rolling 7d | p95 < 2s (ajustar por rota em baseline) | APM, traces com `trace_id` | Eng prod | **Alerta**; revisão se degradar vs baseline |
| **WH-ingest** | Webhooks Meta aceitos e enfileirados com sucesso | por 1k eventos | ? 99% com ACK processual < 5s (ajustar) | Logs pipeline ingest | Eng prod | **Alerta**; postmortem se > 2× baseline piloto |
| **CHAN-fail** | Falhas de entrega/aplicação atribuíveis à plataforma (excl. 4xx por culpa do cliente) | por 1k mensagens | abaixo do **baseline** definido em piloto | Taxonomia de erro + `tenant_id` | Eng prod | **Postmortem** obrigatório se dois meses acima do baseline |
| **OBS-fresh** | Atraso entre evento de canal e visibilidade em agregados/painel operador | p95 | < 60s (exemplo; calibrar) | Medição ingest ? query UI | Eng prod | **Alerta** |
| **MIG-parity** | Divergência de dados críticos legado vs stack alvo (contagens / estados) | por gate de migração | 0 divergências **críticas** antes de cutover | Jobs de reconciliação | Eng prod | **Bloqueio de cutover** |
| **OAUTH-sess** | Falhas de refresh/revogação inesperadas (erro 5xx ou estado inconsistente) | rolling 30d | abaixo de limiar acordado após baseline | Logs auth | Eng prod | **Alerta**; revisão de segredos/escopos |

**Error budget (resumo):** para cada SLO com alvo de disponibilidade, definir **orçamento de erro mensal** (ex.: 99,9% ? 43 min/mês) e política: esgotado ? **freeze** de mudanças não essenciais + foco em fiabilidade (detalhar em runbook).

**Separação de culpa Meta vs plataforma:** classificar incidentes nas dashboards como `meta`, `plataforma`, `cliente`, `indeterminado` com critério documentado (evitar debate reativo em postmortems).

#### Matriz de stakeholders (extensão aos papéis do checkpoint)

| Stakeholder | Interesse principal | Risco se ignorado | Métrica / satisfação sugerida |
|-------------|---------------------|-------------------|------------------------------|
| **Integrador técnico (cliente ou parceiro)** | APIs estáveis, credenciais, sandbox, documentação | Projeto atrasa; abandono técnico | Time-to-first-success (primeira mensagem fim-a-fim); % tickets P1 fechados em SLA |
| **Suporte N1/N2 (fornecedor)** | Playbooks, logs por tenant, ferramentas | MTTR alto; confiança baixa | MTTR por severidade; taxa de reopen; CSAT em tickets críticos |
| **Financeiro / revenue ops** | Faturação alinhada a uso; NRR | Disputas; churn silencioso | Reconciliação uso?fatura; NRR por cohorte piloto |
| **Compliance / qualidade canal (Meta e políticas)** | Contas, quality rating, messaging limits | Risco operacional na conta WABA | Incidentes de política; limites e alertas proativos |
| **DPO / segurança** | LGPD, retenção, minimização, acesso | Multa ou bloqueio legal | Evidências de export/eliminação no prazo; auditorias internas OK |
| **Operações de produto** | Roadmap vs SLO; noise de alertas | Fadiga de incidentes | Alertas por SLO com baixo falso positivo; revisão trimestral de thresholds |

**Nota:** comprador, operador e consumidor final permanecem definidos no **Checkpoint**; esta matriz **não substitui** essa tabela ? complementa com atores que tipicamente influenciam **sucesso mensurável** e **risco**.

---

## Product Scope (passo 3)

Síntese alinhada ao checkpoint MVP / F2 / F3; detalhe operacional permanece nas secções de classificação e decisões abaixo.

**Fonte canónica de escopo:** a definição **operacional** de MVP, fases e piloto está em **Project Scoping & Phased Development (passo 8)** e na tabela **MVP vs fases** do **Checkpoint de decisões**; esta secção resume o mesmo alinhamento ? em caso de dúvida, prevalece o **Checkpoint** para critérios GD-AGK e o **passo 8** para gates e DoD.

### MVP - Minimum Viable Product

- **BSP** + **chatbot por regras** (fluxos/regras, não LLM como núcleo) + **painel embedded**.
- Canal **só WhatsApp**; atendimento **24h** com parte **híbrida** (regras primeiro; humano quando aplicável).
- **Ações** por **regra de fluxo** (mensagens, tags, handoff); integração profunda com ERP **fora do núcleo MVP** salvo exceção explícita.
- **Centralizador v1:** visão unificada no produto das conversas e estados no WhatsApp (inbox / histórico + embed), sem pretender ser CRM único do mundo.

### Growth Features (Post-MVP)

- **Fase 2:** **agente inteligente** ? treino, usabilidade, contexto do sistema do cliente para o cliente final; políticas e limites configuráveis no produto.
- **Fase 3:** **orquestrador de integrações** (N8N ou similar); **uma integração piloto** com primeiro cliente quando escopo o permitir.

### Vision (Future)

- Canais além do WhatsApp; motion **B2C** com PRD e entitlements próprios; ofertas **multi-tenant vs dedicado**; expansão de SKUs e maturidade de **NRR** / upsell conforme dados.

---

## User Journeys (passo 4)

Narrativas para cobrir **caminho feliz**, **caso limite**, **operação/admin**, **comprador**, **integração técnica**, **suporte** e **micro-jornadas** de compliance/finanças. SLIs referenciados alinham ao **Anexo A** (ligação explícita pedida no passo 4).

### Marina ? consumidora final (B2B2C), caminho feliz

**Abertura:** Contacta a organização no WhatsApp no fim do expediente; quer saber se o serviço cobre a região e qual o prazo.

**Ação ascendente:** O fluxo por regras responde em segundos com informação estruturada (âmbito, próximo passo, opção de falar com pessoa).

**Clímax:** Um detalhe extra (documentação) leva o bot ao limite; o handoff para humano é explícito, com contexto para não repetir tudo.

**Resolução:** Agente humano confirma e fecha o ponto; Marina sai com dúvida resolvida.

**Arco emocional:** curiosidade ? alívio ? confiança no limite do bot ? satisfação com continuidade humana.

**SLIs tocados:** `WH-ingest`, `API-lat`, `OBS-fresh`, `CHAN-fail` (ausência de falha atribuível à plataforma no happy path).

### Marina ? caso limite (atraso Meta / webhook)

**Abertura:** Mesma intenção, horário de pico; o duplo visto demora.

**Ação ascendente:** Sem resposta automática visível, a ansiedade sobe (medo de fila, bug ou número errado).

**Clímax:** A plataforma recupera: ingestão tardia do webhook, atualização do estado; o bot pede desculpa contextual **ou** o operador vê o atraso no painel e assume com prioridade.

**Resolução:** Explicação breve da demora no canal + conclusão do pedido.

**Arco emocional:** expectativa ? tensão ? pico de incerteza ? alívio com recuperação e presença humana.

**SLIs tocados:** `WH-ingest`, `API-lat`, `OBS-fresh`, `CHAN-fail` (todos sob pressão).

### Rafael ? operador / admin (happy path)

Rafael precisa fechar o ciclo pedido pelo CX: novo fluxo de triagem de leads, sem planilha nem grupo informal. Mapeia gatilhos e respostas no construtor, **testa em sandbox** até a conversa ?respirar?, **publica** com controlo de permissões e abre o **inbox embed** onde o time já trabalha ? o WhatsApp deixa de ser caixa preta e passa a ser mesa de operação. **Batida emocional:** não é ?uau tecnológico?; é **controlo partilhável** (mostrar ao gestor *como* o atendimento flui).

**SLIs tocados:** `OBS-fresh`, `API-avail`, `API-lat` (painel e publicação); falhas de canal impactam confiança do operador (`CHAN-fail`).

### Diretora financeira ? compradora (valor, anti-vanity)

Percorre relatório de **horas/capacidade libertada** e redução de retrabalho, cruzando volume atendido e tempo de resolução ? não ?ranking de mensagens?. Se a evidência liga a **menos risco operacional** e **capacidade para casos complexos**, valida investimento; se parecer vanity, encerra a análise.

**Capabilities:** relatórios orientados a valor (alinhados a Business Success / North Star).

### Integrador técnico ? primeira mensagem fim a fim

Registo da aplicação, **OAuth** (client, fluxo de tokens), **sandbox** com número de teste, **webhook** HTTPS verificável, validação de payload e correlação com envio. Chamada de **envio** com bearer válido; **idempotência** em retries (chave de negócio / contrato da API). Observabilidade com logs correlacionados.

**Ramo de falha:** **401** ? renovar token, evitar loop com credencial inválida; **429** ? backoff, `Retry-After`, filas e política de taxa acordada com produto.

**SLIs / métricas:** disponibilidade do endpoint de envio, **p95** envio ? confirmação, taxa **5xx**, taxa **401/429**, tempo até primeira mensagem bem-sucedida em sandbox (cruzamento com `API-lat`, `OAUTH-sess`, `CHAN-fail`).

### Suporte N2 ? incidente por tenant

Abrir ticket com tenant, janela, impacto (mensagens, template, webhook). Confirmar WABA, ambiente, versão. Correlacionar `request_id`/timestamp com trilha webhook ? Meta ? persistência. Classificar **culpa** Meta vs plataforma vs cliente. Reprodução mínima controlada; escalar com evidências. Gancho de **postmortem**: causa raiz, mitigação, follow-up (alerta/teste), dono e ligação ao ticket.

**Testes / caos mínimos ligados:** falhas sintéticas Meta (rate limit, 5xx); isolamento por tenant (RLS / credenciais); observabilidade suficiente para reconstruir a linha do tempo em minutos.

### Micro-jornadas (extensão ? Mary)

- **Exportação de dados para o DPO (LGPD):** quem pede, âmbito do export, prazos, verificação de identidade, trilho de auditoria até entrega ao titular ? separado de suporte genérico.
- **Reconciliação financeira pós-faturamento:** extratos BSP/Meta vs uso interno vs fatura; exceções para finanças com critério de encerramento.

**Pre-mortem (âncoras):** dono de **offboarding/portabilidade**; playbook de incidente com jurídico/seguro; **custo por conversa** visível para financeiro antes de escalar roadmap multi-tenant.

### Journey Requirements Summary

Capabilities reveladas pelas jornadas (priorizar no backlog de FR/NFR):

- Construtor e **versionamento** de fluxos com validação pré-publicação; **sandbox / preview** repetível.
- **Publicação** com controlo (ambiente, permissões, auditoria mínima de mudança).
- **Inbox embed** integrável ao workspace do cliente.
- Telemetria de **operação** (filas, tempos, conclusões, falhas) ? não só volume.
- Relatórios **anti-vanity** (horas, capacidade, retrabalho) para comprador.
- **OAuth**, webhooks verificáveis, API de envio com contrato de **idempotência** e erros documentados (401/429).
- **Observabilidade** por tenant com correlação (`trace_id`, `tenant_id`) e runbooks de suporte/postmortem.
- **LGPD:** export/portabilidade como jornada própria; **billing** conciliável com uso.
- **Handoff** com contexto preservado; tratamento de **atraso de canal** visível ao operador.

### Refinamento ? Advanced Elicitation + Party Mode (passo 4)

Ronda com **Sally** (narrativa/emotion), **John** (capabilities + comprador), **Winston** (OAuth/API/falhas), **Murat** (suporte/chaos), **Mary** (lacunas compliance/financeiro + micro-jornadas + pre-mortem). **Síntese:** jornadas passam a exigir ligação explícita a **SLIs**, anti-vanity no relatório do comprador, idempotência e política de 429, investigação com separação de culpa, e extensão para **DPO** e **reconciliação** para não deixar LGPD/billing como ?checklist depois?.

---

## Domain-Specific Requirements (passo 5)

**Decisão de elegibilidade:** complexidade do projeto no PRD = **medium**; `domain-complexity.csv` usa **general** como referência de baixa complexidade setorial ? a sobrecarga regulatória vem sobretudo de **mensageria B2B2C**, **LGPD (Brasil)** e **políticas Meta / WhatsApp BSP**, comuns a **todos** os tenants. **Extensões por vertical** (quando um cliente exigir regras ou integrações próprias de setor) são **módulos opcionais** ativados por contrato, não parte do núcleo horizontal.

### Compliance & Regulatory

- **LGPD:** mapear **finalidade** por fluxo (webhook, mensagens, billing, suporte); **bases legais** por tratamento; fluxo documentado de direitos do titular (acesso, correção, exclusão, portabilidade) com SLA interno; **encarregado (DPO)**, canal publicado e cooperação com tenants em modelo multi-tenant.
- **Contratual / governança:** **DPA** com clientes; lista e atualização de **subprocessadores** (incl. Meta); processo de notificação a mudanças; **registro de operações de tratamento (ROPA)** e inventário auditável.
- **Transferência internacional:** dados processados via infraestrutura Meta (ex. EUA) ? documentar avaliação, instrumentos aplicáveis e repasse de obrigações ao cliente quando pertinente.
- **Meta / WhatsApp Business:** políticas de uso, **quality rating**, opt-in, **templates** (aprovação, categorias, pausa por baixa qualidade), limites de throughput/tier; restrições de comércio/catálogo ? tratadas como **requisitos de domínio** com monitorização e alertas ao tenant.
- **Acessibilidade (experiência regulada):** alinhar painel embedded a critérios equivalentes **WCAG 2.2 AA** onde o produto assumir obrigação de interface inclusiva (ver também FRs em Sally no refinamento abaixo).

### Technical Constraints

- **Multi-tenant:** isolamento no Postgres (**RLS** / políticas) + validação de tenant em **todas** as camadas; sessão/OAuth com claims verificáveis; sem inferir tenant só por URL.
- **Segurança:** TLS em trânsito; cifrado em repouso conforme stack; **segredos** em vault; rotação de chaves de webhook e credenciais.
- **OAuth (Meta):** tokens por tenant, escopos mínimos, refresh/revogação sem fallback inseguro.
- **Auditoria:** trilho append-only para ações de alto risco (export, mudança de fluxo, acesso a dados sensíveis, troca de tokens).
- **Retenção:** políticas por tipo de dado (logs vs conteúdo de mensagens) com TTL e processos de eliminação alinhados a LGPD e negócio WABA.
- **Superfície:** validação de assinatura de webhooks, rate limiting, hardening de API/edge.

### Integration Requirements

- **Meta Cloud API / BSP:** abstração versionada contra mudanças de API; changelogs monitorizados; feature flags / rollback.
- **Export / portabilidade:** capacidades técnicas alinhadas aos direitos LGPD e aos micro-fluxos já referidos nas jornadas.
- **Canais futuros (visão):** desenho de integrações para não acoplar 100% ao WhatsApp (reduz dependência de política única).

### Risk Mitigations

| Risco de domínio | Mitigação (sumário) |
|------------------|----------------------|
| Mudanças de API / política Meta | Camada anti-coupling, monitorização, planos de rollback; relacionamento BSP |
| Banimento / restrição WABA | Opt-in, warm-up, qualidade de conteúdo, ambientes separados, backup de documentação de números/templates |
| Multas / incorreção LGPD | Privacy by design, minimização, ROPA, DPIA quando aplicável, DPO como gate de produto |
| Limites de quota / tier WABA | Dimensionamento, filas, observabilidade de erros 429, contratos alinhados ao volume real |
| Dependência exclusiva de messaging | Roadmap multi-canal incremental; export de dados; narrativa contratual clara |

### Módulos opcionais ? extensões verticais (sob demanda)

O núcleo BSP **não** inclui entidades nem fluxos específicos de um setor (retail, saúde, serviços, indústria, etc.). Quando um **cliente** exigir, por contrato:

- regras adicionais de dados (ex.: categorias especiais de titulares, bases legais reforçadas);
- consentimento ou registos sectoriais acima do baseline LGPD/Meta;
- **procurement** enterprise (licitação, contratos quadro, garantias);

isso é tratado como **pacote de extensão / integração dedicada**, não como modelo de dados central do produto.

### Refinamento ? Advanced Elicitation + Party Mode (passo 5)

**Vozes:** **Mary** ? LGPD, DPA, subprocessadores, Meta/BSP, ROPA; **Winston** ? RLS, auditoria, retenção, OAuth, superfície; **Victor** ? risco API Meta, banimento WABA, LGPD, quotas, dependência de canal; **John** ? delimitação núcleo horizontal vs extensões verticais; **Sally** ? FRs de opt-in, transparência bot/humano, WCAG no embed.

**Síntese:** LGPD e Meta são **restrições de produto** para qualquer tenant; engenharia sustenta **auditabilidade** e **isolamento**; verticalização só entra por **contrato**; UX de confiança (opt-in, bot/humano, acessibilidade) permanece explícita.

---

## Innovation & Novel Patterns (passo 6)

**Sinais (tipo `saas_b2b` em `project-types.csv`):** *Workflow automation; AI agents* ? aplicados ao produto como combinação **orquestração WhatsApp multitenant + automação de fluxos + camada de agentes** com governo explícito, sem vender inovação vazia.

**Enquadramento (Winston):** *Inovação* aqui = **diferenciação de produto e de GTM** (o que o cliente percebe e paga). **Agentes desacoplados** e **migração FastAPI** são **decisões arquitetônicas e padrões de engenharia** maduros (limitação de complexidade, strangler/paridade), não ?novelty? de pesquisa; ficam explicitamente sob o subtítulo seguinte para não diluir a secção com *inovação-teatro*.

**Table stakes (Victor):** conectores à API Meta, webhooks e fluxos básicos são **comuns** ? não são em si ?inovação?; o argumento defensável é **multitenant + BSP + governo + SLIs + LGPD + faseamento honesto + embed**. Complementar com **um** critério mensurável de diferenciação (métrica + baseline + prazo por release/piloto) e, por fase, **hipótese de valor** + **o que falharia** se a hipótese estivesse errada.

### Diferenciação de produto (inovação no PRD)

- **Automação de fluxo com governo comercial:** fluxos estilo chatbot e capacidades **por plano/conta** ? inovação de **empacotamento e previsibilidade** (o que o cliente pode ligar sem surpresa de custo ou risco), não só ?mais um bot?.
- **Faseamento explícito:** MVP com **regras**; Fase 2 **agente treinável** com políticas no produto; Fase 3 **orquestrador** (N8N ou similar) ? inovação como **cadência honesta** (menos ?IA no dia um? e mais **prova por fases**).
- **Embed operacional:** inbox/config no **contexto do sistema do cliente** (iframe) ? reduzir ilha WhatsApp vs stack do tenant.

### Decisões arquitetônicas e continuidade brownfield (padrões, não ?novel patterns?)

- **Agentes desacoplados (complexidade fora do core):** prioridade documentada no repositório ? **agentes avançados como serviços externos** (OpenAI SDK, ADK, etc.) com protocolos (`a2a`, chat-completions, MCP) em vez de monólito conhecimento-tudo; **agente leve** no núcleo com ferramentas (MCP/SQL/HTTP) onde fizer sentido ? **fronteira de sistema** e custo/risco controláveis, alinhado ao risco *Complexidade de agentes* na tabela abaixo.
- **Stack e evolução:** migração declarada para **FastAPI + Postgres + OAuth** com trilho de paridade ? **continuidade operacional** e redução de dependência da stack legada; tratar como **decisão de plataforma** documentada no *architecture* / ADRs, não como claim de inovação de mercado.

### Market Context & Competitive Landscape

- Mercado maduro de **conectores WhatsApp** e chatbots genéricos; diferenciação não é ?ter API Meta?, e sim **multitenant + BSP + observabilidade + governança LGPD/Meta** + **roteiro claro** até agente e orquestração.
- **Parceiros Meta / ISV** e agências reforçam necessidade de **SLIs**, **transparência de custo canal** e **embed** com marca do cliente.
- **Arquétipos (Mary):** (A) automação/bot **genérico** ? rápido, tende a vanity e pouca governança B2B2C; (B) **BSP/enterprise fechado** ? escala e compliance, menos flexibilidade para self-host e agentes externos com contratos claros. **Lacuna reclamada:** meio-termo **multitenant/open**, WhatsApp oficial, honestidade Meta, **agent-ready** com orquestração ? sem só superficialidade nem só lock-in.
- **Validação comercial sugerida:** matriz competitiva **versionada** (5?8 capacidades vs A/B, com fonte/data); ICP com **lista curta** de contas-alvo + **desqualificadores**; plano **30/60/90** dias pós-piloto vs baseline.
- Pesquisa adicional (opcional): gatilhos CSV `compliance requirements;integration guides` + *workflow automation* + ano corrente.

### Validation Approach

- **Piloto com baseline:** North Star e métricas já definidas ? validar **com números**, não com demo.
- **Gates mensuráveis (John) ? alinhar limiares no 1.º piloto:**
  - **Governo comercial:** publicação de fluxos **sem** estouro de quota nem ?surpresa? de upgrade por entitlements (evento auditável).
  - **Agentes desacoplados:** integrações em produção com **contrato versionado** + **testes de contrato** verdes no CI para a versão suportada (Murat).
  - **Faseamento:** **go/no-go** escrito por fase (North Star + baseline **fechados**) antes de ligar a fase seguinte (LLM só após gate MVP).
  - **Embed:** **p95** ?tempo até primeira ação útil? ? limiar do piloto; com `tenant_id`/sessão.
  - **Migração stack:** marco de **paridade** ? jornadas críticas fechadas com regressão aceitável ou % de paridade antes de cutover.
- **Prova por fase (LLM):** custo/conversa, correção humana, tempo até publicar comportamento ? só após gate F2.
- **Orquestrador:** **uma** integração piloto; lead time e falhas antes de repetir.
- **Arquitetura / agentes (Murat):** contratos de fronteira estáveis; **isolamento de falha** (circuit breaker / degradação); `tenant_id` até ao agente externo; idempotência + **429** + duplicados + **caos mínimo**; alinhado a testes de contrato Meta.

### Pré-mortem: Fase 2 (agente) atrasada ou inexistente (John)

- Proposta de valor recua para **BSP + regras + embed**; North Star = apenas métricas que o **MVP** prova.
- SKUs e messaging **alinhados** ao MVP real; sem prometer treino LLM até existir entrega.
- Métricas F2 **fora** do discurso comercial até haver produto; F3 pode ancorar-se em **integração/lead time** sem depender de LLM.

### Risk Mitigation

| Risco | Mitigação |
|--------|------------|
| **Inovação-teatro** (?IA? no marketing sem critério) | AITech em **FRs** e fases; **table stakes** explícitos; critério mensurável único (baseline + prazo) |
| **Narrativa sem defensibilidade** | Hipótese por fase + matriz competitiva; o que falha se a hipótese estiver errada |
| **Complexidade de agentes** | Agentes pesados **fora** do core; contratos e limites claros |
| **Dependência Meta** | Abstração de API, multi-canal na visão, separação de culpa |
| **Over-promise de automação** | Regras primeiro; quotas WABA explícitas; SKUs honestos se F2 atrasar |

### Refinamento ? Advanced Elicitation + Party Mode (passo 6)

**Vozes:** **Victor** ? table stakes vs novidade; critério verificável; hipótese por fase. **Winston** ? produto vs decisão arquitetônica (já no enquadramento). **Mary** ? arquétipos A/B e lacuna; matriz e ICP. **John** ? gates por área; pré-mortem se F2 não existir. **Murat** ? prova de desacoplamento (contrato, isolamento, caos).

**Síntese:** a ronda **endurece** validação (gates), **reduz vanity** de mercado e liga **testes** à narrativa de agentes ? sem substituir o passo 7 (project type), que pode puxar mais detalhe SaaS B2B.

---

## SaaS B2B ? requisitos específicos de tipo de projeto (passo 7)

**Fonte:** `project-types.csv`, linha **`saas_b2b`**, alinhada a `classification.projectType: saas_b2b_primary_b2c_optional`. **Perguntas guia do CSV:** Multi-tenant? Permission model? Subscription tiers? Integrations? Compliance?

**Secções obrigatórias CSV:** `tenant_model`; `rbac_matrix`; `subscription_tiers`; `integration_list`; `compliance_reqs`. **Ignoradas por tipo:** `cli_interface`; `mobile_first` (CLI não é foco; mobile-first opcional ? UI web/embed já coberto noutras secções).

### Visão do tipo de projeto

Produto **SaaS B2B/B2B2B** multitenant: cada **organização cliente** é uma unidade de isolamento de dados e faturação; **consumidor final** do WhatsApp não é tenant da plataforma, mas exige governança B2B2C (LGPD, políticas Meta). O desenho favorece **parceiros Meta**, ISV e operações centralizadas com **embed** no sistema do cliente.

### Modelo de tenant (`tenant_model`)

- **Tenant:** conta B2B (organização) com identificador estável; todos os dados operacionais (conversas, configurações, secrets por ambiente) **escopados** por tenant.
- **Sub-recursos por tenant:** números WABA / telefones, filas, fluxos, integrações; sem mistura de dados entre tenants (RLS / políticas Postgres + validação na API).
- **Ambientemente:** dev/stage/prod quando aplicável; segredos e webhooks **não** reutilizados entre tenants sem mapeamento explícito.
- **B2C como oferta:** entitlements que **bloqueiam** modo B2C ou capability sem contrato (já alinhado ao checkpoint).
- **Hierarquia explícita org ? WABA(s) ? número(s):** o *tenant* de isolamento e faturação é a organização; WABA e telefone são recursos **da** org (não tenants paralelos), com IDs Meta estáveis e regra de ciclo de vida (onboarding, desconexão, troca de número).
- **Escopo por camada:** deixar claro o que é *org-wide*, *WABA-scoped* e *phone-scoped* (webhooks, envio/recebimento, templates, métricas, auditoria) para não assumir um único nível de ?tenant?.
- **Entitlements vs objeto comercial:** amarrar limites de plano ao nível **org** e/ou **WABA** (volume, ambientes, integrações) para evitar ambiguidade entre faturação e recursos.

### Matriz de permissões (`rbac_matrix`)

| Papel (exemplo) | Criar/editar fluxos | Publicar | Ver inbox todas as filas | Configurar embed | Uso / faturação | Admin OAuth/webhooks |
|-----------------|---------------------|----------|----------------------------|------------------|-----------------|----------------------|
| **Admin tenant** | sim | sim | sim | sim | ver uso e faturação | sim |
| **Operador** | conforme política | opcional | filas atribuídas | leitura | ver uso (opcional) | não |
| **Atendente** | não | não | filas atribuídas | não | não | não |
| **Leitura / auditoria** | não | não | read-only | não | metadados / relatórios conforme política | não |
| **Finanças (read-only)** | não | não | não | não | sim (contrato, uso, exportações) | não |
| **Parceiro / suporte (diagnóstico)** | não | não | read-only limitado / impersonação auditada | não | metadados mínimos para incidente | não |

*Detalhe de papéis finos = FR no backlog; a matriz fixa **least privilege**, separação operação vs faturação, e evita ?Admin temporário? por falta de linha para parceiro ou finanças.*

### Planos e níveis (`subscription_tiers`)

- **Entitlements por plano:** limites de **fluxos avançados**, **mensagens/volume**, **mensagens de modelo**, uso de **agente** (F2), **integrações / orquestrador** (F3), **SLA** comercial opcional.
- **Primitives comerciais (enterprise):** além do ?menu? de planos, prever **commit** (prazo, mínimo, renovação, *true-up* quando aplicável) e **medição de uso** (mensagens, API, throughput, WABA) com política de **overage** e transparência de faturação; **seat** só quando o valor for por identidade (RBAC/auditoria/suporte nomeado), não como proxy único de tráfego WhatsApp.
- **Por conta/piloto:** overrides negociados documentados; evitar surpresa de upgrade (gate alinhado ao passo 6).
- **SKUs B2B vs B2C:** separados quando B2C existir; KPIs próprios (checkpoint).

### Lista de integrações (`integration_list`)

| Categoria | Integrações / fronteiras |
|-----------|---------------------------|
| **Canal** | Meta WhatsApp Cloud API, webhooks assinados, coexistência/embedded signup conforme produto |
| **Auth** | OAuth 2.0 / OIDC (stack alvo); tokens Meta por tenant |
| **Dados** | PostgreSQL; export/portabilidade (LGPD) |
| **Automação (F3)** | N8N ou similar; webhooks de saída; MCP/API conforme docs modulares |
| **Agentes** | Serviços externos (a2a, chat-completions); agente leve + ferramentas no núcleo |

*Tokens Meta e segredos de canal ficam **escopados** por org e por WABA/número onde a API assim exigir; responsabilidade quando um parceiro configura o canal em nome do cliente fica em contrato + trilho de auditoria (ver break-glass).*

### Requisitos de compliance (`compliance_reqs`)

- **LGPD:** DPA, ROPA/subprocessadores, direitos do titular, retenção ? ver **Domain-Specific Requirements (passo 5)**.
- **Meta / WABA:** políticas, templates, quality rating, opt-in ? requisitos de produto monitorizáveis.
- **Break-glass (fornecedor):** acesso emergencial para suporte/incidente com duração, aprovação do cliente, trilho de auditoria e base legal ? alinhado a LGPD e à matriz de papéis.
- **Acessibilidade:** WCAG no embed onde assumido ? jornadas passo 4 / domínio.

### Considerações de arquitetura técnica

- **Multi-tenant por construtor:** Postgres com RLS ou equivalente; claims OAuth com `tenant_id`; nunca confiar só no path da URL.
- **API pública:** rate limit, versionamento, erros documentados; idempotência em envio (passo 6 / integrações).
- **Observabilidade:** métricas por tenant; SLIs do Anexo A.

### Implementação (notas)

- **Não exigido por este tipo:** interface CLI primária; app mobile nativo first (embed/responsive suficiente para MVP).

### Refinamento ? Advanced Elicitation + Party Mode (passo 7)

**Vozes:** **Mary** ? org vs WABA e faturação; parceiro/reseller fora ou dentro do produto; break-glass; entitlements ao nível org vs WABA. **Winston** ? tenant = org com hierarquia org ? WABA ? telefone; escopo por camada. **John** ? linhas Parceiro/suporte e Finanças; coluna uso/faturação; regra de composição de papéis. **Victor** ? *subscription_tiers* necessário mas não suficiente; **commit + usage** para enterprise; seat condicional. **Murat** ? provas mínimas RLS (leitura/escrita cross-tenant), RBAC intra-org, claim vs URL.

**Síntese:** a ronda **preenche** o modelo de tenant (hierarquia Meta), **expande** a matriz para B2B2B real, **ancora** compliance de acesso emergencial e **explicita** primitives comerciais e provas de isolamento sem substituir o passo 8 (scoping).

---

## Project Scoping & Phased Development (passo 8)

**Relação com o documento:** formaliza decisões já presentes em **Product Scope (passo 3)**, **Executive Summary**, **Innovation (passo 6)** e **Checkpoint**; serve como âncora única para MVP vs pós-MVP e para riscos de scope.

### MVP Strategy & Philosophy

**MVP Approach:** combinação de **problem-solving MVP** (reduzir trabalho manual e caixa negra do WhatsApp com fluxos por regras e inbox) com **platform MVP** (multitenant, OAuth/OIDC, webhooks Meta, API e observabilidade por tenant como base reutilizável para F2/F3). **Validated learning** via **1?2 pilotos** com baseline e gates do passo 3/6 ? não ?feature completa? no primeiro corte.

**Resource Requirements (orientação):** equipa enxuta típica de produto **brownfield** ? backend (API, canal Meta, dados), frontend/embed, plataforma/observabilidade e migração legado ? stack alvo; produto/suporte para runbooks e piloto. Tamanho exato **não fixado** neste PRD; se recursos forem menores que o planeado, a **sequência** mantém-se: cortar profundidade de **F3** e automações não essenciais no MVP, **não** cortar isolamento tenant nem trilho de webhook/envio fiável.

**Stack do piloto (brownfield):** declarar explicitamente **qual runtime está em produção** durante o piloto (legado vs stack alvo, ou coexistência por caminho) e a **fronteira de responsabilidade** entre eles (auth, tenancy, filas, segredos, observabilidade) para evitar dois ?produtos? implícitos. **Critérios de saída** do piloto: período de observação, SLIs mínimos acordados, decisão **go / no-go / estender** e plano para não ficar indefinidamente em estado híbrido (paridade de dados, rollback, critério de desligar legado).

**Comercial (MVP):** **medição de uso** (eventos, quotas, agregação por tenant) como **fonte da verdade** no núcleo; **faturação end-to-end** e contratos refinados podem ser **posterior** ao ship do piloto. Para 1?2 pilotos iniciais, cobrança pode ser **manual** (PO, link, nota) desde que o sistema **registe e limite** uso ? evita inflar o MVP com ?billing completo? antes de validar o motor económico.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

- **Consumidor final (B2B2C):** contacto no WhatsApp com resposta por regras, handoff explícito para humano quando necessário (Marina ? caminho feliz e recuperação de atraso).
- **Operador / admin:** construir e publicar fluxos, permissões, inbox/embed no contexto do cliente (Rafael).
- **Integrador técnico:** OAuth, sandbox, webhook verificável, envio com idempotência e erros documentados (primeira mensagem fim a fim).
- **Suporte / operações:** investigação por tenant com logs correlacionados e separação de culpa Meta vs plataforma vs cliente (mínimo viável).
- **Comprador (financeiro):** no MVP, **relatórios anti-vanity** e visibilidade de uso conforme sucesso de negócio; **papéis/permissões ?Finanças?** e jornadas de compra self-serve completas podem ficar **mínimas** se o piloto for assistido ? calibrar no primeiro tenant.
- **Onboarding:** para os primeiros pilotos, assumir **white-glove** (implantação guiada) aceitável; **self-serve** mínimo é objetivo de produto, não obrigação de corte do piloto.

**Must-Have Capabilities:**

- **Canal:** apenas **WhatsApp** (Cloud API / BSP) com ingestão de webhooks e envio com política de retries/429.
- **Autenticação e tenant:** **OAuth 2.0 / OIDC**, claims com `tenant_id`, **RLS / validação** em todas as camadas; hierarquia **org ? WABA ? número** onde aplicável ao produto.
- **Automação MVP:** **chatbot por regras** (fluxos), **sem LLM como núcleo**; ações por regra (mensagens, tags, handoff).
- **UI:** **painel embedded** (inbox / operação) responsivo; não exigir app mobile nativo no MVP.
- **Observabilidade:** métricas por tenant (mensagens, conversas, handoffs, erros de canal) e **SLIs** alinhados ao **Anexo A**; correlação `trace_id` / `tenant_id`.
- **Compliance baseline:** bases legais e finalidades **mapeáveis** por fluxo; políticas Meta (templates, opt-in, quality) como requisitos monitorizáveis. **Direitos do titular / export:** no **primeiro corte de piloto**, DSAR e portabilidade podem ser **processo assistido** (runbook + export pontual por operações/eng) com trilho de auditoria; **automatismo self-serve completo no produto** é desejável mas não deve bloquear aprendizagem ? escalar para produto quando o volume exigir.
- **Migração:** marcos de **paridade** e rollback verificável entre legado e stack alvo ? não bloquear MVP de piloto se o piloto correr ainda no legado, mas **critérios de cutover** explícitos antes de ?só alvo?.

**Explicitamente fora ou adiado no MVP:** integração profunda com ERP; **agente LLM** como núcleo; **orquestrador** (N8N) além do mínimo necessário para o próprio produto; canais além do WhatsApp; oferta **B2C** dedicada; CLI primária; **modelo partner/revenda** completo (billing multi-tenant para parceiro) salvo decisão explícita de contrato ? default **canal direto** no núcleo do piloto.

### Definition of Done (MVP) ? evidência (não só documentação)

- **Isolamento:** prova automatizada ou integração que **nega** leitura/escrita cross-tenant (API + estado em DB/RLS).
- **Webhook:** testes do handler real com **assinatura válida/inválida** e roteamento ao tenant correto antes de persistir.
- **Pipeline:** evento webhook fixture ? artefato persistido com `tenant_id` e correlação (idempotência onde aplicável).
- **Operador ? publicar:** cenário que liga **publish** ao efeito esperado **sem** vazamento entre tenants.

### Piloto concluído (gates)

Critérios mensuráveis acordados (duração, volume mínimo, incidentes, tempo até primeiro valor), **sign-off** do sponsor/comprador e regra **go/no-go** para escalar ou repetir piloto ? alinhado a **Business Success** e **gates** dos passos 3 e 6.

### Post-MVP Features

**Phase 2 (Growth ? agente):**

- **Agente inteligente** com treino/uso, políticas no produto, custo e qualidade mensuráveis (gates do passo 6).
- Relatórios e SKUs alinhados a **custo por conversa** e correção humana onde aplicável.

**Phase 3 (Expansion ? orquestração):**

- **Orquestrador de integrações** (N8N ou similar); **pelo menos uma integração piloto** com cliente; lead time e falhas como métricas de sucesso.
- Profundidade adicional de **automação de processo** e, quando fizer sentido, **commit/usage** enterprise (passo 7).

**Vision (além da fase 3):** multi-canal; motion **B2C** com entitlements próprios; ofertas multi-tenant vs dedicado; maturidade de NRR/upsell ? conforme **Product Scope ? Vision** e classificação.

### Risk Mitigation Strategy

**Technical Risks:** dependência e volatilidade **Meta** ? abstração versionada, separação de culpa em incidentes, filas e política de quota; **migração** ? paridade de dados, reconciliação antes de cutover, pré-mortem de split-brain (passo 3/6). **Agentes (F2):** complexidade fora do core, contratos e isolamento de falha.

**Market Risks:** commoditização de conectores WhatsApp ? diferenciação por **governança B2B2C**, **embed**, **honestidade de faseamento** e métricas anti-vanity; validação por **piloto com baseline** e North Star económica.

**Resource Risks:** menos capacidade que o planeado ? **reduzir escopo de F3 e nice-to-have do MVP**, manter **jornadas críticas** e **isolamento tenant**; operações manuais temporárias (ex.: onboarding assistido) em troca de automação interna.

### Refinamento ? Advanced Elicitation + Party Mode (passo 8)

**Vozes:** **Mary** ? comprador no MVP; onboarding white-glove vs self-serve; definição de ?piloto concluído?; parceiro/revenda; LGPD pacote mínimo vs fora; marcos de migração/cutover. **John** ? must-have não virar ?enterprise de uma vez?; três frentes (observabilidade, compliance, migração) com mínimo aceitável; hierarquia org/WABA sem overbuild; **DSAR assistido no piloto** vs produto. **Winston** ? stack do piloto explícita; fronteira legado/alvo; go/no-go e fim de estado híbrido. **Victor** ? **metering** como âncora comercial do MVP; billing/contratos refinados depois; cobrança manual com uso medido. **Murat** ? DoD com provas (RLS, webhook, pipeline, publish).

**Síntese:** a ronda **desacopla** aprendizagem de piloto de **produto maduro num único corte**, **crava** medição de uso e critérios testáveis de ship, e **alinha** stack brownfield e gates de piloto sem antecipar o passo 9 (FRs).

---

## Functional Requirements (passo 9)

**Rastreabilidade:** cada FR material deriva da combinação de **User Journeys (passo 4)** (personas e capacidades nomeadas), **Product Scope / Scoping (passos 3 e 8)** e **SaaS B2B (passo 7)**; os **IDs de SLI** no **Anexo A** e os **NFRs (passo 10)** fecham atributos de qualidade. Não há ID de matriz formal FR?jornada neste PRD ? ao priorizar backlog, mapear FR?jornada nas *stories*.

**Contrato de capacidades:** os FRs abaixo definem **o quê** o produto deve permitir (atores e capacidades), **sem** prescrever implementação. **MVP** = núcleo alinhado a **Project Scoping (passo 8)**; capacidades marcadas **(F2)** / **(F3)** são pós-MVP explícitas. Qualquer funcionalidade não rastreável a um FR (ou a uma extensão acordada) **não faz parte** do escopo contratual deste PRD até revisão.

### Organização, inquilino e recursos do canal

- **FR1:** Administrador do tenant pode registar e gerir perfil e definições da organização.
- **FR2:** Administrador do tenant pode associar e gerir uma ou mais contas comerciais WhatsApp (WABA) e números sob a organização, com estado operacional visível (ativo, pendente, suspenso, etc.).
- **FR3:** A plataforma pode impor isolamento de dados por tenant em todas as áreas operacionais expostas a utilizadores e integrações.
- **FR4:** Administrador do tenant pode utilizar ambientes distintos (ex.: desenvolvimento / staging / produção) quando o produto os expuser, sem misturar dados entre ambientes.

### Identidade, acesso e credenciais

- **FR5:** Utilizadores podem autenticar-se através de fluxos OAuth/OIDC suportados pelo produto.
- **FR6:** Administrador do tenant pode atribuir papéis e permissões a utilizadores com princípio de menor privilégio.
- **FR7:** Utilizadores só podem aceder a recursos permitidos pelo seu papel dentro da sua organização.
- **FR8:** Operador autorizado pode rodar credenciais de API (criar novas, revogar antigas) com período de coexistência controlado para migração de integrações.
- **FR9:** Operador autorizado pode rodar segredos de verificação de webhooks com janela de coexistência que não interrompa entregas válidas de forma imediata e não controlada.
- **FR10:** Administrador do tenant pode emitir, rever e revogar chaves ou credenciais de integração conforme o modelo de acesso exposto pelo produto.

### Canal WhatsApp: eventos, envio e política do canal

- **FR11:** A plataforma pode receber eventos de entrada WhatsApp através de webhooks verificados e encaminhados ao tenant e contexto WABA/número corretos.
- **FR12:** A plataforma pode recusar ou ignorar entregas de webhook que falhem proteção contra reenvio ou critérios de frescura acordados.
- **FR13:** O pipeline de ingestão pode determinar de forma inequívoca o tenant (e, quando aplicável, WABA / ambiente) a partir do pedido recebido, antes de aplicar regras de negócio.
- **FR14:** Atores autorizados podem enviar mensagens de saída WhatsApp através da plataforma segundo política e permissões do tenant.
- **FR15:** Administrador do tenant pode gerir o ciclo de vida de mensagens de modelo (pedidos, estados de aprovação, uso) na medida exigida pelas políticas do canal, sem depender de ERP.
- **FR16:** Tenant pode configurar e monitorizar sinais relevantes a opt-in, qualidade e limites do canal conforme políticas aplicáveis.

### Inbox, conversas, filas e handoff

- **FR17:** Operadores podem ver uma inbox unificada das conversas dos números a que têm acesso.
- **FR18:** Operadores podem classificar conversas com etiquetas ou campos de triagem partilhados pela equipa.
- **FR19:** Operadores podem transferir o atendimento entre automação e humano preservando contexto suficiente para continuidade.
- **FR20:** Supervisor pode definir regras de encaminhamento, prioridade ou reatribuição entre filas ou agentes quando há handoff da automação para humanos.
- **FR21:** Operadores podem ver sinais operacionais sobre atrasos ou falhas do canal relevantes ao seu tenant, sem expor dados de outros tenants.

### Automação por regras (fluxos) e ciclo de vida

- **FR22:** Operadores podem construir e editar fluxos de conversa baseados em regras (sem motor LLM como núcleo no MVP).
- **FR23:** Operadores podem testar fluxos em pré-visualização ou sandbox antes da publicação.
- **FR24:** Operadores podem publicar fluxos com controlo de permissões e separação de ambiente.
- **FR25:** A plataforma pode registar versões ou alterações materiais de fluxos de forma auditável.
- **FR26:** A plataforma pode aplicar ações disparadas por regras (mensagens, etiquetas, handoff) segundo a configuração do tenant.
- **FR27 (F2):** Operadores podem configurar e treinar um agente inteligente com políticas e limites no produto, quando a fase estiver ativa.
- **FR28 (F3):** Organização pode orquestrar integrações externas através do módulo de orquestração quando a fase estiver ativa, incluindo pelo menos um percurso piloto acordado.

### Experiência embutida e confiança do contacto final (B2B2C)

- **FR29:** Tenant pode incorporar o painel operacional no workspace do cliente com contexto de sessão adequado.
- **FR30:** Contacto final pode perceber de forma clara se interage com automação ou com humano durante a conversa, incluindo transições.
- **FR31:** Contacto final pode receber explicação objetiva do tratamento de dados da conversa antes de interações que impliquem consentimento, quando aplicável.
- **FR32:** Contacto final pode optar por mensagens proativas e retirar o consentimento, com confirmação registada de preferências.
- **FR33:** Contacto final pode interromper categorias específicas de comunicação (ex.: marketing vs. transacional) sem perder canais essenciais de suporte acordados.
- **FR34:** Contacto final pode utilizar o painel embutido com suporte a critérios de acessibilidade declarados pelo produto para os componentes suportados (ex.: alinhamento a WCAG 2.2 AA onde assumido).

### API pública, integração e versionamento

- **FR35:** Integrador pode invocar APIs documentadas de envio e operações expostas com semântica de idempotência em operações mutáveis.
- **FR36:** Consumidor da API pode obter comportamento conforme uma versão declarada e suportada do contrato público.
- **FR37:** Consumidor pode antecipar ciclo de vida de versões (suporte, descontinuação, coexistência) para API e, quando aplicável, para formatos de eventos de webhook.
- **FR38:** Integrador pode usar ambiente de sandbox limitado ao tenant, sem acesso a dados de produção ou de outros tenants.
- **FR39:** Integrador ou operador técnico pode consultar histórico de entregas de webhooks e alinhar reenvios ou reconciliação quando o produto expuser essa capacidade.
- **FR40:** Consumidor da API pode receber semântica de erro documentada para falhas de autenticação, autorização e limitação de taxa, sem perda silenciosa de resultado para o tenant quando o produto se compromete com entrega visível.

### Medição de uso, planos, relatórios e operações comerciais

- **FR41:** A plataforma pode registar eventos de uso por tenant adequados a quotas e medição comercial (mensagens, operações-chave, agregações).
- **FR42:** Comprador ou utilizador com papel de finanças pode aceder a relatórios orientados a valor (horas, capacidade, retrabalho) e evitar métricas exclusivamente vanity, quando o produto os expuser.
- **FR43:** Administrador pode configurar limites de plano ou entitlements e receber alertas antes de bloqueios ou degradação quando configurado.
- **FR44:** Utilizador autorizado pode exportar extratos de utilização e dados de faturação com identificadores estáveis para reconciliação com sistemas externos.

### Governança de dados, privacidade e pedidos do titular

- **FR45:** Tenant pode mapear finalidades e bases legais por fluxo ou tratamento conforme o modelo de governança suportado pelo produto.
- **FR46:** Utilizador autorizado pode iniciar e acompanhar pedidos de direitos do titular (acesso, portabilidade, eliminação) com estados e trilho de auditoria; no MVP o percurso pode ser assistido por operações conforme passo 8.
- **FR47:** Tenant pode apresentar lista de sub-processadores relevante com indicação de versão ou data de atualização.
- **FR48:** Administrador do tenant pode configurar regras de retenção por categoria de dado dentro dos limites da política do produto.
- **FR49:** A plataforma pode aplicar ou orquestrar aplicação de retenção e reportar resultados agregados sem exposição indevida de conteúdo.
- **FR50:** Responsável de conformidade ou operador autorizado pode registar e consultar registo de consentimento, opt-in ou opt-out por contacto, para mensagens proativas e tratamento contínuo, além do fluxo de pedidos do titular.

### Suporte, auditoria e operação da plataforma

- **FR51:** Suporte da plataforma pode investigar incidentes no âmbito de um tenant com identificadores de correlação e classificação de culpa (Meta vs plataforma vs cliente).
- **FR52:** Auditor autorizado pode consultar registos de auditoria filtrados por ator ou por capacidade para validar fronteiras de permissão.
- **FR53:** Processo suportado pelo produto pode permitir acesso emergencial (break-glass) com aprovação, duração limitada e trilho de auditoria, alinhado a compliance.
- **FR54:** Administrador da plataforma ou fluxo acordado pode executar ações de alto risco apenas com registo imutável ou apêndice auditável conforme política do produto.

### Refinamento ? Advanced Elicitation + Party Mode (passo 9)

**Vozes:** **John** ? lacunas: gestão multi-número/WABA, etiquetas de triagem, registo legal por contacto, estado de pedido LGPD ao titular, filas/supervisão, ciclo de templates Meta, reconciliação de webhooks, alertas de quota. **Winston** ? rotação de credenciais, anti-replay, resolução de tenant na ingestão, versionamento de API e ciclo de vida. **Sally** ? transparência bot/humano, explicação de tratamento, opt-in/out granular, WCAG no embed. **Mary** ? jornada export DPO, pacote de export, subprocessadores, retenção configurável, aplicação de retenção, extratos para reconciliação financeira. **Murat** ? sandbox isolado, idempotência como contrato testável, auditoria por ator e por capacidade.

**Síntese:** a ronda **fecha lacunas** de operação (etiquetas, filas, templates, quotas), **reforça** fronteiras técnicas (credenciais, replay, versão) e **B2B2C** (confiança e acessibilidade), e **ancora** LGPD e finanças como **capacidades** (incluindo DSAR assistido no MVP). **F2/F3** ficam explícitas em FR27?28 para não diluir o núcleo MVP.

---

## Non-Functional Requirements (passo 10)

**Âmbito:** RNFs definem **quão bem** o sistema deve comportar-se (atributos de qualidade), não **o quê** faz ? complementam os **FRs**. Abordagem **seletiva:** só categorias relevantes a BSP multitenant, LGPD, canal Meta e embed B2B. **Alvos numéricos** de disponibilidade, latência, ingestão e frescura do painel permanecem como **fonte primária** na **Anexo A (SLI/SLO)**; os itens abaixo **alinham, estendem ou operacionalizam** verificação sem duplicar a tabela salvo referência explícita.

### Desempenho e latência

- **NFR-PERF-01:** Rotas críticas (ingest de webhook, envio de mensagem, autenticação) devem manter-se dentro dos **SLO de latência** definidos no **Anexo A** (`API-lat`), com **p95** monitorizado por rota e revisão quando degradar face ao baseline do piloto.
- **NFR-PERF-02:** O tempo entre evento de canal e **visibilidade no painel do operador** deve cumprir o SLO **`OBS-fresh`** do Anexo A (calibrar p95 em piloto).
- **NFR-PERF-03:** Com APIs Meta e webhooks saudáveis no perfil de teste acordado, o processamento de webhook (**ack** e persistência mínima em fila/BD) deve manter-se dentro do limiar acordado no **WH-ingest** / ingestão interna (referência Anexo A e runbook de carga).

### Fiabilidade e disponibilidade

- **NFR-REL-01:** A API de produto deve cumprir o SLO **`API-avail`** (Anexo A) em janela rolling; política de **error budget** e consequências (freeze de mudanças, página) conforme Anexo A e runbooks.
- **NFR-REL-02:** Falhas de entrega atribuíveis à plataforma devem ser tratadas conforme **`CHAN-fail`** (baseline por piloto, postmortem quando aplicável).
- **NFR-REL-03:** Após interrupção que gere backlog de webhooks, o sistema deve **drenar** o backlog dentro de **RTO** acordado (ex.: percentil de eventos processados em N minutos após recuperação), **sem perda** após persistência na fila de entrada; p99 da latência de processamento durante a drenagem não deve exceder múltiplo documentado do baseline sem escalação.
- **NFR-REL-04:** A migração legado ? stack alvo deve respeitar **`MIG-parity`** (Anexo A) antes de cutover; rollback verificável documentado.

### Segurança e proteção de dados

- **NFR-SEC-01:** Tráfego exposto à internet (API, painel, webhooks, OAuth) deve usar **TLS 1.2 ou superior** com certificados válidos; **0** endpoints de produção em TLS obsoleto em auditoria periódica.
- **NFR-SEC-02:** Dados sensíveis em repouso (BD, objeto, backups) com **criptografia gerida** (ex.: AES-256 ou equivalente) e chaves sob gestão adequada (KMS/secret manager), sem segredos estáticos em repositório.
- **NFR-SEC-03:** Segredos de OAuth, verificação de webhooks e chaves de API seguem **rotação programada** (ex.: ? 90 dias ou política do fornecedor) e **rotação de emergência** (ex.: ? 24 h após classificação de incidente), com registo de data da última rotação por segredo.
- **NFR-SEC-04:** Sessões de operador/admin: **timeout por inatividade** e vida máxima de sessão conforme política de risco; OAuth com refresh/rotação e **revogação** aplicável dentro de janela documentada após logout administrativo forçado.
- **NFR-SEC-05:** APIs autenticadas aplicam **limite de taxa por `tenant_id`** com resposta **429** documentada e cabeçalho **`Retry-After`** quando aplicável; ingestão de webhooks com **proteção contra abuso** entre tenants (quota por tenant), com métricas que provem isolamento de cota.
- **NFR-SEC-06:** Em degradação ou indisponibilidade Meta, **sem perda silenciosa**: filas/backpressure com retenção mínima e **alertas** quando profundidade ou idade média exceder limiar; degradação documentada em runbook (alinhado a testes de caos).

### Multitenancy, quotas e fairness

- **NFR-FAIR-01:** Um tenant não pode degradar de forma sustentada o SLO de outros: limites de **concorrência** e/ou **WFQ** por tenant; com carga sintética de ?noisy neighbor?, o **p95 de latência** de tenants vizinhos não aumenta além de **?%** face ao baseline (valor a calibrar em teste de carga).
- **NFR-FAIR-02:** Após estouro de quota, o **enforcement** (primeira resposta consistente de recusa ou backpressure) ocorre dentro de **T segundos** (calibrar); taxa mínima documentada de enforcement correto na primeira tentativa subsequente.
- **NFR-FAIR-03:** Uso e custo **atribuíveis por tenant** (mensagens, chamadas API, armazenamento, compute relevante) com atualização em painel em **horas** (near real-time no núcleo); percentual mínimo de volume associável a `tenant_id` ou classificação explícita de ?não atribuível?; reconciliação periódica com totais agregados dentro de **±D%** ou processo documentado.
- **NFR-FAIR-04:** Dimensionamento com **folga** (ex.: utilização sustentada ? **U%** da capacidade validada em teste de carga) e capacidade de absorver **picos** burst sem violar latência acordada ou com modo degradado apenas para classes não críticas **documentado**.

### Observabilidade e operações

- **NFR-OPS-01:** Pipeline de release executa verificação sintética ou smoke dos **SLOs críticos** antes de promover artefacto (pass/fail explícito); falhas consecutivas em staging bloqueiam promoção até análise.
- **NFR-OPS-02:** **Testes de caos ou falha simulada** da integração Meta (timeouts, 5xx, indisponibilidade) em cadência documentada; sucesso = degradação graciosa, retries e **ausência de perda indevida** de estado conforme checklist.
- **NFR-OPS-03:** Logs de **auditoria** retidos o período mínimo da política (ex.: **R** meses) com **? 99,9%** de recuperabilidade em consultas típicas; exclusões antecipadas apenas com fluxo aprovado e registo; consultas administrativas padrão com **p95** de tempo de resposta documentado.
- **NFR-OPS-04:** Alertas em **100%** dos painéis críticos (burn rate, fila, falhas Meta) com **MTTD** máximo em cenários de teste injetado em staging; alertas P1/P2 com runbook e **ack** dentro de **N minutos** (SLA interno).
- **NFR-OPS-05:** **Separação de culpa** em incidentes (`meta`, `plataforma`, `cliente`, `indeterminado`) conforme critério documentado (Anexo A).

### Privacidade e operações LGPD (métricas operacionais ? não substituem parecer jurídico)

- **NFR-LGPD-01:** **ACK** de pedidos de direitos do titular em **? 24 h** úteis (ou janela comercial documentada); primeira resposta substantiva em **? 5 dias úteis** em **? 95%** dos casos; MTTR monitorizado mensalmente.
- **NFR-LGPD-02:** Entrega de **pacote de export** em **? 15 dias corridos** após confirmação de escopo/identidade (quando elegível), com **? 99%** sem retrabalho por formato; **100%** com checksum e log de auditoria.
- **NFR-LGPD-03:** Incidentes com impacto a dados pessoais: rascunho de comunicações (titulares/ANPD quando aplicável) em **? 24 h** da decisão de severidade; **100%** com linha do tempo numa ferramenta; revisão pós-incidente em **? 10 dias úteis** em **? 90%** dos casos.
- **NFR-LGPD-04:** Lista de **subprocessadores** atualizada em **? 10 dias úteis** após mudança material; **100%** com registo versionado; notificação proativa a clientes em mudança material; indicador de leitura/confirmação conforme processo comercial.

### Acessibilidade (painel embutido)

- **NFR-A11Y-01 (2.4.3):** Ordem de foco lógica nas rotas críticas do embed; **0** falhas bloqueantes em auditoria manual das jornadas prioritárias (Tab/Shift+Tab sem armadilha).
- **NFR-A11Y-02 (1.4.3 / 1.4.11):** Contraste mínimo **4,5:1** texto normal; **3:1** texto grande; estados e erros não dependem só da cor.
- **NFR-A11Y-03 (2.1.1 / 2.1.2):** Funções essenciais do painel operáveis por teclado; foco visível; sem armadilha de teclado em modais.
- **NFR-A11Y-04 (3.3.1 / 3.3.3):** Erros de validação com identificação textual e ligação programática ao campo quando aplicável.

### Integrações e resiliência de canal (Meta)

- **NFR-INT-01:** Política de **retry** e **backoff** para APIs Meta e filas internas alinhada a **429** / `Retry-After`; sem perda silenciosa de mensagens quando o produto assume entrega.
- **NFR-INT-02:** **Idempotência** e deduplicação de eventos conforme contrato do ingest (alinhado a FRs e DoD do passo 8).
- **NFR-INT-03:** Compatibilidade com **versão** declarada de API/contrato público (alinhado a FR36?FR37).

### Refinamento ? Advanced Elicitation + Party Mode (passo 10)

**Vozes:** **Winston** ? TLS, repouso KMS, rotação de segredos, sessão, rate limit por tenant, degradação Meta com filas e alertas. **Murat** ? gates de SLO em CI/staging, caos Meta, RTO de backlog de webhooks, retenção e consulta de auditoria, alertas P1/P2 com MTTD/ack. **Sally** ? WCAG 2.2 AA no embed: foco, contraste, teclado, erros (critérios WCAG referenciados nos NFR-A11Y). **Mary** ? tempos operacionais DSAR/export, incidente de dados e subprocessadores (percentagens e prazos operacionais). **Victor** ? noisy neighbor, latência de enforcement de quota, custo por tenant, headroom e burst.

**Síntese:** a ronda **liga** NFRs ao **Anexo A** (sem duplicar indefinidamente), **fecha** segurança operacional e **fairness** multitenancy, **torna auditáveis** LGPD e a11y, e **reforça** resiliência Meta e provas (caos, backlog, CI).

---

## Classificação do produto (iterada ? input GD-AGK + Party Mode 2026-04-17)

- **Tipo / GTM:** SaaS com foco **B2B e B2B2B**; **B2C possível**, mais raro, com oferta **posterior** via **marketing** (não é núcleo do go-to-market inicial).
- **Domínio:** Plataforma **horizontal** (**Tech**, ênfase **AITech** no que o produto entrega). **Nenhuma** vertical de mercado é pré-assumida no núcleo ? o ICP é refinado com pilotos independentemente do setor.
- **Contexto:** **Brownfield** (núcleo OpenBSP e documentação modular no repositório).

**Texto curto sugerido para o PRD (editar ao gosto):**

> Plataforma multitenant de orquestração de WhatsApp, fluxos e integrações, com camada de automação e agentes supervisionados (ênfase AITech). Posicionamento comercial principal: B2B/B2B2B. Uso B2C pode existir em fases futuras, com motion e requisitos próprios; fora do escopo do núcleo até decisão explícita de release.

---

## Checkpoint de decisões (GD-AGK ? 2026-04-17)

### Papéis: comprador, operador, consumidor final

**Intenção:** qualquer organização (ou pessoa jurídica) que necessite de mensageria e, mais tarde, do orquestrador â€” **aspiração horizontal**.

**Para o PRD (mais operacional):**

| Papel | Quem é | Contrato / suporte (ângulo) |
|--------|--------|-----------------------------|
| **Comprador** | Quem assina e paga (conta B2B). | Contrato de plataforma, SLA comercial, faturação. |
| **Operador** | Admins e atendentes do tenant (configuram fluxos, regras, embed, futuro agente). | Suporte operacional, documentação, permissões. |
| **Consumidor final** | Contacto no WhatsApp (cliente do teu cliente). | Experiência, opt-in/opt-out, tom e limites do bot/agente â€” responsabilidade partilhada com o tenant (controlador vs operador conforme desenho LGPD). |

**Hipótese em aberto:** segmentação comercial (PME vs enterprise) fica **a definir com os primeiros pilotos**; até lá o PRD assume **multi-tenant genérico** com limites por plano.

### ICP (tamanho / volume)

**Estado:** não há números fixos neste momento.

**Regra no PRD:** documentar **critérios de seleção dos primeiros clientes** (ex.: já usa WhatsApp oficial, tem dono para o projeto, volume suficiente para medir â€” a calibrar) em vez de faixa de receita obrigatória.

### MVP vs fases (canal, automação, integrações)

| Fase | Conteúdo (definição GD-AGK) |
|------|-----------------------------|
| **MVP** | **BSP** + **chatbot** (fluxos/regras) + **painel embedded**. Canal **só WhatsApp**. Atendimento **bot 24h com parte híbrida** (regras primeiro; humano quando aplicável). **Ações:** inicialmente por **regra** (fluxo), não por agente LLM. |
| **Fase 2** | **Agente inteligente** (treino/uso: usabilidade, o que responder, contexto do sistema do cliente para o cliente dele). |
| **Fase 3** | **Orquestrador de integrações** â€” **N8N ou similar** (integrações compostas). |

**Nota de alinhamento:** esta cadência substitui para documentação atual qualquer roadmap anterior onde integração/orquestração apareça antes do agente; o PRD segue **esta** sequência até nova decisão explícita.

### "Centralizador" vs fontes de conhecimento

- **Centralizador (v1):** uma **visão unificada no produto** das conversas e estados no **WhatsApp** (inbox / histórico operacional no BSP + painel/embed) â€” **não** significa "único CRM do mundo" na v1.
- **Outras fontes/canais:** **fora do âmbito v1**; avaliar depois.
- **"Fonte da verdade" para o que o bot diz:** no MVP **chatbot por regras**, o conteúdo vem da **configuração que o cliente monta** (scripts, FAQs, fluxos). **Não** é obrigatoriamente treino de LLM no MVP â€” isso entra com clareza na **Fase 2**. Se a dúvida era *quem treina o agente*: **sim, o cliente (operador) com apoio do produto**, na fase em que o agente existir.

### ERP / inputar / buscar (quem faz o quê)

A pergunta anterior era: *que sistema atualizar primeiro e quem executa a ação?*

Com a tua resposta (**ações por regra no início**), no **MVP** o desenho típico é: **regras de fluxo** disparam passos (mensagens, tags, handoff humano); **integração profunda com ERP** fica **ligada à Fase 3 (orquestrador)** salvo exceções explícitas. O PRD deve listar **uma integração piloto** quando escolheres o primeiro cliente.

### KPIs de piloto (proposta para validares)

Medir **antes/depois** num ou dois tenants, com baseline explícito:

1. **Tempo até primeira resposta útil** (segundos/minutos; p50 e p90) â€” consumidor final.  
2. **Taxa de conversas resolvidas só com fluxo/regra** (sem humano), quando o desenho permitir medição.  
3. **Incidentes de integração Meta** (webhooks falhados / mensagens não entregues) por 1k mensagens â€” **confiança no canal**.  
4. **Horas/semana** que o cliente reporta em trabalho manual **antes vs. depois** (inquerito estruturado no piloto).  
5. A partir da **Fase 2:** **custo médio por conversa** (LLM + infra) e, se aplicável, **taxa de correção humana** (ex.: o agente errou e precisou de override).

### "Uso" por tenant (observabilidade mínima v1)

Sem ser vanity: **por tenant e por dia (ou hora)** â€” **mensagens inbound/outbound**, **conversas abertas/fechadas**, **handoffs para humano**, **erros de envio/API Meta**. Opcional: **tempo médio de fila** antes da primeira resposta humana.

### Churn e "crescimento mau" (definições propostas)

- **Churn de logo:** tenant deixou de pagar / encerrou conta no período.  
- **Churn de receita:** variação MRR atribuível a downgrade ou saída.  
- **"Crescimento mau" (alerta):** novos logos **e** (a) **queda de utilização** (mensagens/conversas per capita) em 30?60 dias, ou (b) **subida de tickets de suporte críticos** / falhas de canal, ou (c) **NRR inferior a 100%** com aumento de aquisição (crescimento que não retém).  
- **NRR** (expansão â€” churn â€” downgrade) quando houver dados de upsell.

### Limites do agente para o consumidor final (configurável)

**Direção:** configurar **boa parte** â€” marca, tom, o que pode/não pode dizer, escalação, uso de dados.

**Dois planos no PRD:**

1. **Produto (OpenBSP / portal):** requisitos funcionais do **módulo de políticas / construtor de comportamento do bot-agente** (papéis, revisão, ambientes).  
2. **BMAD "Agent Builder" no repositório:** o skill **`bmad-agent-builder`** (ex.: `.cursor/skills/bmad-agent-builder/SKILL.md`) serve para **criar agentes BMAD no Cursor** (documentação, skills de equipa) ? **não** substitui a UI que o teu cliente usa para configurar o bot. Para instrução passo a passo no ecossistema BMAD de desenvolvimento, usa esse skill quando quiseres **outro agente de apoio no IDE**; para o **produto**, os requisitos ficam no PRD como **módulo de configuração do agente conversacional**.

---

## Polish do documento (passo 11)

**O que mudou neste passe:** **Mapa do documento** (índice com ordem e leitura sugerida); **fonte canónica** de MVP/fases (Checkpoint + passo 8) no **Product Scope**; **nota de rastreabilidade** antes dos **Functional Requirements** (ligação a jornadas, scoping e NFRs; matriz FR?jornada na story); cabeçalhos **SaaS B2B** e **Classificação/Checkpoint** normalizados onde o encoding quebrava o título.

### Refinamento ? Advanced Elicitation + Party Mode (passo 11)

**Vozes:** **John** ? índice com âncoras, fonte única do MVP, nota de rastreabilidade FR/jornada. **Paige** ? mapa no topo com ordem estável, uma linha por bloco sobre o que o leitor obtém, leitura executivo vs implementação. **Winston** ? cabeçalhos `##` consistentes para *chunking* previsível em ferramentas e agentes. **Sally** ? leitura B2B2C não se perde antes de **User Journeys**; mapa aponta onde está a narrativa do contacto final.

**Síntese:** o polish **reduz fricção de navegação** (humanos e LLMs), **explicita precedência** entre secções sobre o mesmo tema (escopo) e **prepara** epicagem sem exigir matriz ID?ID no PRD ? adiada para *backlog* com traço claro às jornadas.

**Brainstorming:** `documentCounts.brainstorming: 0` ? sem reconciliação de documento de brainstorming neste projeto.

---

## Conclusão do workflow PRD (passo 12)

O fluxo **`bmad-create-prd`** (BMad Method) está **encerrado** para este artefacto. O PRD serve de base a **UX**, **arquitetura**, **épicos/histórias** e desenvolvimento; quando as decisões de produto mudarem, **atualizar o PRD** (no ecossistema BMad: `bmad-edit-prd`).

**Decisões complementares (ambiguidades, roadmap em três entregas, LGPD DSAR híbrido, parceiro por fases):** registo vivo em **`_bmad-output/planning-artifacts/prd-decisoes-registradas-gd-agk.md`**. Não substitui os requisitos deste PRD; **informa** backlog, contratos e possíveis revisões futuras do documento.

### Próximos passos recomendados (BMad / equipa)

| Prioridade | Sugestão | Notas |
|------------|----------|--------|
| Validação opcional | **`bmad-check-implementation-readiness`** ? menu **[IR]** Check Implementation Readiness | Alinha PRD com UX, arquitetura e épicos antes de investir pesado ? *mais útil quando esses artefactos existirem*. |
| Solutioning | **`bmad-create-architecture`** ? **[CA]** Create Architecture | ADRs, multitenancy, Meta, migração legado ? alinhado ao `platformTarget` deste PRD. |
| Planning UI | **`bmad-create-ux-design`** ? **[CU]** Create UX | Recomendado se o embed for peça central da proposta. |
| Descomposição | **`bmad-create-epics-and-stories`** ? **[CE]** | Tipicamente após arquitetura/UX alinhados aos FR/NFR. |
| Orientação | **`bmad-help`** | Catálogo em `_bmad/_config/bmad-help.csv`. |

### Validação (escolha da equipa)

- **Opção A ? Readiness:** correr **Check Implementation Readiness** quando existirem PRD + épicos/arquitetura para fechar lacunas antes do build.
- **Opção B ? Avançar:** passar a arquitetura/épicos/sprint sem gate formal e rever readiness mais tarde.

### Riscos a fechar cedo (pós-PRD)

Checklist técnico ? complementa *spikes* e desenho:

- **Isolamento:** provas RLS + `tenant_id` só em claims verificáveis (nunca tenant inferido só pela URL).
- **Webhook Meta:** matriz assinatura, roteamento org?WABA?número, idempotência e eventos duplicados/fora de ordem.
- **Brownfield:** gate **MIG-parity**, fronteira legado vs stack alvo no piloto, rollback antes de cutover.

### Evitar ?PRD na prateleira?

- **Piloto** com critérios de encerramento explícitos; **métricas** de valor em cadência fixa; **donos** do documento e ligação à priorização (produto/negócio).

### Refinamento ? Advanced Elicitation + Party Mode (passo 12)

**Vozes:** **John** ? épicos com critérios de aceite e rastreabilidade; arquitetura e ADRs; validação formal; sprint zero com *spikes*. **Murat** ? provas de isolamento, matriz de webhook, **MIG-parity** e brownfield. **Victor** ? piloto com time real, KPIs com decisões explícitas, governo do PRD e alinhamento a metas.

**Síntese:** a ronda **encerra** o CP com **próximos passos BMad nomeados**, **riscos verificáveis** após congelar requisitos e **hábitos** que mantêm o PRD **vivo** até à implementação.
