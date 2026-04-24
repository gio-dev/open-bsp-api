#!/usr/bin/env python3
"""Historico: geracao em batch foi substituida por stories manuais por epico.

- Epicos **2-6**: ficheiros em `_bmad-output/implementation-artifacts/` mantidos no fluxo CS -> VS -> AT.
- Epicos **7-10** e **F2/F3**: gerados com `scripts/materialize_epic7_f3_story_files.py` (uma vez) ou editados manualmente.

Este script ja nao escreve ficheiros (evita sobrescrever trabalho curado).
"""

from __future__ import annotations


def main() -> None:
    print(
        "Nada a gerar: use scripts/materialize_epic7_f3_story_files.py "
        "para recriar epicos 7-10 / F2/F3, ou edite os .md manualmente."
    )


if __name__ == "__main__":
    main()
