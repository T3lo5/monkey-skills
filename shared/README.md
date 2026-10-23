# Contrato compartilhado

`findings.schema.json` define o formato de dados trocado entre as skills.

1. `/monkey-user` audita e grava `findings.json`.
2. `/monkey-report caminho/para/findings.json` gera `index.html`, `priority-queue.md`, `priority-queue.csv` e `report-meta.json`, e tenta abrir o dashboard.
3. Artefatos ficam na pasta do relatório; o código do produto não é modificado.
4. O renderizador usa apenas a biblioteca padrão do Python.
