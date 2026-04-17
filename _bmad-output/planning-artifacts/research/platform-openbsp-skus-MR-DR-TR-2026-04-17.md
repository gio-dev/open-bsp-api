# Pesquisa MR + DR + TR ? Plataforma em camadas (OpenBSP + SKUs Empresa 1/2/3)

**Cliente / parceiro:** GD-AGK  
**Data:** 2026-04-17  
**Idioma:** português (Brasil)  
**Contexto:** Tech provider vendendo soluções; OpenBSP como núcleo de WhatsApp; UI iframe; N8N como camada de integração opcional; agentes com treino e aprovação.

---

## MR ? Market Research (mercado e concorrência)

### Posicionamento de mercado

- O mercado de **WhatsApp Business Platform** para **agências, ISVs e white-label** cresce em torno de três propostas: onboarding rápido (**Embedded Signup**), **multi-tenant** para vários clientes, e **camadas** de valor (só canal, canal + automação, canal + IA + integrações).
- Fontes públicas descrevem **parceiros Meta** em níveis distintos (ex.: **Solution Partners** com linha de crédito vs **Tech Providers** onde o cliente paga uso direto à Meta). Isso **impacta** teu modelo de revenda: margem, cobrança e papel teu na fatura (ver [tiers de BSP](https://www.wuseller.com/whatsapp-business-knowledge-hub/whatsapp-business-solution-providers-partner-tiers-2026/) ? conteúdo de terceiros; validar sempre na documentação oficial Meta).

### Concorrentes / referências (padrão de produto)

- Plataformas que vendem **?embed?** da API WA em SaaS vertical ou agência ([ex.: narrativas de integração partner](https://chakrahq.com/article/whatsapp-api-partner-integration-solution-embedded/)) reforçam teu desenho: **iframe + configuração** reduz atrito com sistemas legados do cliente final.
- Diferenciação típica não é ?ter API?, é **tempo de go-live**, **governança** (quem aprova o bot), e **integrações** (ERP/CRM).

### Jobs-to-be-done dos teus três SKUs

| SKU | Job principal (cliente final) | O que compram de ti além do software |
|-----|-------------------------------|--------------------------------------|
| Empresa 1 | Operar WA com equipe, sem prometer IA | Confiança, simplicidade, embed no sistema deles |
| Empresa 2 | Reduzir carga humana com agente aprovado | Processo de treino, SLA de qualidade, gate de aprovação |
| Empresa 3 | Documentos e dados fluindo para o sistema deles | Integração modular, transparência de custo, suporte à mudança |

### Tendências a explorar no roadmap comercial

- **Marketing Messages API** e atualizações periódicas da Meta (ex.: blogs de fornecedores CPaaS em 2026) ? implicam **retrabalho** de templates e compliance; teu produto ?grandioso? precisa **camada de compliance** comunicada ao cliente.
- Expectativa de **IA** sem alucinação puxa ofertas com **RAG + auditoria** (conecta com DR abaixo).

### Lacunas / perguntas de mercado (para validar contigo)

- Segmento geográfico prioritário (Brasil vs LATAM) e **ticket médio** alvo.
- Posicionamento Meta: **Tech Provider** vs aspiração a **Solution Partner** (afeta pricing e risco).

---

## DR ? Domain Research (domínio: WA + IA conversacional + integrações)

### Domínio regulatório e produto

- **WhatsApp Cloud API**: termos de uso, opt-in, janela de 24h, templates ? o ?domínio? inclui **políticas Meta** e risco de bloqueio de número; teu fluxo Empresa 2/3 deve **ensinar** o cliente o que não pode prometer no agente.

### IA em atendimento (anti-alucinação e governança)

- Literatura e fornecedores destacam **grounding** em base de conhecimento, **RAG** e **human-in-the-loop** como mitigação de alucinação em contexto enterprise (ex.: discussões sobre RAG + revisão humana ? ver [artigos de governança](https://datanucleus.dev/corporate-governance-compliance/ai-hallucinations-rag-and-human-in-loop-risk-mitigation); benchmarks sectoriais variam amplamente).
- Implicação para o teu caso: **?liberar agente após aval?** não é burocracia ? é **controle de risco** alinhado ao domínio.

### Integrações (N8N e afins)

- **Orquestração** entre sistemas heterogêneos é domínio à parte: **idempotência**, **retry**, **PII**, **mapeamento de documentos** recebidos no WhatsApp para destinos no ERP/CRM.
- **N8N** é ferramenta de domínio ?automação?; o produto vendável é **?conector certificado?** ou **?pacote de fluxo?**, não o N8N em si.

### Vocabulário a fixar no produto

- **Módulo WhatsApp multi-pessoas** = capacidade + papéis (owner/admin/member) alinhados ao teu modelo (OpenBSP já pensa em organizações e agentes).
- **Treinar o agente** = definir se é: só instruções, base documental versionada, ou ambos + avaliação em sandbox.

---

## TR ? Technical Research (arquitetura e tecnologias)

### Ancoragem no OpenBSP (o que já favorece teu desenho)

- **Multi-tenant** (`organizations`), **mensagens e triggers**, **webhooks de saída** (`notify_webhook`), **agent-client** com protocolos e tools (MCP/HTTP/SQL), **billing** em schema dedicado ? reduz risco de reinventar núcleo transacional.
- **Embedded Signup / gestão** já tem trilha no repo (`whatsapp-management`) ? alinha com Empresa 1?3 para **onboarding de número**.

### Camada ?por cima? (teu produto)

- **Portal + iframe:** autenticação unificada (JWT/session) entre teu shell e OpenBSP UI ou views que vocês embutem; **CORS e origem** do iframe devem ser desenhados cedo.
- **Planos e limites:** estender `billing` + regras de enforcement (agentes, mensagens, números, ?setores?) ? TR sugere **uma tabela de políticas por plano** e jobs de uso, não só flags soltas.

### N8N vs alternativas

- **N8N self-hosted:** forte em webhooks, filas, centenas de nós; custo operacional previsível em VPS; licenciamento Fair Code ? avaliar compliance interno ([comparações gerais](https://flowengine.cloud/blog/n8n-vs-zapier-in-2025-self-hosted-control-vs-automation-3)).
- **Alternativa ?menos custosa?** para Empresa 2: **só** `notify_webhook` + **um** serviço worker (fila) que chama LLM ? sem N8N, se o fluxo for linear.
- **Empresa 3:** N8N (ou equivalente) tende a **pagar o ingresso** pela **composição** de integrações modulares e retries.

### Agentes ?próprios? (LangChain, RAG, memória)

- Padrão alinhado ao próprio OpenBSP: **agente pesado fora** da Edge (serviço dedicado) falando com o `agent-client` via **A2A** ou HTTP; **LangChain** como biblioteca **no worker**, não necessariamente dentro da função Deno.
- **Memória longa:** tabelas por `organization_id` + `contact_id` + política de retenção; **RAG:** pgvector ou vector externo; **anti-alucinação:** citação obrigatória + recusa quando score baixo.

### Riscos técnicos explícitos

- **Dois cérebros:** N8N e agente a competir pela mesma resposta ? definir **prioridade** e **estados** (ex.: só IA quando conversa não pausada).
- **BD dedicado por cliente:** explode custo de operações; preferir **logically isolated** até prova de compliance.

---

## Síntese executiva (Mary)

1. **MR:** o mercado compra **velocidade + confiança + integração**; teus três SKUs espelham **escada de valor** clara ? diferencia-te com **gates de aprovação** e **pacotes de integração** nomeados.
2. **DR:** o domínio exige **Meta + governança de IA**; ?treinar e aprovar? é **alinhado à prática** de mitigação de risco, não opcional para enterprise.
3. **TR:** OpenBSP acelera; **N8N** é ferramenta na camada certa (Empresa 3 e integrações); **LangChain/RAG** pertencem a **serviços** com limites e observabilidade, não espalhados ad hoc.

---

## Fontes web (consulta 2026-04-17)

- Tiers BSP / mercado partner: wuseller knowledge hub; Chakra embed SaaS; blogs CPaaS/Meta updates (validar datas e políticas na Meta).
- RAG / hallucination / HITL: datanucleus, Vonage developer blog (Knowledge AI), literatura enterprise RAG.
- N8N self-hosted / comparações: FlowEngine, selfhosting.sh, Zapier blog (perspetivas comerciais ? cruzar com docs oficiais n8n).

---

*Documento gerado como continuação dos skills MR, DR e TR; persona Mary (analista BMAD).*
