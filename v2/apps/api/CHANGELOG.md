# Changelog

Todas as notas relevantes para integradores ficam aqui alinhadas a `GET /openapi.json`
(`info.version`) e ao campo `api_semantic_version` em `GET /v1/policy/deprecation`
(Story 7.2 / FR37).

## 0.1.0

- Contrato REST estavel sob o prefixo `/v1` (FR35 / FR36).
- Historico tenant-scoped de ingresso webhook: `GET /v1/me/sandbox/webhook-deliveries`
  (Story 7.3 / FR38, FR39); resposta JSON com schema fechado (`extra=forbid` no servidor).
- Cabecalho `Idempotency-Key` documentado para `POST /v1/me/messages/send`
  com respostas 429 / 503 e `Retry-After` onde aplicavel (Story 7.1 / FR40).
- Politica publica de ciclo de vida e deprecacao: `GET /v1/policy/deprecation`
  (Story 7.2 / FR37).
- Schema fechado (`additionalProperties: false` effect) nos modelos JSON desta politica
  via Pydantic `extra=forbid` (pos-code review 7.2).
