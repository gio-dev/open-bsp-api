---
story_key: 6-3-disclosure-tratamento-opt-in-granular
epic: epic-6
status: review
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

- [x] Modelo preferencias (categorias marketing, transacional, registo de versao de copy).
- [ ] Integracao fluxos 5.x para nos de consentimento quando aplicavel.
- [x] Admin-web: revisao copy baseline; listagem contacto + preferencias.
- [x] Ligacao futura Epico 9 (DSAR) documentada; ATDD `test_epic6_story63_disclosure_preferences_atdd.py`.

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
- Fluxos **5.x** com nos de consentimento explicitos ficam backlog; **`POST .../messages/send`** ja aceita **`preference_kind`** para integradores aplicarem categorias antes do editor grafico cobrir cada no.

## Testing Requirements

- ATDD API (epic6): `v2/apps/api/tests/atdd/test_epic6_story63_disclosure_preferences_atdd.py`
- Integracao: `v2/apps/api/tests/integration/test_story63_contact_preferences.py`
- OpenAPI policy: `test_me_contacts_preferences_documents_errors`
- Admin Vitest ATDD: `v2/apps/admin-web/src/atdd/epic6-story63-contact-preferences.atdd.test.tsx`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 6.3

## Dev Agent Record

### Agent Model Used

Cursor agent.

### Completion Notes List

- Tabela `tenant_contact_preferences` + RLS; seed `atdd-contact` para ATDD CI.
- `GET|PATCH /v1/me/contacts/{contact_id}/preferences`; audit em PATCH quando ha alteracoes.
- Envio **`preference_kind`** `marketing|transactional` com gate em `contacts/outbound_prefs.py`.
- Pagina admin `/privacy/contacts/:contactId/preferences`; README atualizado (Epico 9 / LGPD minimal).

### File List

- `v2/apps/api/alembic/versions/023_tenant_contact_preferences.py`
- `v2/apps/api/app/db/models.py` (TenantContactPreference)
- `v2/apps/api/app/api/routes/me_contact_preferences.py`
- `v2/apps/api/app/contacts/outbound_prefs.py`, `contacts/__init__.py`
- `v2/apps/api/app/api/routes/me_messages.py`
- `v2/apps/api/app/ci_seed.py`, `app/atdd_fixture_ids.py`
- `v2/apps/api/app/tenancy/rbac.py` (CONTACT_PREFERENCE_WRITE_ROLES)
- `v2/apps/api/app/main.py`
- Tests ATDD/integration/policy story63 / epic6_story63 / openapi_me_contacts
- `v2/apps/admin-web/src/features/privacy/ContactPreferencesPage.tsx`
- `v2/apps/admin-web/src/atdd/epic6-story63-contact-preferences.atdd.test.tsx`
- `v2/apps/admin-web/src/App.tsx`
- `v2/README.md`

---

## Change Log

- 2026-04-24: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-24: **[VS]** validada; `atdd_ready: true`.
- 2026-04-24: **[AT]** `test_epic6_story63_disclosure_preferences_atdd.py`.
- 2026-04-30: **[DS]** modelo + API + outbound gate + admin + tests; sprint `review`; integracao fluxos 5.x deixada aberta.
