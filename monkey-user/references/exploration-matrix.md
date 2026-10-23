# Matriz de exploração

| Área | Ação adversarial | Observar | Exemplos de defeito |
|---|---|---|---|
| Ações | Clique duplo/repetido; agir durante loading | Estado do botão, requests, resultado | Registros duplicados, corrida de estado |
| Formulários | Vazio, espaços, formato inválido, limites | Mensagem, foco, preservação | Aceitação indevida, perda silenciosa |
| Modais | Cancelar, fechar, reabrir, Escape | Descarte/retomada previsível | Perda inesperada de entrada |
| Navegação | Voltar, avançar, refresh, rota direta | Estado e recuperação | Fluxo quebrado |
| Tabelas | Filtrar, ordenar, paginar, limpar | Consistência dos itens | Ação aplicada ao item errado |
| Rede | Erro/timeout apenas quando seguro | Retry e recuperação | Loading infinito |
| Permissões | Conta de teste autorizada | Ações/dados visíveis | Controle de UI inconsistente |
| Teclado | Tab, Shift+Tab, Enter, Espaço, Escape | Foco e ordem | Tarefa inacessível |
| Feedback | Sucesso, erro e validação | Mensagem acionável | Resultado ambíguo |

Estados de teste: `passed`, `failed`, `blocked`, `not_tested`, `inconclusive`. Nunca marque `passed` sem executar.
