---
story_key: 5-5-engine-aplica-acoes
epic: epic-5
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 3-1-webhook-entrada-verificacao-encaminhamento
  - 5-3-publish-permissao-ambiente
code_location: v2/apps/api
---

# Story 5.5 - Engine aplica acoes

## Story

**Como** tenant com regra **publicada**,  
**quero** que a plataforma **aplique** acoes (mensagem, tag, handoff) segundo a regra e o estado da conversa,  
**para** FR26 (sem LLM core).

## Acceptance Criteria

1. **Dado** inbound apos 3.1, **quando** o motor faz match da regra, **entao** acoes executam; erros **nao** silenciosos (UX-DR4); liga a **3.2** e **4.3** sem dependencia inversa indevida.
2. Ordem e idempotencia de efeitos side-effect (mensagens) respeitam politica (NFR-INT-02).
3. Feature flag **motor em staging** aceitavel antes do inbox completo, se DoD brownfield permitir; documentar no README.

**Requisitos:** FR26, NFR-INT-02.

## Tasks / Subtasks

- [ ] Loop: evento normalizado pos-3.1 -> avaliacao de regras publicadas -> acoes.
- [ ] Acoes: enviar mensagem (3.2), aplicar tag (4.2), emitir handoff (4.3) via contratos internos.
- [ ] Erros visiveis em logs/telemetria; correlation id.
- [ ] Endpoint de status ou metrica (ex. `GET /v1/me/engine/status`) para operacao; ATDD `test_epic5_story55_engine_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Motor stateless com estado em DB; sem corrida entre workers sem lock documentado. |
| **Mary** | FR26 + NFR-INT-02; nota de dependencia 3.1 + subset 4.1 no epico. |
| **John** | Valor core da automatizacao. |
| **Sally** | Falhas refletem-se na conversa ou health (4.4), nao silencio. |
| **Amelia** | Testes de idempotencia com mesmo event_id duplicado. |

## Advanced Elicitation (CS)

- **Pre-mortem:** regra infinita (loop de acoes) - limite de passos por evento.
- **Red team:** motor com regra de outro tenant - validar tenant em cada passo.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Match so sobre regras **publicadas** no ambiente alvo (5.3). |
| **Amelia** | ATDD: GET engine/status 200; expandir com probes de match em integracao. |
| **Mary** | DoD brownfield para flag staging explicito no project-context se aplicavel. |

### Advanced Elicitation (VS)

- **Pre-mortem:** Meta down - acoes de envio falham com classificacao culpa (FR51 prep).

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Tenant boundary em todo o pipeline do motor. |
| Confiabilidade | NFR-INT-02 testado com duplicados. |

## Dev Notes - requisitos tecnicos

- Depende de **3.1** e **5.3**; **4.1** minimo para QA fim-a-fim quando exigido.
- Integracao com **f2** futura: gate de produto separado.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story55_engine_atdd.py`
- Testes integracao motor + stub inbound recomendados no DS.

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.5

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story55_engine_atdd.py`.
