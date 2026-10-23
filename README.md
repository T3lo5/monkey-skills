# Monkey User Suite para Claude Code

Pacote com duas skills complementares:

- `monkey-user`: auditoria estática + exploração real no navegador, simulando uso sem treinamento. Apenas relatório; não altera o produto.
- `monkey-report`: gera dashboard HTML local e fila priorizada em Markdown/CSV a partir de `findings.json`.
- `shared/findings.schema.json`: contrato de dados entre as duas skills.
- `shared/sample-findings.json`: amostra fictícia para testar o renderizador. **Não representa uma auditoria real.**

## Instalação no projeto

Copie estas pastas para o projeto onde usa Claude Code, preservando a estrutura:

```text
seu-projeto/
└── .claude/
    └── skills/
        ├── monkey-user/
        │   ├── SKILL.md
        │   └── references/
        ├── monkey-report/
        │   ├── SKILL.md
        │   ├── references/
        │   └── scripts/
        └── shared/
            ├── findings.schema.json
            └── README.md
```

O diretório `shared` precisa ficar como irmão das duas skills para que os caminhos relativos no `SKILL.md` funcionem.

## Uso

1. Abra o projeto no Claude Code e execute `/monkey-user`.
2. A skill deve auditar sem alterar o código e salvar `findings.json` em `.monkey-user/reports/<run-id>/`.
3. Gere o dashboard com `/monkey-report .monkey-user/reports/<run-id>/findings.json`.
4. O renderizador salva `index.html`, `priority-queue.md`, `priority-queue.csv` e `report-meta.json` na pasta de relatório e tenta abrir o HTML no navegador padrão.

Se a invocação direta de uma skill pela outra não estiver disponível na sua configuração, execute o comando `/monkey-report ...` manualmente.

## Renderizador manual

Requer Python 3.9+ e usa somente a biblioteca padrão:

```bash
python3 .claude/skills/monkey-report/scripts/render_report.py \
  .monkey-user/reports/<run-id>/findings.json --open
```

Para gerar em outra pasta vazia:

```bash
python3 .claude/skills/monkey-report/scripts/render_report.py \
  caminho/para/findings.json --outdir caminho/para/relatorio-novo --open
```

O script se recusa a sobrescrever saídas existentes. Se o navegador não abrir automaticamente, abra `index.html` manualmente.

## Segurança e validação

- Confirme que o ambiente de testes é local/homologação antes de executar fluxos dinâmicos.
- Use apenas contas/dados de teste autorizados; não realize operações irreversíveis reais.
- O HTML não usa CDN, telemetria ou recursos externos. O conteúdo do JSON é escapado antes da renderização.
- Foi executado um smoke test com a amostra fictícia: geração de HTML, Markdown, CSV e metadados, com dois achados de demonstração.
- O smoke test valida a geração do relatório, não a capacidade de Claude Code acessar seu navegador ou a qualidade da auditoria em qualquer projeto.
