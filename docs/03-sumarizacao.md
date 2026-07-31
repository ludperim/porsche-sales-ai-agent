# 3. Sumarização dos Dados

## Objetivo

Esta etapa teve como objetivo transformar os dados sanitizados em
indicadores estruturados de vendas.

Os cálculos foram realizados pelo módulo `src/analisador.py`.

A Inteligência Artificial não é responsável pelos cálculos
matemáticos. O código Python calcula os indicadores e exporta os
resultados em formato JSON.

Essa separação reduz o risco de erros numéricos ou respostas não
fundamentadas geradas pelo modelo de IA.

## Arquivo utilizado

A análise utiliza a planilha sanitizada:

`data/processed/vendas_porsche_sanitizadas.xlsx`

A aba analisada é:

`Dados Sanitizados`

## Indicadores gerais

Foram calculados os seguintes indicadores:

- total de pedidos;
- faturamento bruto;
- faturamento realizado;
- faturamento cancelado;
- ticket médio;
- menor venda;
- maior venda;
- quantidade de vendas entregues;
- quantidade de vendas canceladas.

## Resultados gerais

Os dados analisados apresentaram:

- total de pedidos: 100;
- faturamento bruto: US$ 12.827.800,50;
- faturamento realizado: US$ 5.078.800,50;
- faturamento cancelado: US$ 625.250,00;
- ticket médio: US$ 128.278,01;
- menor venda: US$ 58.900,00;
- maior venda: US$ 286.500,00;
- vendas entregues: 41;
- vendas canceladas: 7.

## Faturamento bruto e faturamento realizado

O faturamento bruto representa a soma de todos os pedidos existentes
na planilha.

Esse valor inclui pedidos:

- entregues;
- pendentes;
- em trânsito;
- aguardando;
- enviados;
- cancelados.

O faturamento realizado considera somente os pedidos classificados
como `Delivered`.

Essa distinção evita tratar pedidos ainda não concluídos ou cancelados
como receita efetivamente realizada.

## Análise por modelo

Os dados foram agrupados por modelo Porsche para calcular:

- quantidade de pedidos;
- faturamento total por modelo.

Houve empate entre os modelos mais vendidos.

Os seguintes modelos registraram 4 pedidos cada:

- Taycan 4S;
- Cayenne Coupe;
- Cayenne E-Hybrid;
- Macan Electric;
- Panamera;
- Macan T.

O modelo com maior faturamento foi:

- 911 Dakar;
- faturamento: US$ 810.600,00.

A implementação considera corretamente a possibilidade de empate e
não seleciona apenas o primeiro modelo encontrado.

## Análise por estado

Os dados foram agrupados por estado para calcular:

- quantidade de pedidos;
- faturamento total.

O estado com maior faturamento foi:

- Texas, representado pela sigla `TX`;
- faturamento: US$ 2.023.400,50;
- quantidade de pedidos: 14.

A Califórnia apresentou 16 pedidos, quantidade superior à do Texas,
mas faturamento menor.

Esse resultado demonstra que quantidade de pedidos e faturamento não
devem ser interpretados como indicadores equivalentes.

## Análise por forma de pagamento

As formas de pagamento foram agrupadas para calcular:

- quantidade de pedidos;
- faturamento total.

A categoria com maior faturamento foi:

- Bank Transfer;
- quantidade de pedidos: 40;
- faturamento: US$ 5.422.950,50.

As categorias analisadas foram:

- Bank Transfer;
- Credit Card;
- Financing;
- Cash;
- Leasing;
- Crypto;
- Debit Card.

## Estrutura do arquivo de resumo

Os indicadores foram exportados para:

`data/processed/resumo_indicadores.json`

O arquivo contém as seguintes seções:

### `indicadores_gerais`

Armazena os principais indicadores consolidados.

### `destaques`

Armazena informações como:

- modelos mais vendidos;
- modelo com maior faturamento;
- estado com maior faturamento;
- forma de pagamento com maior faturamento.

### `top_10_modelos`

Contém os dez modelos com maior quantidade de pedidos, considerando
também o faturamento como critério secundário de ordenação.

### `top_10_estados`

Contém os dez estados com maior faturamento.

### `formas_pagamento`

Contém quantidade de pedidos e faturamento por forma de pagamento.

## Uso pelo agente de IA

O agente de IA utilizará o arquivo JSON como fonte principal para gerar
o resumo executivo.

O modelo não receberá a responsabilidade de recalcular valores.

Ele deverá:

1. interpretar os indicadores;
2. destacar padrões relevantes;
3. explicar diferenças entre volume e faturamento;
4. apontar riscos e oportunidades;
5. produzir um texto executivo baseado exclusivamente nos dados
   fornecidos.

## Uso pelo dashboard

O dashboard utilizará:

- a planilha sanitizada para filtros e gráficos detalhados;
- o relatório de qualidade para métricas de confiabilidade;
- o resumo de indicadores para cartões e destaques executivos.

## Arquivos relacionados

- `src/analisador.py`
- `data/processed/vendas_porsche_sanitizadas.xlsx`
- `data/processed/resumo_indicadores.json`
- `data/processed/relatorio_qualidade.json`