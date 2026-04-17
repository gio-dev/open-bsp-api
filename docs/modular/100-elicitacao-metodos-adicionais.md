# Advanced Elicitation ? métodos adicionais (sessão 2)

Complementa **[99-elicitacao-pre-mortem-e-riscos.md](./99-elicitacao-pre-mortem-e-riscos.md)** aplicando outros métodos do registro **methods.csv** (skill `bmad-advanced-elicitation`) ao **caso OpenBSP** documentado nos módulos **01?15**.

---

## 1. Five Whys Deep Dive (?40) ? ?o integrador não recebeu o evento?

| # | Por quê? | Resposta |
|---|----------|----------|
| 1 | Por que o n8n não disparou? | Não chegou HTTP POST. |
| 2 | Por que não chegou POST? | `notify_webhook` não incluiu essa URL no `SELECT`. |
| 3 | Por que foi excluída? | Já existiam **3** webhooks matching; `LIMIT 3` sem `ORDER BY`. |
| 4 | Por que quatro webhooks iguais? | Configuração duplicada por testes / falta de governança. |
| 5 | Por que falta governança? | **Causa raiz**: ausência de checklist de integração + documentação do limite até este pacote de docs. |

**Ação**: consolidar destinos; monitorar contagem de linhas em `public.webhooks` por `(org, table, ops)`.

---

## 2. Failure Mode Analysis (?35) ? componentes críticos

| Componente | Modo de falha | Detecção | Mitigação |
|------------|---------------|----------|-----------|
| Vault `edge_functions_url` | URL errada ou vazia | Triggers não disparam funções; hooks vazios | Smoke test pós-deploy [10](./10-rotina-deploy-ci-billing-vault.md) |
| `net.http_post` (notify) | Timeout / DNS | Integração silenciosa | Timeout e alertas no destino; fila dead-letter no n8n |
| `agent-client` batching | Descarta execução legítima | Logs ?ok? sem resposta | Métricas de taxa de skip [04](./04-rotina-agent-client.md) |
| Meta token por endereço | Expirado | `failed` em `messages.status` | Job de renovação OAuth / alerta |
| `LIMIT 3` webhooks | Destinos não escolhidos | Auditar sorteio não determinístico | ?3 URLs ou fan-out único [13](./13-notify-webhook-semantica-e-riscos.md) |

---

## 3. Socratic Questioning (?41) ? extensão RAG

- **O que** exatamente deve o modelo **nunca** inventar? ? Política de citação obrigatória.
- **Como** sabemos que o chunk está atualizado? ? Pipeline de ingestão com versão / `updated_at`.
- **Quem** aprova novo conteúdo na base? ? Workflow humano (não só embedding automático).
- **Onde** fica o custo quando o vector store cresce? ? Orçamento por org [11](./11-extensoes-rag-n8n-aprendizado.md).

---

## 4. Tree of Thoughts (?11) ? onde hospedar o RAG

| Caminho | Prós | Contras |
|---------|------|---------|
| A) `pgvector` no mesmo Postgres | Baixa latência, transações | Tamanho DB, backup maior |
| B) MCP externo (serviço dedicado) | Escala independente | Mais rede, mais SPOF |
| C) Só tool HTTP para OpenSearch | Flexível | Mais código operacional |

**Seleção sugerida**: prototipar **B** (MCP) para desacoplar; migrar para **A** se latência e custo Net forem problema.

---

## 5. Self-Consistency Validation (?14) ? duas leituras do mesmo requisito

**Requisito**: ?Integração n8n para todos os eventos de mensagem.?

| Leitura | Interpretação | Compatível com código? |
|---------|---------------|-------------------------|
| Literal | Todo insert/update em `messages` notifica **todos** os endpoints cadastrados | **Não** ? máximo 3 linhas por disparo [13](./13-notify-webhook-semantica-e-riscos.md) |
| Negocial | Todo evento chega ao **automation hub** (um n8n) que distribui | **Sim** ? uma URL, fan-out interno |

**Consistência**: alinhar stakeholders com a leitura **negocial** até evoluir o schema.

---

## 6. Challenge from Critical Perspective (?36) ? pressuposto ?Supabase sempre disponível?

O pressuposto: *se o DB está up, o fluxo WhatsApp funciona.*

**Crítica**: `pg_net` e Edge são **serviços distintos**; fila pode acumular; Meta pode rate-limitar.

**Fortalecimento**: idempotência em `messages.external_id`, retries no dispatcher (comportamento Meta), observabilidade unificada.

---

## Encerramento

Esta sessão **não** substitui revisão de segurança formal nem load testing ? **instrumenta** prioridades de backlog com base no código real.

**Próxima elicitação sugerida**: após mudanças em **`notify_webhook`** ou **`edge_function`**, rerodar **Pre-mortem** [99](./99-elicitacao-pre-mortem-e-riscos.md).
