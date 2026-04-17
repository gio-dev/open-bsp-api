# MR · DR · TR ? Relatório aprofundado

**Contexto:** Plataforma B2B2B em camadas ? OpenBSP como núcleo WhatsApp; SKUs Empresa 1 (só WA multi-pessoas + iframe), Empresa 2 (WA + agente IA com treino e aprovação), Empresa 3 (Empresa 2 + integração documental/sistemas via automação modular).  
**Parceiro:** GD-AGK  
**Data:** 2026-04-17  
**Persona:** Mary (analista BMAD) ? evidências com fontes web onde aplicável; **validar números e políticas** com documentação oficial Meta/LGPD antes de decisões contratuais.

---

# Parte A ? MR (Market Research) aprofundado

## A.1 Segmentação de mercado (quem compra de ti)

| Segmento | Características | Implica para o produto |
|----------|-----------------|-------------------------|
| **Agências / integradores** | Revendem para vários clientes finais; precisam multi-tenant e white-label | Onboarding repetível, limites por plano, **iframe** para encaixar no ?sistema do cliente? |
| **ISV vertical** (saúde, logística, etc.) | Querem WA **dentro** do produto próprio | APIs estáveis, SLAs, **embed** sem fugir da marca deles |
| **Enterprise direto** | Poucos tenants, alto ticket | **Compliance**, auditoria, opção de isolamento forte (ver TR) |

**Teu posicionamento** (pelo que descreveste): estás entre **agência tech** e **fabricante de plataforma** ? o SKUs 1/2/3 permitem **subir na conta** sem trocar de stack técnica.

## A.2 Categorias concorrenciais (mapa mental)

1. **CPaaS globais** (MessageBird, Twilio, etc.) ? largura de canais; WhatsApp é uma feature entre muitas.  
2. **Agregadores / BSP-friendly** ? onboarding Embedded Signup, CRM embutido, automações. Referências de mercado falam em **redução de tempo de setup** e **multi-tenant** para parceiros ([ex.: narrativas de embed em SaaS](https://chakrahq.com/article/whatsapp-api-partner-integration-solution-embedded/)).  
3. **CRM com WA nativo** (HubSpot, Zoho, players locais) ? concorrem na **experiência unificada**, não na flexibilidade do teu **N8N + módulos**.  
4. **Automação genérica** (Make, n8n cloud, Zapier) ? concorrem na **integração**, não no **compliance WA + conversa unificada** se tu entregares pacote completo.

**Diferenciação sustentável** para ti: **pacote ?canal + governança de IA + integração modular?** com **gate de aprovação** e **catálogo de conectores** ? não ?mais um painel de API?.

## A.3 Modelo de receita e sensibilidade a custo Meta

- A Meta cobra pelo uso da **WhatsApp Business Platform** com regras que **mudam** (categorias de conversa/marketing, possíveis transições de modelo de faturação). Há fontes que mencionam **janela de 24h** e categorias (Marketing, Utility, Authentication, Service) com **preços por país** ([calculadoras e guias de terceiros](https://whautomate.com/tools/whatsapp-business-api-pricing-calculator); [documentação Meta ? pricing](https://developers.facebook.com/docs/whatsapp/pricing/conversation-based-pricing/) ? ver nota *deprecated* e **sempre** a página atual da Meta).

**Implicação de produto:** o teu **plano comercial** deve separar claramente:  
- **Receita tua** (mensalidade plataforma, setup, integrações)  
- **Custo Meta** (repasse ou ?cliente paga direto? conforme teu papel BSP ? ver [discussões públicas sobre tiers de parceiros](https://www.wuseller.com/whatsapp-business-knowledge-hub/whatsapp-business-solution-providers-partner-tiers-2026/) ? **confirmar na Meta**)

Sem essa separação no **SKU**, margem e previsibilidade quebram.

## A.4 Jobs-to-be-done e critérios de compra (B2B2B)

| Job | Critério típico de decisão |
|-----|----------------------------|
| ?Lançar WA rápido sem projeto de 6 meses? | Time-to-value, documentação, suporte de onboarding |
| ?Não passar vergonha com IA? | Sandbox, aprovação, logs, possibilidade de **human takeover** |
| ?Documento que chega no Whats vai para o ERP? | Confiabilidade, retries, mapeamento de campos, **não** só ?tem integração? |

## A.5 Tendências e incerteza (monitorizar)

- **Marketing Messages API** e mudanças frequentes de produto Meta ? exige **roadmap de compliance** no teu lado ([ex.: blogs de fornecedores em 2026](https://saleshiker.com/blog/february-2026-whatsapp-update-marketing-messages-api-embedded-signup/)).  
- **IA regulada e expectativa de explicabilidade** ? reforça o teu **fluxo Empresa 2** (treino ? aval ? go-live).

## A.6 Síntese MR ? oportunidades e riscos

**Oportunidades:** escada 1?2?3 clara; **iframe** reduz atrito; **BSP/Embedded** já é linguagem de mercado.  
**Riscos:** commoditização de ?ligar WhatsApp?; **dependência de política Meta**; **subestimar custo de suporte** em integrações (Empresa 3).

---

# Parte B ? DR (Domain Research) aprofundado

## B.1 Vocabulário e fronteiras do domínio (WABA / Cloud API)

- **WABA** (WhatsApp Business Account), **número**, **template**, **janela de serviço (24h)** são conceitos **operacionais** que o teu cliente final vai confundir ? o teu produto precisa **guias** por SKU.  
- **Embedded Signup** e papéis de **BSP/Tech Provider** afetam **quem paga o quê** ? domínio comercial + domínio técnico (alinhado ao que o OpenBSP já trata em `whatsapp-management`).

## B.2 Políticas Meta (o ?regulador? do canal)

- Respostas **fora da janela** exigem **templates** aprovados; categorias incorretas geram **rejeição ou bloqueio**.  
- Documentação oficial: [WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp/overview/) ? **fonte única** para regras que vão para **checklist de go-live** no teu portal.

*Nota:* blogs de terceiros sobre ?preço por mensagem vs conversa? divergem; **nunca** uses número de blog em contrato sem cruzar com a Meta.

## B.3 LGPD (Brasil) ? atendimento, chatbots e retenção

Fontes jurídicas e de compliance resumem:

- **Consentimento** claro quando há coleta além do estritamente necessário ao atendimento; informar **finalidade** ([artigos sobre chatbots e LGPD](https://parceriajuridica.com.br/como-a-lgpd-impacta-o-uso-de-chatbots-em-empressas/); [coleta via chatbots](https://lawinnovation.com.br/lgpd-como-coletar-corretamente-os-dados-pessoais-via-chatbots/)).  
- **Minimização e retenção**: não guardar indefinidamente; políticas típicas citadas em materiais de mercado sugerem **prazos por tipo de dado** e anonimização após prazo ? **teu produto** deve permitir **política por organização** e **export/delete** (requisito de confiança enterprise).

**Multas:** até patamar elevado (fontes citam valores em R$; **validar** texto legal atualizado na ANPD).

## B.4 IA conversacional em ambiente regulado (além da LGPD)

- Expectativa de **base documental** (RAG), **não inventar fatos** em domínios sensíveis ? alinha com literatura de **RAG + human-in-the-loop** ([ex.: discussão de governança](https://datanucleus.dev/corporate-governance-compliance/ai-hallucinations-rag-and-human-in-loop-risk-mitigation)).  
- Se clientes forem **UE** ou tratam dados de europeus, cruzar com **GDPR**; se usar fornecedores EUA, **DPAs** com subprocessadores.

## B.5 SLAs ?implícitos? do domínio

- Cliente final associa **WhatsApp** a **resposta imediata**; indisponibilidade do teu agente ou fila mal desenhada vira **churn** antes de SLA formal.  
- **Empresa 3:** integração que ?perde? documento é **incidente de negócio** ? exige **idempotência** e **visibilidade** (ver TR).

## B.6 Síntese DR

O domínio exige **duas camadas de compliance**: **Meta** (canal) e **proteção de dados + governança de IA** (jurídico e reputacional). O teu **gate de aprovação** não é burocracia ? é **alinhamento ao domínio**.

---

# Parte C ? TR (Technical Research) aprofundado

## C.1 Arquitetura de referência em camadas (alinhada ao teu desenho)

```
[Cliente final] ? WhatsApp Cloud API ? Meta
                      ?
              [OpenBSP ? Edge + Postgres]
              (webhook, messages, agent-client, billing, RLS?)
                      ? eventos / API
[Teu ?shell? ? portal multi-tenant, planos, iframe, catálogo módulos]
                      ?
[N8N ou fila/worker] ? sistemas do cliente (ERP, CRM, storage)
                      ?
[Serviço de agente IA ? opcional por SKU]
(LangGraph/LangChain, RAG, memória; exposto via HTTP/A2A para o agent-client)
```

**Princípio:** **uma fonte de verdade** para conversa no OpenBSP; **orquestração externa** não deve duplicar estado de mensagem sem contrato.

## C.2 Padrões de integração (OpenBSP ? mundo)

| Padrão | Quando usar | Riscos |
|--------|-------------|--------|
| **Webhook `notify_webhook`** (`messages` / `conversations`) | Empresa 3, baixa latência, event-driven | Limite `LIMIT 3` por disparo no schema atual ? ver `docs/modular/13`; fan-out único ou evolução de schema |
| **REST PostgREST / API keys** | CRUD, backoffice, N8N HTTP Request | RLS + escopo de key |
| **MCP (servidor OpenBSP)** | Ferramentas para agentes externos / operadores | Autorização fina (`Allowed-Contacts`) |
| **Fila + worker** (SQS, Redis queue, etc.) | Alto volume, retries, poison queue | Operação mais pesada |

**n8n:** encaixa como **motor de workflows** com **webhook trigger** e nós HTTP; self-hosted é comum em cenários de custo/controle ([comparações gerais](https://flowengine.cloud/blog/n8n-vs-zapier-in-2025-self-hosted-control-vs-automation-3)). Licenciamento **Fair Code** ? validar compliance interno.

## C.3 Multi-tenant e dados

- **Padrão recomendado** para SaaS: **Postgres partilhado + RLS + `organization_id` / tenant** ? padrão documentado para Supabase ([Makerkit](https://makerkit.dev/blog/tutorials/supabase-rls-best-practices), [SupaExplorer](https://supaexplorer.com/dev-notes/10-real-world-rls-patterns-for-supabase-with-policy-snippets.html), [visão geral multi-tenant](https://veldsystems.com/blog/multi-tenant-saas-architecture)).  
- **Base de dados dedicada por cliente** só com **motivo forte** (regulatório, isolamento de performance); custo de **migrations**, backups e conexões explode.

**?Cada empresa fornece acesso ao BD próprio?** (teu requisito anterior): modelar como **conector** (credenciais encriptadas, IP allowlist, **read-only** onde possível), não como ?substituir? o Postgres do OpenBSP sem desenho explícito.

## C.4 Agente IA: onde vive o ?cérebro?

- O OpenBSP **`agent-client`** já suporta **Chat Completions** e **A2A** e **tools** (MCP, HTTP, SQL). Para **LangChain/LangGraph**, o padrão saudável é **serviço dedicado**:
  - **LangGraph** pode correr como **standalone** (Docker/K8s) com Postgres/Redis para estado ([documentação LangChain deployment](https://docs.langchain.com/langgraph-platform/deploy-standalone-server); [visão geral produção](https://blog.langchain.com/langgraph-platform-announce/)).
  - O **agent-client** chama esse serviço como **A2A** ou HTTP ? alinha ao README do OpenBSP (?agentes avançados como serviços externos?).

## C.5 RAG, memória, anti-alucinação (técnicas)

- **RAG:** `pgvector` no mesmo projeto ou vector DB externo; **re-ranking** e **citação obrigatória** reduzem confiança em respostas soltas ([técnicas enterprise](https://www.techment.com/blogs/15-advanced-rag-techniques-enterprise-guide/)).  
- **Memória longa:** tabelas por `organization_id` + `contact_id` + política de retenção (coerente com LGPD).  
- **Human-in-the-loop:** estados `draft` / aprovação antes de `active` no agente ? já é linguagem do domínio OpenBSP (`AgentExtra.mode`).

## C.6 Iframe e segurança

- **Auth:** sessão/JWT com **origem** permitida; **CSP** e **frame-ancestors** para impedir clickjacking.  
- **Cookies / third-party:** restrições de browser ? preferir **subdomínio dedicado** ou **token de curta duração** na URL assinada para embed.

## C.7 Observabilidade e custo

- Unificar **logs** (aplicação + integrações) com **correlação** `organization_id` / `conversation_id`.  
- **LLM:** custo por token + **media preprocessor** (Gemini no repo) ? **quotas por plano** ligadas ao schema `billing` existente.

## C.8 Síntese TR ? decisões que precisam entrar no PRD técnico

1. **Fan-out de webhooks** (hoje `LIMIT 3`) vs **um endpoint hub** vs **migração de schema**.  
2. **Um serviço de agente** por tenant ou **pool** compartilhado com isolamento lógico.  
3. **N8N** como componente **obrigatório** só no SKU 3 ou **opcional** no 2.  
4. **Conector BD cliente**: MVP = **SQL tool** com credencial vault ou **só leitura via API** do cliente.

---

# Parte D ? Ponte para a ideia final e documentação

## D.1 O que já está maduro para documentar

- **Proposta de valor** em três SKUs (Empresa 1/2/3) com **fronteira clara** com OpenBSP.  
- **Riscos de mercado e domínio** (Meta + LGPD + expectativa de IA).  
- **Arquitetura lógica** em camadas e **padrões de integração**.

## D.2 Checklist Mary ? preenchida (workshop rápido, 2026-04-17)

Decisões registadas com GD-AGK; embasam o **CB** (`bmad-product-brief-preview`) a seguir.

| Item | Decisão |
|------|---------|
| **Geografia** | **Brasil apenas** nos primeiros 12?18 meses ? **LGPD** como eixo principal de privacidade e políticas de retenção. |
| **Papel Meta** | **Fase inicial:** repasse transparente do **custo Meta** ao cliente (ou modelo equivalente de transparência). **Aspiração:** evoluir para **Meta Partner** quando fizer sentido com volume e operação; **Partner preferível** quando viável (margem, suporte, relação comercial). |
| **Iframe (v1)** | **Conversa + configurações leves** (ex.: quick replies, filas, ajustes operacionais) ? não painel administrativo completo no primeiro embed. |
| **Aprovação do agente** | **Dois modos permitidos no produto:** (a) aprovação **só pelo cliente B2B** (agência/ISV); (c) **dois passos** ? validação B2B **e** aceite do **cliente final** quando o cenário exigir (ex.: domínio sensível ou contrato). O produto deve suportar **flexibilidade por tenant ou por SKU**, não um único fluxo rígido. |

### Notas Mary (risco / produto)

- **Repasse de custo Meta:** documentar no **CB** como promessa de produto (?transparente?) para evitar atrito comercial.  
- **Partner:** tratar como **roadmap** com gates de volume, não como dependência do MVP.  
- **Aprovação a + c:** no brief, definir **quando** o fluxo (c) é obrigatório vs opcional (regra de negócio ou plano).

## D.3 Próximo artefato sugerido (fase ideia final)

1. **Product Brief** (comando **CB** ? `bmad-product-brief-preview`) com: visão, não-objetivos, SKUs, métricas de sucesso.  
2. **One-pager** executivo (narrativa Caravaggio-ready): problema ? solução ? três ofertas ? porquê agora.  
3. **ADR pack** (3?5 decisões): webhooks vs fila; agente monólito vs serviço; N8N mandatório ou não.

---

## Referências web (amostra; não exaustivo)

- Meta pricing / overview: [developers.facebook.com/docs/whatsapp](https://developers.facebook.com/docs/whatsapp/overview/)  
- RLS Supabase: [makerkit.dev](https://makerkit.dev/blog/tutorials/supabase-rls-best-practices), [supaexplorer.com](https://supaexplorer.com/dev-notes/10-real-world-rls-patterns-for-supabase-with-policy-snippets.html)  
- LGPD + chatbots: [parceriajuridica.com.br](https://parceriajuridica.com.br/como-a-lgpd-impacta-o-uso-de-chatbots-em-empressas/), [lawinnovation.com.br](https://lawinnovation.com.br/lgpd-como-coletar-corretamente-os-dados-pessoais-via-chatbots/)  
- LangGraph deploy: [docs.langchain.com/langgraph-platform/deploy-standalone-server](https://docs.langchain.com/langgraph-platform/deploy-standalone-server)  
- n8n self-host: [flowengine.cloud](https://flowengine.cloud/blog/n8n-vs-zapier-in-2025-self-hosted-control-vs-automation-3)  

---

*Relatório MR+DR+TR aprofundado ? Mary ? continuação dos comandos solicitados; checklist D.2 fechada no workshop; pronto para CB (Product Brief).*
