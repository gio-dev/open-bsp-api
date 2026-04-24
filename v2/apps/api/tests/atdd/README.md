# ATDD (pytest)

Coloque aqui os testes de aceitação gerados em **fase vermelha** do ATDD (`bmad-testarch-atdd`).

## Epic 1

Ver `_bmad-output/test-artifacts/V2/atdd-checklist-epic-1.md` para inventário, comandos e `data-testid` do admin.

## Regra de merge

- Cada teste deve usar `@pytest.mark.atdd` (além de nomes `test_*`).
- O job **CI v2 (Docker)** executa **toda** a suite `pytest` na imagem `api-ci`, **incluindo** esta pasta.
- Enquanto um teste ATDD estiver a falhar (**vermelho**), o pipeline falha e **não há merge** para `main` / `develop` até ficar verde (implementação + refatoração).

Não commite testes ATDD com `skip` ou `xfail` temporário sem política explícita da equipa.
