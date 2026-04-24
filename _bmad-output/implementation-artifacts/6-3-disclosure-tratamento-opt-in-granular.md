---
story_key: 6-3-disclosure-tratamento-opt-in-granular
epic: epic-6
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-24
atdd_ready: true
cs_completed: 2026-04-24
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 6-2-copy-estados-bot-humano
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 6.3 - Disclosure de tratamento e opt-in granular (MVP minimo)

## Story

**Como** operador,  
**quero** flows e templates a **recolher/confirmar** finalidade, opt-in e categorias com registo,  
**para** FR31 a FR33 no MVP minimo (DSAR hibrido no Epico 9; aqui copy e estado no produto).

## Acceptance Criteria

1. **Dado** desenho de fluxo, **quando** o contacto entra percurso que requer consentimento ou opt-out categoria, **entao** o sistema **persiste** preferencias minimas e respeita **opt-out de marketing** sem bloquear **transacional** acordado (FR33, FR32).
2. Copy padrao **revisivel** pelo tenant (politica de produto).
3. API preferencias por contacto (ex. `GET/PATCH /v1/me/contacts/{id}/preferences`) com RLS; OpenAPI.

**Requisitos:** FR31, FR32, FR33, FR50 (cruzado Epico 9 minimo).

## Tasks / Subtasks

- [ ] Modelo preferencias (categorias marketing, transacional, registo de versao de copy).
- [ ] Integracao fluxos 5.x para nos de consentimento quando aplicavel.
- [ ] Admin-web: revisao copy baseline; listagem contacto + preferencias.
- [ ] Ligacao futura Epico 9 (DSAR) documentada; ATDD `test_epic6_story63_disclosure_preferences_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Nao armazenar texto legal como unica fonte sem versionamento. |
| **Mary** | FR31-33 + FR50; juridico valida copy templates - fora do codigo. |
| **John** | Risco regulatorio se marketing dispara sem opt-in. |
| **Sally** | Fluxos claros; sem dark patterns (UX-DR4). |
| **Amelia** | Audit trail minimo em mudanca de preferencia. |

## Advanced Elicitation (CS)

- **Pre-mortem:** contacto sem ID estavel - resolver wa_id / phone hash conforme CDA.
- **Red team:** bypass opt-out via API interna - enforcement no envio 3.2.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Separacao marketing vs transacional testada por caso. |
| **Amelia** | ATDD: GET preferences 200 para contacto fixture. |
| **Mary** | Epico 9 completa DSAR; esta story nao bloqueia se piloto for assistido. |

### Advanced Elicitation (VS)

- **Socratic:** o que prova "nao bloqueia transacional"? - teste de envio OTP/simulado com marketing off.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Compliance | Preferencias persistidas; sem conselho juridico no codigo. |
| RLS | Contacto e preferencias por tenant. |

## Dev Notes - requisitos tecnicos

- Depende de **6.2** para narrativa continuidade canal/painel.
- Alinhar com **9.x** para registo de consentimento formal.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic6_story63_disclosure_preferences_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.3

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story63_disclosure_preferences_atdd.py`.
