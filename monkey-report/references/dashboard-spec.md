# Especificação do dashboard

- HTML único, offline-first, CSS/JS embutidos; sem CDN, tracking, fonte externa ou API.
- JSON é dado não confiável: escapar HTML, nunca executar strings.
- Busca sem distinção entre maiúsculas/minúsculas.
- Filtros combinam por AND e atualizam a lista.
- Mostrar passos, observado/esperado, impacto, recomendação e evidências.
- Só criar links para evidências existentes dentro da pasta do relatório.
- Separar suspeitas de defeitos confirmados; bloqueados/não testados são cobertura.
- Ordem P0 > P1 > P2 > P3 > P4; confirmados antes de suspeitas.
- Responsivo, foco visível, controles rotulados e estado vazio.
