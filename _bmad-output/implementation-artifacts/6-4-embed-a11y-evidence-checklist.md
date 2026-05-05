# Story 6.4 ? Evidência a11y embed (checklist interno)

**Story:** `6-4-acessibilidade-embed`  
**Rota SPA:** `/embed/panel`  
**Objectivo de produto:** WCAG 2.1/2.2 nível AA (FR34, NFR-A11Y-01..04) ? este ficheiro **não** substitui auditoria jurídica nem avaliação humana completa.

## Automatização em CI (Vitest)

- Ficheiro: `v2/apps/admin-web/src/atdd/epic6-story64-embed-a11y.atdd.test.tsx`
- Ferramenta: **jest-axe** (axe-core) sobre fases: `need_token`, `loading`, `ok`, `erro`, `refresh`.
- Limite JSDOM: regra **color-contrast** desligada nos testes (estilos não são calculados como no browser). Contraste deve ser validado abaixo com **axe** ou inspetor no Chrome.

## Roteiros prioritários (MVP)

| Jornada | Verificação manual (teclado + SR) | Axe browser (claro/escuro) |
|--------|-----------------------------------|----------------------------|
| Falta `?token=` (need_token) | Tab: skip link ? foco no `main`; leitura do `h1` e copy | Sem violações críticas/serias |
| Loading | `role=status`, `aria-busy`; spinner com `aria-label` | Idem |
| OK (token válido) | Conteúdo FR30 legível; landmark único | Idem |
| Erro API | `role=alert`, foco movido para a mensagem | Idem |
| 401 / refresh | Mensagem de renovação compreensível | Idem |

## Evidência por release (preencher na data do merge / deploy embed)

- **Data:** _______________
- **Versão / commit:** _______________
- **Executor:** _______________
- **Ambiente:** Chrome ______ Firefox ______ Safari ______  
- **Temas:** claro ? escuro ? (Chakra / sistema)
- **Extensão axe DevTools** (ou relatório exportado): ? anexo ou link interno _______________
- **Teclado apenas** (sem rato) nas 5 jornadas: ?  
- **Leitor de ecrã** (amostra NVDA/VoiceOver): ? / N/A ?  

## Pre-mortem (story 6.4)

- **iframe:** coordenar com integrador ? foco inicial pode vir do parent; documentar contrato `postMessage` (`openbsp_embed_session`, `refresh`).
- **Modais futuros:** ao adicionar `Dialog` no embed, usar padrão com trap de foco (Chakra).

## Referência API (metadados, não prova legal)

`GET /v1/me/embed/a11y-status` ? resume tooling e roteiros; alinhado a este checklist.
