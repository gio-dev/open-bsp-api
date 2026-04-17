# `notify_webhook` ? semântica profunda, limites e riscos

Este módulo aprofunda [09](./09-rotina-webhooks-saida-integracoes.md) com **análise de implementação** e **implicações operacionais**.

## Código-fonte

Função: `public.notify_webhook()`  
Arquivo: `supabase/schemas/02_functions/02-03_trigger_functions.sql`

```332:377:supabase/schemas/02_functions/02-03_trigger_functions.sql
create function public.notify_webhook() returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  webhook_record record;
  headers jsonb;
begin
  -- loop through all matching webhooks
  for webhook_record in
    select w.url, w.token
    from public.webhooks w
    where new.organization_id = w.organization_id
      and w.table_name = tg_table_name::public.webhook_table
      and lower(tg_op)::public.webhook_operation = any(w.operations)
    limit 3
  loop
    -- prepare headers
    headers := case
      when webhook_record.token is not null then
        jsonb_build_object(
          'content-type', 'application/json',
          'authorization', 'Bearer ' || webhook_record.token
        )
      else
        jsonb_build_object(
          'content-type', 'application/json'
        )
      end;

    -- send webhook notification
    perform net.http_post(
      url := webhook_record.url,
      body := jsonb_build_object(
        'data', to_jsonb(new),
        'entity', tg_table_name,
        'action', lower(tg_op)
      ),
      headers := headers
    );
  end loop;

  return new;
end;
$$;
```

## Tipos enumerados relevantes

Definidos em `supabase/schemas/01_types.sql`:

- **`webhook_operation`**: apenas **`insert`** e **`update`** ? **delete** não dispara este caminho por enum.
- **`webhook_table`**: **`messages`**, **`conversations`**.

Se a UI permitir `delete` na tabela `webhooks` como operação, o trigger de **DELETE** na tabela de negócio **não** casa com `webhook_operation` atual ? comportamento esperado: só insert/update de linhas de negócio geram notificações.

## Semântica do `LIMIT 3`

O `SELECT` que alimenta o loop **não** tem **`ORDER BY`**.

Consequências:

1. **No máximo três** URLs distintas (na verdade três **linhas** da tabela `webhooks`) são processadas por disparo de trigger.
2. Se existirem **mais de três** webhooks cadastrados para a **mesma** combinação `(organization_id, table_name, operação)`, os demais **não** recebem POST nesse ciclo ? e a escolha dos três é **indeterminada** sem `ORDER BY` (depende do plano do Postgres).
3. Isso **não** é ?até 3 tentativas da mesma URL?: são **até 3 registros** retornados pela query.

**Implicação para n8n**: se a organização precisa de **vários** fluxos independentes, ou consolidam em **um** webhook n8n com fan-out, ou **garantem ? 3** linhas por combinação, ou **mudam o schema** (feature futura).

## `SECURITY DEFINER` e `search_path`

A função roda com privilégios do dono da função (**security definer**) e `search_path = ''` ? padrão de endurecimento: nomes de tipos/tabelas são **qualificados** (`public.webhooks`, `public.webhook_table`).

## Rede: `net.http_post`

- Chamada **assíncrona** no sentido de `pg_net`: retorno não bloqueia a transação da mesma forma que um await em app ? mas **erros de rede** podem afetar observabilidade (ver documentação Supabase `pg_net`).
- **Não** há retry explícito no snippet da função.
- Corpo fixo: **`data`** = linha completa `NEW` como JSONB, **`entity`** = nome da tabela do trigger, **`action`** = `lower(tg_op)`.

## Segurança do destino

- O token vai no header **`Authorization: Bearer`** se configurado ? o destino (n8n) deve validar.
- **SSRF**: administradores podem apontar `url` para IPs internos; isso é **risco de configuração** ? mitigar com política de org ou validação fora do DB.

## Triggers que invocam `notify_webhook`

- `messages`: `AFTER INSERT OR UPDATE` ? ver `03-05_messages.sql`.
- `conversations`: `AFTER INSERT OR UPDATE` ? ver `03-03_conversations.sql`.

Cada insert/update em mensagem pode gerar **carga** em integrações: avalie **volume** antes de ativar em produção.

## Checklist de teste

1. Cadastrar **1** webhook ? verificar POST único no n8n.
2. Cadastrar **4** webhooks idênticos em escopo ? verificar se apenas **3** recebem (comportamento atual).
3. Update em `messages` ? `action: "update"` no corpo.
4. Token inválido no destino ? falha visível no n8n / logs do worker.

## Referências

- [09](./09-rotina-webhooks-saida-integracoes.md)
- [99](./99-elicitacao-pre-mortem-e-riscos.md) (risco de produto)
- [12](./12-apendice-rotas-http-e-contratos.md)
