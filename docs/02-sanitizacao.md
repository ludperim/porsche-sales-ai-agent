# 2. Sanitização dos Dados

## Objetivo

Esta etapa teve como objetivo transformar os dados originais da
planilha em um conjunto padronizado, consistente e adequado para
análises posteriores.

As regras foram desenvolvidas sem utilizar as colunas previamente
sanitizadas da planilha.

As colunas de referência existentes serão utilizadas somente em uma
etapa posterior de validação.

## Fluxo da sanitização

O processo executado pelo arquivo `src/sanitizador.py` segue esta ordem:

1. carregamento das colunas originais;
2. sanitização das datas;
3. padronização dos modelos Porsche;
4. conversão dos anos dos modelos;
5. conversão dos preços;
6. padronização da quilometragem;
7. padronização das formas de pagamento;
8. padronização das cidades;
9. padronização dos estados;
10. padronização dos status de entrega;
11. exportação da planilha sanitizada;
12. geração do relatório de qualidade.

## Preservação dos dados originais

Nenhuma coluna original foi sobrescrita.

Para cada campo tratado, foi criada uma nova coluna sanitizada.
Também foram criadas colunas de status para indicar se o valor foi
considerado válido ou inválido.

Essa estratégia permite comparar o valor original com o resultado da
sanitização e mantém a rastreabilidade das transformações.

## Regras aplicadas

### Datas

A coluna `sale_date` apresentava diferentes formatos e datas
impossíveis.

Exemplos encontrados:

- `2024-02-30`
- `April 31st, 2024`
- `2024-15/07`
- `February 30th, 2027`

As datas válidas foram convertidas para o tipo de data.

As datas impossíveis foram transformadas em `NaT` e marcadas como
inválidas. Nenhuma data foi corrigida por suposição.

Resultado:

- 76 datas válidas;
- 24 datas inválidas.

### Modelos Porsche

A coluna `porsche_model` foi tratada com regras seguras de remoção de
espaços excedentes.

Nenhuma versão legítima dos modelos foi agrupada ou alterada.

Resultado:

- 100 modelos válidos;
- nenhuma alteração necessária.

### Ano do modelo

A coluna `model_year` continha anos em diferentes formatos.

Exemplos:

- `2024`
- `20-24`
- `20 23`
- `twenty twenty five`
- `two thousand twenty one`

Todos os formatos reconhecíveis foram convertidos para números
inteiros.

Resultado:

- 100 anos válidos.

### Preço de venda

A coluna `sale_price` apresentava símbolos monetários, abreviações,
separadores diferentes e valores por extenso.

Exemplos:

- `$79,500.00`
- `235000 USD`
- `USD 112.750`
- `$121k`
- `$89.750,00`
- `eighty two thousand USD`

Os preços foram convertidos para valores numéricos decimais.

Resultado:

- 100 preços válidos.

### Quilometragem

A coluna `vehicle_mileage` apresentava valores em milhas, quilômetros,
texto e números por extenso.

Exemplos:

- `9,800 miles`
- `Miles: 6,400`
- `KM 18,900`
- `zero miles`
- `new car`
- `twelve thousand miles`

A unidade padrão adotada foi milhas.

Valores em quilômetros foram convertidos usando o fator de conversão
de quilômetros para milhas.

Resultado:

- 100 quilometragens válidas.

### Formas de pagamento

As diferentes variações foram agrupadas em categorias padronizadas:

- `Bank Transfer`
- `Cash`
- `Credit Card`
- `Crypto`
- `Debit Card`
- `Financing`
- `Leasing`

Exemplos de agrupamento:

- `wire-transfer`, `bank wire` e `ACH payment` foram classificados
  como `Bank Transfer`;
- `CreditCard` e `credit card payment` foram classificados como
  `Credit Card`;
- `lease plan` e `Leasing` foram classificados como `Leasing`.

Resultado:

- 100 formas de pagamento válidas.

### Cidades

Os nomes das cidades foram padronizados quanto à capitalização e aos
espaços.

Exemplos:

- `atlanta` para `Atlanta`;
- `colorado springs` para `Colorado Springs`;
- `san francisco` para `San Francisco`.

Resultado:

- 100 cidades válidas;
- 30 valores alterados.

### Estados

Os nomes completos e siglas foram padronizados para siglas de duas
letras em maiúsculas.

Exemplos:

- `California` para `CA`;
- `california` para `CA`;
- `tx` para `TX`;
- `North Carolina` para `NC`.

Resultado:

- 100 estados válidos.

### Status de entrega

As variações foram agrupadas nas categorias:

- `Delivered`
- `Pending`
- `In Transit`
- `Awaiting`
- `Cancelled`
- `Shipped`

Exemplos:

- `delivered!!!` e `DELIVERD` para `Delivered`;
- `pending approval` e `pending review` para `Pending`;
- `in-transit` e `IN TRANSIT` para `In Transit`.

Resultado:

- 100 status válidos.

## Resultado geral

Foram realizadas 800 validações:

- 100 registros;
- 8 campos avaliados por registro.

Dessas validações:

- 776 foram aprovadas;
- 24 foram consideradas inválidas.

A qualidade geral calculada foi de 97%.

Essa métrica representa a proporção de validações aprovadas e não
significa que 97% dos registros estejam completamente perfeitos.

## Arquivos gerados

A planilha sanitizada foi exportada para:

`data/processed/vendas_porsche_sanitizadas.xlsx`

O relatório de qualidade foi exportado para:

`data/processed/relatorio_qualidade.json`

## Limitações atuais

- datas inválidas permanecem sem valor sanitizado;
- valores numéricos por extenso ainda são tratados por regras simples;
- categorias desconhecidas são marcadas como inválidas;
- algumas decisões de agrupamento dependem do contexto de negócio;
- a validação contra as colunas de referência ainda será implementada.