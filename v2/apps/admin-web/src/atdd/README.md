# ATDD (Vitest)

Testes de aceitação ao nível da UI (ou contratos consumidos pelo admin) em **fase vermelha**.

## Regra de merge

- Ficheiros `*.test.ts` / `*.test.tsx` nesta pasta são corridos por `npm run test` / `vitest --run` na imagem **admin-web-ci**.
- Falhas aqui **bloqueiam** o merge tal como na API.

Quando existir E2E (Playwright), parte dos cenários P0 pode migrar para essa suite; até lá, use testes aqui ou em colocalização `*.test.tsx` conforme `test-framework.md`.
