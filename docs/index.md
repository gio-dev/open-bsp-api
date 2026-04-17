# Documentação ? OpenBSP API

Bem-vindo ao hub de documentação do repositório **open-bsp-api**.

## Documentação modular (principal)

A análise técnica **brownfield** ? rotinas, triggers, Edge Functions, webhooks de saída, extensões (RAG/MCP) ? está organizada em módulos independentes. O **núcleo** descreve o sistema atual no repositório; integrações específicas (ex.: n8n) aparecem só como exemplos onde indicado.

**[? Ir para `modular/README.md`](./modular/README.md)**

### Atalhos rápidos

| Tema | Documento |
|------|-----------|
| Escopo do caso | [modular/00-caso-e-escopo.md](./modular/00-caso-e-escopo.md) |
| Arquitetura reativa | [modular/01-arquitetura-reativa-visao-geral.md](./modular/01-arquitetura-reativa-visao-geral.md) |
| Webhook Meta | [modular/02-rotina-whatsapp-webhook.md](./modular/02-rotina-whatsapp-webhook.md) |
| Triggers / mensagens | [modular/03-rotina-mensagens-triggers-edge.md](./modular/03-rotina-mensagens-triggers-edge.md) |
| Agent client | [modular/04-rotina-agent-client.md](./modular/04-rotina-agent-client.md) |
| Dispatcher | [modular/05-rotina-whatsapp-dispatcher.md](./modular/05-rotina-whatsapp-dispatcher.md) |
| Media preprocessor | [modular/06-rotina-media-preprocessor.md](./modular/06-rotina-media-preprocessor.md) |
| WhatsApp management | [modular/07-rotina-whatsapp-management.md](./modular/07-rotina-whatsapp-management.md) |
| MCP servidor | [modular/08-rotina-mcp-servidor-api.md](./modular/08-rotina-mcp-servidor-api.md) |
| Webhooks de saída (`notify_webhook`) | [modular/09-rotina-webhooks-saida-integracoes.md](./modular/09-rotina-webhooks-saida-integracoes.md) |
| Deploy / billing / vault | [modular/10-rotina-deploy-ci-billing-vault.md](./modular/10-rotina-deploy-ci-billing-vault.md) |
| Extensões RAG / aprendizado | [modular/11-extensoes-rag-n8n-aprendizado.md](./modular/11-extensoes-rag-n8n-aprendizado.md) |
| Rotas HTTP e contratos | [modular/12-apendice-rotas-http-e-contratos.md](./modular/12-apendice-rotas-http-e-contratos.md) |
| `notify_webhook` em profundidade | [modular/13-notify-webhook-semantica-e-riscos.md](./modular/13-notify-webhook-semantica-e-riscos.md) |
| Contatos, onboarding, papéis | [modular/14-contatos-onboarding-e-rls.md](./modular/14-contatos-onboarding-e-rls.md) |
| Catálogo MCP (ferramentas) | [modular/15-mcp-servidor-catalogo-ferramentas.md](./modular/15-mcp-servidor-catalogo-ferramentas.md) |
| Party Mode (roundtables) | [modular/98-party-mode-perspectivas-rota.md](./modular/98-party-mode-perspectivas-rota.md) |
| Elicitação: pré-mortem / red team | [modular/99-elicitacao-pre-mortem-e-riscos.md](./modular/99-elicitacao-pre-mortem-e-riscos.md) |
| Elicitação: métodos adicionais | [modular/100-elicitacao-metodos-adicionais.md](./modular/100-elicitacao-metodos-adicionais.md) |

## Documentação oficial do produto (raiz)

O **[README.md](../README.md)** na raiz do repositório continua sendo a fonte canônica para: visão de produto, configuração Meta, planos hospedados, e fluxo de desenvolvimento local (Supabase CLI).

## Convenção

- Texto dos módulos em **português (Brasil)**.
- Caminhos de código relativos à raiz do repositório `open-bsp-api/`.
