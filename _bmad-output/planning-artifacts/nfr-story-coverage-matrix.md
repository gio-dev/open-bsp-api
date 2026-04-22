---
title: Matriz de cobertura NFR ? histórias (open-bsp-api)
date: '2026-04-17'
related:
  - epics.md
  - prd.md
  - architecture.md
  - ../project-context.md
---

# Matriz NFR ? histórias

Liga cada identificador NFR do inventário em `epics.md` às histórias do *sprint* (`sprint-status.yaml`) que **devem** validar ou implementar o requisito. Valores numéricos de SLO permanecem no PRD (Anexo A); aqui só o **rasto**.

| NFR | Âmbito | Histórias principais (IDs) | Notas |
|-----|--------|----------------------------|--------|
| NFR-PERF-01 | Latência p95 rotas críticas | 3-2, 7-1 | Ingest, envio, API pública alinhados a SLO `API-lat`. |
| NFR-PERF-02 | Frescura evento ? UI | 4-1 | Inbox e sinais honestos (ligado a `OBS-fresh`). |
| NFR-PERF-03 | Ingest webhook ack/persistência | 3-1 | Alinhado a `WH-ingest` / carga no runbook. |
| NFR-REL-01 | Disponibilidade API | 1-1, 7-1 | *Health*, contrato e política `API-avail`. |
| NFR-REL-02 | Falhas atribuíveis à plataforma | 3-2, 4-4 | Sem ?falso enviado?; classificação de culpa (cruz. FR51). |
| NFR-REL-03 | Drenagem backlog webhooks | 3-1 | RTO pós-falha; pode exigir história técnica adicional se não couber só em 3.1. |
| NFR-REL-04 | Migração legado ? alvo (`MIG-parity`) | *(runbook / histórias de migração)* | Explícito após núcleo MVP; não duplicar como épico só técnico. |
| NFR-SEC-01 | TLS, superfícies | 1-1, 2-1, 6-1 | Ambiente *staging* alinhado; embed e consola. |
| NFR-SEC-02 | Dados em repouso, segredos | 1-2, 2-3 | KMS/*secret manager*; chaves de API. |
| NFR-SEC-03 | Rotação segredos | 2-3, 2-4 | OAuth, webhooks, chaves. |
| NFR-SEC-04 | Sessão e OAuth | 2-1 | Timeout; revogação pós *logout* admin. |
| NFR-SEC-05 | Rate limit, quota ingest | 3-1, 3-2, 7-1 | 429, `Retry-After`, *backpressure*. |
| NFR-SEC-06 | Degradação Meta | 3-2, 4-4 | Sem perda silenciosa; honestidade UX. |
| NFR-FAIR-01 | Isolamento *noisy neighbor* | 1-2 | Base RLS + *fairness* de recurso. |
| NFR-FAIR-02 | *Enforcement* quota | 8-3 | Entitlements e alertas. |
| NFR-FAIR-03 | Atribuição uso por tenant | 8-1 | *Metering* mínimo. |
| NFR-FAIR-04 | *Headroom* / capacidade | 8-3, 1-1 | *Gates* e observabilidade mínima. |
| NFR-OPS-01 | Gates SLO no release | 1-1 | CI e *smoke*; detalhe em pipeline. |
| NFR-OPS-02 | Caos / simulação falha Meta | 4-4, 10-1 | Sinais e investigação. |
| NFR-OPS-03 | Retenção *audit log* | 10-2 | Consulta e política de PII. |
| NFR-OPS-04 | Alertas operacionais | 4-4, 8-3 | Próximos a limites e incidentes. |
| NFR-OPS-05 | Separação de culpa | 10-1, 4-4 | Taxonomia Meta vs plataforma vs cliente. |
| NFR-LGPD-01 | SLO operacional DSAR | 9-2 | *ACK* na janela acordada. |
| NFR-LGPD-02 | Export / titular | 8-4, 9-2, 9-4 | Coordenar com DSAR e retenção. |
| NFR-LGPD-03 | Incidente de dados | 10-3 | *Break-glass* e acesso emergencial. |
| NFR-LGPD-04 | Subprocessadores | 9-3 | Lista com versão/data. |
| NFR-A11Y-01 a 04 | Acessibilidade embed | 6-4 | WCAG onde assumido; roteiros prioritários. |
| NFR-INT-01 | Retries 429 / *backoff* | 2-4, 3-2, 7-1 | Integração resiliente. |
| NFR-INT-02 | Idempotência / duplicados | 3-1, 3-2, 5-5, 7-1 | Webhook e efeitos colaterais. |
| NFR-INT-03 | Compatibilidade versão API | 7-1, 7-2 | *Deprecation* e coexistência. |

**Legenda de IDs:** `<épico>-<número>-slug` como em `development_status` (ex.: `3-1-webhook-entrada-...`).

**Lacunas conscientes:** NFR-REL-03 (drenagem prolongada) e NFR-REL-04 (*parity* de migração) podem precisar de histórias técnicas dedicadas após o núcleo ? registar no *refinement* se saírem do DoD de uma única história de canal.
