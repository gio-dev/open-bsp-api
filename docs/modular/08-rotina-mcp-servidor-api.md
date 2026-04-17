# Rotina: `mcp` (servidor MCP sobre Edge)

## Finalidade

Expor um **servidor MCP** (Model Context Protocol) via HTTP (**Hono** + SDK MCP), para clientes como Claude Desktop ou outras plataformas agenticas operarem **contas, conversas, templates e envio** com as mesmas regras de negócio do produto.

**Código**: `supabase/functions/mcp/index.ts`, `supabase/functions/mcp/tools.ts`

## Autenticação

- Header **`Authorization: Bearer <API_KEY>`** onde a key existe em **`public.api_keys`** ligada a **`organization_id`**.
- Headers opcionais:
  - **`Allowed-Contacts`** ? lista de telefones normalizados (só dígitos).
  - **`Allowed-Accounts`** ? restrição similar para contas.

Falha ? **403** com mensagem explícita.

## Implementação runtime

- **`McpServer`** por requisição (comentário no código: Edge é **stateless** ? novo servidor + transporte por request).
- CORS aplicado globalmente.

## Ferramentas expostas (README)

Documentação de produto na raiz lista: `list_accounts`, `list_conversations`, `fetch_conversation`, `search_contacts`, `send_message`, `list_templates`, `fetch_template`.

Implementação detalhada em `tools.ts` ? usa cliente Supabase com escopo da org e aplica filtros de allowed contacts/accounts.

## Diferença em relação ao MCP **client** no `agent-client`

| Local | Papel |
|-------|--------|
| **`functions/mcp`** | **Servidor** MCP ? expõe tools para **clientes externos** autenticados por API key |
| **`agent-client/tools/mcp.ts`** | **Cliente** MCP ? o **agente** OpenBSP chama servidores MCP **terceiros** configurados em `AgentExtra.tools` |

Arquitetura simétrica: OpenBSP pode ser **hub** (servidor MCP para humanos/devs) e **spoke** (agente consome MCPs de RAG/ERP).

## Referências

- README: secção ?MCP server?
- Agente + tools: [04](./04-rotina-agent-client.md)
