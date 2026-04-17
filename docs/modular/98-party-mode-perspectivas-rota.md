# Party Mode ? perspectivas sobre as rotinas (roundtable BMAD)

Este documento aplica o espírito do skill **Party Mode**: vozes do manifesto `_bmad/_config/agent-manifest.csv`, cada uma julgando o conjunto de rotinas documentada nos módulos **01?15**. Idioma: **português (Brasil)**.

---

## Rodada 1 ? núcleo técnico e produto

**Winston (Architect):**

A arquitetura reativa é **coerente e defensável**: Postgres como barramento de eventos reduz acoplamento entre Meta e Deno, desde que **vault** e **pg_net** estejam sempre consistentes. O ponto frágil não é uma Edge Function isolada: é a **cadeia de triggers** ? uma condição mal ajustada em `status` ou `timestamp` silencia `agent-client` ou dispara o dispatcher em duplicata. Para RAG e n8n, recomendo **MCP** e **webhooks de saída** em vez de polling direto no banco a partir de processos externos: mantém fronteiras claras. Self-host ?só Postgres? continua **estratégia ruim** para este codebase; se Docker, que seja **stack Supabase completa**.

**John (Product Manager):**

O valor do produto está no **fluxo WhatsApp ? resposta ? medição**. As rotinas **02?05** entregam isso; **09** e **[13](./13-notify-webhook-semantica-e-riscos.md)** são o gancho natural para **parceiros e automação**. Para **agentes + RAG**, o PRD implícito precisa separar: (1) resposta em tempo real, (2) conhecimento atualizado, (3) governança de erros. O repositório cobre (1) bem; (2) e (3) são **incrementos explícitos**. O `LIMIT 3` em `notify_webhook` é **risco de produto** se prometermos ?webhooks ilimitados? sem perceber ? **[13](./13-notify-webhook-semantica-e-riscos.md)** agora deixa isso explícito.

**Paige (Technical Writer):**

A documentação modular deve sempre **nomear a direção dos dados** (Meta ? DB ? Edge ? Meta; DB ? integração). Os módulos **[01](./01-arquitetura-reativa-visao-geral.md)**, **[03](./03-rotina-mensagens-triggers-edge.md)** e **[12](./12-apendice-rotas-http-e-contratos.md)** fecham o circuito para quem não abre o SQL. **[12](./12-apendice-rotas-http-e-contratos.md)** é o anexo que faltava para **contratos HTTP** explícitos.

**Murat (Test Architect):**

O sistema é difícil de testar ponta a ponta sem **Postgres + funções reais**: mocks precisam simular `net.http_post` e respostas da Graph. Prioridades: (1) assinatura do webhook Meta, (2) batching do `agent-client`, (3) dispatcher com token por endereço, (4) **`notify_webhook` com quatro URLs** para reproduzir o corte por `LIMIT 3`. Vault vazio: triggers falham sem mensagem para o usuário final ? precisa **alerta** em staging.

**Mary (Business Analyst):**

O caso brownfield + n8n + agentes forma uma **história de valor**: operacionalizar WhatsApp e conectar ecossistema. Requisitos não funcionais ? latência Edge, limites Meta, custo Gemini ? são **parte do escopo**. ?Autoaprendizado? traduz-se para stakeholders como **ciclo de melhoria com aprovação humana**, não como treino online mágico.

---

## Rodada 2 ? inovação, problemas estruturados e comunicação

**Dr. Quinn (Master Problem Solver):**

O problema não é ?falta de n8n?: é **garantir causalidade** entre evento de negócio e efeito externo. A cadeia **INSERT messages ? notify_webhook ? net.http_post** tem **dois pontos frágeis**: (a) limite de três destinos sem ordem definida, (b) falha de rede sem retry no SQL. Eu instrumentaria **primeiro** o destino (n8n com fila e idempotência por `message.id`) **antes** de pedir mudança no banco.

**Victor (Innovation Strategist):**

Quem quiser **diferenciar** no mercado não vende ?mais um webhook?: vende **orquestração confiável + RAG auditável**. O repositório já separa **servidor MCP** ([08](./08-rotina-mcp-servidor-api.md), [15](./15-mcp-servidor-catalogo-ferramentas.md)) de **cliente MCP no agente** ([04](./04-rotina-agent-client.md)) ? isso é **arquitetura de plataforma**. O próximo salto de receita é **pacotes** (SMB vs enterprise) com limites claros em webhooks e créditos AI ([10](./10-rotina-deploy-ci-billing-vault.md)).

**Caravaggio (Presentation / claridade):**

Se eu desenhasse um slide único para executivos: **esquerda** = Meta, **centro** = Postgres + triggers, **direita** = Edge + integrações. Uma seta grossa para **?LIMIT 3?** com ícone de alerta ? não para assustar, mas para **forçar decisão** de fan-out. A doc modular agora sustenta essa narrativa sem misturar REST público com gatilhos internos ([12](./12-apendice-rotas-http-e-contratos.md)).

---

## Nota do orquestrador

- **Convergência**: Winston e Dr. Quinn concordam que **observabilidade do vault** e **contrato de webhook** vêm antes de feature nova.
- **Divergência saudável**: John empurra **promessa de integração**; Murat exige **prova por teste** ? alinhados se o backlog tiver **critérios de aceite** medindo os quatro cenários de webhook.
- **Próximo passo documental**: manter **[100](./100-elicitacao-metodos-adicionais.md)** atualizado quando o schema de `notify_webhook` mudar.

---

## Mapa agente ? foco

| Agente | Foco nesta rodada |
|--------|-------------------|
| Winston | Plataforma, vault, self-host |
| John | Produto, limites, promessa comercial |
| Paige | Estrutura da documentação, leitor não-SQL |
| Murat | Teste, caos, limites |
| Mary | Requisitos e linguagem para stakeholders |
| Dr. Quinn | Causalidade e instrumentação |
| Victor | Diferenciação e modelo de negócio |
| Caravaggio | Narrativa visual e clareza executiva |
