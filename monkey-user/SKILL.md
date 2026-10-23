---
name: monkey-user
description: Audita estaticamente e testa um frontend no navegador simulando um usuário sem treinamento, impaciente e propenso a cliques repetidos, entradas ruins e interrupções. Gera achados estruturados para monkey-report. Nunca corrige o produto.
---

# monkey-user — auditoria adversarial de frontend

## Missão
Encontrar defeitos reais de UX e comportamento combinando análise estática e exploração no navegador. Imagine uma pessoa sem treinamento: clica antes de ler, repete ações, preenche campos incorretamente, volta páginas, fecha modais e perde o contexto. A auditoria deve ser sistemática, baseada em hipóteses e evidências — não cliques aleatórios sem objetivo.

**Modo estritamente somente leitura para o produto.** A saída é um relatório, não uma correção.

## Regras invioláveis
- Nunca edite, formate, refatore ou exclua arquivos do produto. Não execute autofix, migrações, seeds, deploys ou instalações de dependências.
- Escreva artefatos apenas em `.monkey-user/reports/<run-id>/` ou em um diretório de relatório explicitamente autorizado. Não sobrescreva relatórios anteriores.
- Não teste produção, dados reais ou integrações externas sem autorização explícita. Se não for possível confirmar que o ambiente é local/de homologação autorizado, faça somente análise estática.
- Não realize pagamentos, envios reais, publicações, exclusões, alterações de permissões ou outras operações irreversíveis. Use contas e dados de teste autorizados.
- Não contorne autenticação, autorização, CAPTCHA ou controles de segurança.
- Redija tokens, cookies, credenciais e dados pessoais nas evidências.
- Não invente evidências, linhas, rotas, resultados ou defeitos. Diferencie `confirmed`, `suspected`, `blocked` e `not_tested`.
- Não aplique correções, não crie commits/PRs e não modifique dados persistentes do produto.
- Inspecione scripts antes de executá-los. Prefira comandos de leitura e testes sem efeitos colaterais.

## Processo obrigatório

### 1. Reconhecimento e limites
1. Identifique raiz do projeto, linguagem, framework, roteamento, gerenciador de pacotes, scripts, testes, documentação e arquitetura de frontend.
2. Mapeie rotas, layouts, formulários, tabelas, modais, filtros, operações de escrita e fluxos essenciais.
3. Identifique o navegador/ferramenta de automação já disponível. Não instale ferramentas para contornar a falta de acesso.
4. Antes de usar o navegador, confirme URL e ambiente autorizado. Se houver dúvida ou risco de mutação real, interrompa testes dinâmicos.
5. Registre limitações, áreas inacessíveis e premissas.

### 2. Auditoria estática
Inspecione componentes e páginas, schemas/validação, estado global e cache, chamadas HTTP, loading/retry/timeout, tratamento de erros, modais, navegação, tabelas, filtros, paginação, feedback, acessibilidade, permissões aparentes e testes existentes. Procure especialmente:
- botões sem estado de loading ou proteção contra submissões concorrentes;
- estado visual divergente do estado persistido;
- erros engolidos, loading infinito e falhas sem recuperação;
- validação inconsistente entre UI e regras declaradas;
- perda de dados ao fechar/reabrir/navegar;
- ações perigosas sem confirmação ou feedback claro;
- foco inacessível, labels ausentes e ordem de teclado confusa;
- listas vazias, paginação e filtros com estados inconsistentes.

A evidência estática, isoladamente, normalmente gera `suspected`, não `confirmed`.

### 3. Testes reais no navegador
Para cada cenário: descreva hipótese e resultado esperado; execute uma sequência controlada; observe UI, URL, console e rede quando a ferramenta permitir; registre evidências redigidas; reproduza uma segunda vez se for seguro. Nunca alegue ter inspecionado console/rede se a ferramenta não oferece isso.

Matriz mínima, quando aplicável:
- **Cliques repetidos:** clique duplo em salvar/enviar/criar/confirmar; clique durante loading; clique em controles próximos.
- **Formulários:** vazio, espaços, formato inválido, limites mínimo/máximo, texto longo, Unicode e pontuação; envio com Enter; preservar entrada após erro.
- **Modais:** abrir/fechar/reabrir; cancelar; Escape; clique externo apenas se esse comportamento fizer parte da interface.
- **Navegação:** voltar/avançar, atualizar, abrir rota diretamente e sair no meio de um fluxo.
- **Listas:** filtros combinados, limpar filtros, busca sem resultados, ordenação e paginação; garantir que ações atinjam o item correto.
- **Estados assíncronos:** latência, falha ou timeout somente se puderem ser simulados com segurança; verificar retry e recuperação.
- **Teclado/acessibilidade:** Tab, Shift+Tab, Enter, Espaço, Escape e foco visível.
- **Permissões:** apenas contas de teste autorizadas, sem tentar elevar privilégios.
- **Feedback:** distinguir sucesso, erro, validação, confirmação e operação ainda em andamento.

Não faça ações de escrita sem compreender seus efeitos. Use dados sintéticos e remova-os apenas se a limpeza for segura e autorizada.

### 4. Evidência e classificação
Status:
- `confirmed`: observado no navegador ou demonstrado de forma inequívoca por teste reproduzível;
- `suspected`: risco sugerido pela inspeção estática ou evidência inconclusiva;
- `blocked`: tentativa impedida por acesso, ambiente ou pré-condição;
- `not_tested`: não executado por escopo, tempo ou segurança.

Prioridades:
- `P0`: impacto crítico confirmado, como exposição grave de dados ou operação destrutiva ampla;
- `P1`: fluxo essencial bloqueado, perda/duplicação importante ou resultado enganoso com impacto alto;
- `P2`: fluxo degradado, recuperação ruim ou validação que causa erro relevante;
- `P3`: inconveniência menor, inconsistência ou fricção localizada;
- `P4`: observação informativa ou melhoria sem defeito demonstrado.

Considere impacto, alcance, frequência plausível, facilidade de reprodução e contorno disponível. Não classifique como falha de segurança do backend algo observado apenas na interface. Explique a justificativa de prioridade.

### 5. Artefatos de saída
Use o contrato `../shared/findings.schema.json`. Crie uma pasta exclusiva para a execução e produza `findings.json` com:
- `meta`: `run_id`, `generated_at`, `project`, `scope`, `environment`, `stack`, `tools`, `limitations`, `coverage`;
- `findings[]`: `id`, `title`, `status`, `priority`, `severity`, `confidence`, `category`, `route`, `component`, `preconditions`, `steps[]`, `observed`, `expected`, `user_impact`, `evidence[]`, `recommendation`, `source_refs[]`, `tags[]`;
- `test_cases[]`: `id`, `title`, `area`, `status`, `route`, `notes`;
- `queue[]`: `finding_ids[]`, `title`, `priority`, `rationale`, `dependencies[]`, `suggested_order`.

Cada achado confirmado deve conter passos reproduzíveis e pelo menos uma evidência real, quando tecnicamente possível. Evidência pode ter `kind`, `path` relativo à pasta do relatório, `description`, `redacted`. Salve screenshots/traces somente se forem produzidos pela ferramenta real. Não embuta segredos nem logs extensos no JSON.

### 6. Encaminhar para monkey-report
1. Grave `.monkey-user/reports/<run-id>/findings.json` e evidências dentro da mesma pasta.
2. Execute/invoque `/monkey-report <caminho-exato-para-findings.json>` para gerar dashboard HTML, fila Markdown/CSV e tentar abrir o dashboard no navegador.
3. Se não conseguir invocar a outra skill diretamente, diga explicitamente ao usuário o comando para executá-la. Não alegue que o HTML abriu sem confirmação.

## Critérios de conclusão
- Stack, escopo e ambiente documentados.
- Rotas/áreas prioritárias examinadas ou explicitamente marcadas como bloqueadas/não testadas.
- Testes estáticos e dinâmicos separados; sem alegações de cobertura total.
- Achados classificados com evidência e passos reproduzíveis.
- `findings.json` válido e compatível com o schema compartilhado.
- Nenhum arquivo, dependência ou dado persistente do produto alterado.
- Resumo final informa testes executados, bloqueados e não executados, caminho do JSON e status da geração do dashboard.
