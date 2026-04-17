# Rotina: `whatsapp-management`

## Finalidade

Expor API HTTP (framework **Hono**) para operações de **gestão** do WhatsApp Business: templates, embedded signup, rotas autenticadas por **JWT de usuário** ou **API key** (não confundir com o endpoint MCP).

**Código**: `supabase/functions/whatsapp-management/index.ts`  
**Módulos**: `templates.ts`, `embedded_signup.ts`

## Autenticação

Middleware global (exceto rotas públicas de onboard):

1. Se **`Authorization`** começa com **`eyJ`**, trata como **JWT** ? `createClient`, `auth.getUser()`, injeta `user` e `supabase` no contexto Hono.
2. Caso contrário, valida como **API key** (lógica no restante do middleware ? ver arquivo completo).

Rota **`/onboard`** (embedded signup) pode ser pública para o fluxo de onboarding (ver condição `path.endsWith("/onboard")`).

## Responsabilidades típicas

- **Templates**: criar, listar, editar, excluir, buscar ? usando funções importadas de `templates.ts` (wrappers da Business Management API).
- **Embedded signup**: `performEmbeddedSignup`, `deleteSignup` ? integração com fluxo Meta de coexistência/onboarding (ver README ?Embedded Signup?).

## Relação com outras rotinas

| Rotina | Diferença |
|--------|-----------|
| `whatsapp-webhook` | Entrada **Meta ? sistema** (eventos) |
| `whatsapp-dispatcher` | **Sistema ? Meta** para mensagens de conversa |
| `whatsapp-management` | **Operações de conta/ativos** (templates, signup), uso por **operadores** ou automação com API key |

## Referências

- README: secção WhatsApp integration e modelo de dados `organizations_addresses`
- MCP reutiliza helpers de templates: imports em `supabase/functions/mcp/tools.ts` (`listTemplates`, `fetchTemplate` de `whatsapp-management/templates.ts`)
- **Tabela completa de métodos, caminhos e papéis**: [12-apendice-rotas-http-e-contratos.md](./12-apendice-rotas-http-e-contratos.md)
- **Onboarding público e contatos**: [14-contatos-onboarding-e-rls.md](./14-contatos-onboarding-e-rls.md)
