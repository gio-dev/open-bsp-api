# Documentação modular ? OpenBSP API

Este diretório descreve **cada rotina operacional relevante** do projeto **open-bsp-api** conforme o **código e o schema atuais**. Menções a integrações específicas (ex.: n8n) são **opcionais** e aparecem onde servem de exemplo ? ver **[00-caso-e-escopo.md](./00-caso-e-escopo.md)**.

**Índice na raiz de `docs/`**: [../index.md](../index.md)

## Como ler

1. **[00-caso-e-escopo.md](./00-caso-e-escopo.md)** ? escopo e fronteiras do repositório.
2. **[01-arquitetura-reativa-visao-geral.md](./01-arquitetura-reativa-visao-geral.md)** ? mapa mental (Postgres como orquestrador).
3. Percorra **02?11** na ordem do fluxo de dados (Meta ? banco ? edge ? saída).
4. Use **12?15** como **apêndices operacionais** (rotas HTTP, `notify_webhook` profundo, contatos/onboard, catálogo MCP).
5. **[98-party-mode-perspectivas-rota.md](./98-party-mode-perspectivas-rota.md)** ? trade-offs e vozes BMAD (duas rodadas).
6. **[99](./99-elicitacao-pre-mortem-e-riscos.md)** e **[100](./100-elicitacao-metodos-adicionais.md)** ? Advanced Elicitation (inclui hipóteses de evolução; separar de fatos do repo).

## Índice de módulos

| Doc | Conteúdo |
|-----|----------|
| [00-caso-e-escopo.md](./00-caso-e-escopo.md) | Caso, premissas, fronteiras |
| [01-arquitetura-reativa-visao-geral.md](./01-arquitetura-reativa-visao-geral.md) | Visão de sistema, vault, pg_net |
| [02-rotina-whatsapp-webhook.md](./02-rotina-whatsapp-webhook.md) | Verificação Meta, assinatura, ramos de evento |
| [03-rotina-mensagens-triggers-edge.md](./03-rotina-mensagens-triggers-edge.md) | `before_insert_on_messages`, triggers, `edge_function` |
| [04-rotina-agent-client.md](./04-rotina-agent-client.md) | Orquestração LLM, protocolos, tools, batching, pausa |
| [05-rotina-whatsapp-dispatcher.md](./05-rotina-whatsapp-dispatcher.md) | Graph API, tokens, read/typing |
| [06-rotina-media-preprocessor.md](./06-rotina-media-preprocessor.md) | Gemini, custos, limites |
| [07-rotina-whatsapp-management.md](./07-rotina-whatsapp-management.md) | Hono, templates, signup |
| [08-rotina-mcp-servidor-api.md](./08-rotina-mcp-servidor-api.md) | MCP servidor vs cliente no agente |
| [09-rotina-webhooks-saida-integracoes.md](./09-rotina-webhooks-saida-integracoes.md) | `notify_webhook`, HTTP de saída (exemplos de destino opcionais) |
| [10-rotina-deploy-ci-billing-vault.md](./10-rotina-deploy-ci-billing-vault.md) | CI, vault, billing |
| [11-extensoes-rag-n8n-aprendizado.md](./11-extensoes-rag-n8n-aprendizado.md) | Extensões: RAG, orquestração externa, melhoria contínua |
| [12-apendice-rotas-http-e-contratos.md](./12-apendice-rotas-http-e-contratos.md) | Tabela de rotas HTTP e contratos |
| [13-notify-webhook-semantica-e-riscos.md](./13-notify-webhook-semantica-e-riscos.md) | `LIMIT 3`, segurança, testes |
| [14-contatos-onboarding-e-rls.md](./14-contatos-onboarding-e-rls.md) | Contatos, sync Meta, onboard público, papéis |
| [15-mcp-servidor-catalogo-ferramentas.md](./15-mcp-servidor-catalogo-ferramentas.md) | Ferramentas MCP com parâmetros |
| [98-party-mode-perspectivas-rota.md](./98-party-mode-perspectivas-rota.md) | Party Mode ? duas rodadas |
| [99-elicitacao-pre-mortem-e-riscos.md](./99-elicitacao-pre-mortem-e-riscos.md) | Elicitação: pré-mortem, red team, ADR |
| [100-elicitacao-metodos-adicionais.md](./100-elicitacao-metodos-adicionais.md) | 5 Whys, FMEA, Socratic, Tree of Thoughts |

## Convenções

- **Rotina**: unidade funcional (Edge Function, triggers ou fluxo ponta a ponta).
- Caminhos de código relativos à raiz `open-bsp-api/`.
- Idioma: **português (Brasil)**.
