# Rotina: webhooks de saída (`notify_webhook`)

## Finalidade (sistema atual)

Notificar **sistemas terceiros** via HTTP quando há **insert** ou **update** em tabelas monitoradas ? hoje **`messages`** e **`conversations`**. O mecanismo é **nativo** do OpenBSP: tabela `public.webhooks` + função `public.notify_webhook()` + `pg_net`.

**Schema**: `public.webhooks` (`supabase/schemas/03_models/03-07_webhooks.sql`)  
**Função**: `public.notify_webhook()` (`supabase/schemas/02_functions/02-03_trigger_functions.sql`)

Qualquer URL HTTP compatível (CRM, fila, serviço próprio) pode ser cadastrada em `url`. Menções a ferramentas específicas (ex.: **n8n**) neste documento são **exemplos opcionais de consumidor**, não parte do repositório.

## Modelo de configuração

Tabela `webhooks`:

- **`organization_id`**
- **`table_name`** ? enum `webhook_table` (ex.: `messages`, `conversations`)
- **`operations`** ? array de `insert` / `update`
- **`url`** ? endpoint HTTP do consumidor
- **`token`** opcional ? se presente, enviado como **`Authorization: Bearer <token>`**

## Payload HTTP

`net.http_post` com corpo JSON:

```json
{
  "data": { "...": "linha new como jsonb" },
  "entity": "<nome da tabela>",
  "action": "insert|update|..."
}
```

## Exemplo opcional: automação com webhook genérico (ex.: n8n)

1. Crie um endpoint que aceite POST JSON (em muitas stacks, um nó "Webhook" expõe uma URL).
2. Cadastre essa URL em `public.webhooks` para a organização (via UI OpenBSP, SQL autorizado, ou API com RLS adequada).
3. Opcional: defina **`token`** e valide no destino.

**Efeito**: cada evento correspondente **empurra** o payload para o URL configurado; o que o destino faz depois (Slack, ERP, etc.) é externo ao OpenBSP.

## Limite importante (brownfield)

A query dentro de `notify_webhook` inclui **`limit 3`** no `SELECT` de webhooks correspondentes.

Interpretação operacional: **no máximo três** registros por disparo; sem `ORDER BY` na query (ver [13](./13-notify-webhook-semantica-e-riscos.md)). Para vários destinos, use **um** endpoint que distribui ou evolua o schema.

## RLS

Políticas em `supabase/schemas/05_rls/05-07_webhooks_rls.sql` ? perfis administrativos gerenciam webhooks da própria org.

## Aprofundamento

Semântica exata do **`LIMIT 3`**, `ORDER BY`, SSRF e checklist de teste: **[13-notify-webhook-semantica-e-riscos.md](./13-notify-webhook-semantica-e-riscos.md)**.

## Referências

- Triggers que chamam `notify_webhook`: `03-05_messages.sql`, `03-03_conversations.sql`
- Arquitetura geral: [01](./01-arquitetura-reativa-visao-geral.md)
- Análise profunda: [13](./13-notify-webhook-semantica-e-riscos.md)
