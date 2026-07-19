# Governança das instruções do Salomão

- **Canônico:** `AGENTS.md`.
- **Adaptador Claude:** `CLAUDE.md`, limitado a apontar para o canônico e repetir apenas
  invariantes de segurança.
- **Procedimentos:** `skills/*/SKILL.md`.
- **Fatos e mapas temáticos:** `skills/*/references/`.
- **Evidência primária e vigência:** `Legislacao/`, `knowledge_base/` e catálogo normativo.

Mudanças de identidade, política de fontes ou protocolo de vigência devem ocorrer primeiro
em `AGENTS.md`. O validador rejeita um `CLAUDE.md` que não declare explicitamente essa
precedência.
