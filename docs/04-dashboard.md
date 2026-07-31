# 4. Dashboard Interativo

## Objetivo

Esta etapa teve como objetivo criar uma interface visual para apresentar
os resultados da sanitização e da análise das vendas.

O dashboard foi desenvolvido com Streamlit e Plotly.

## Tecnologias utilizadas

- Streamlit
- Plotly
- pandas
- openpyxl

## Arquivo principal

O dashboard é executado pelo arquivo:

`app.py`

## Fontes de dados

A aplicação utiliza três arquivos processados:

### Planilha sanitizada

`data/processed/vendas_porsche_sanitizadas.xlsx`

Contém os dados originais, as colunas sanitizadas e os indicadores de
validade de cada campo.

### Resumo de indicadores

`data/processed/resumo_indicadores.json`

Contém os indicadores gerais, destaques e agrupamentos utilizados pelos
gráficos.

### Relatório de qualidade

`data/processed/relatorio_qualidade.json`

Contém as métricas de validade dos dados.

## Indicadores exibidos

O dashboard apresenta:

- total de pedidos;
- faturamento bruto;
- faturamento realizado;
- ticket médio;
- maior venda;
- menor venda;
- vendas entregues;
- vendas canceladas;
- qualidade geral dos dados.

## Gráficos disponíveis

### Qualidade dos dados

Apresenta o percentual de validade por campo analisado.

O campo de datas apresentou 76% de validade.

Os demais campos apresentaram 100% de validade após a sanitização.

### Análise por modelo

Apresenta os dez modelos selecionados para o ranking e seus respectivos
faturamentos.

As informações de quantidade de pedidos são exibidas ao posicionar o
cursor sobre as barras.

### Análise por estado

Apresenta os dez estados com maior faturamento.

O Texas apresentou o maior faturamento, enquanto a Califórnia teve a
maior quantidade de pedidos.

### Formas de pagamento

Apresenta a participação de cada forma de pagamento no faturamento
bruto.

A categoria `Bank Transfer` concentrou a maior parcela do faturamento.

## Tabela de dados

O dashboard também apresenta a planilha sanitizada em uma tabela
interativa.

Essa tabela permite:

- navegar pelos registros;
- consultar valores originais;
- consultar valores sanitizados;
- verificar os status de validade.

## Execução local

Com o ambiente virtual ativo, o dashboard pode ser iniciado com:

```bash
streamlit run app.py