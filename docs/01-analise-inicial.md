# 1. Análise Inicial da Planilha

## Objetivo

Esta etapa teve como objetivo analisar a estrutura da planilha fictícia
de vendas da Porsche antes da implementação do processo de sanitização.

A análise foi realizada por meio do script `src/diagnostico.py`,
utilizando as bibliotecas pandas e openpyxl.

## Arquivo analisado

- Arquivo: `vendas_porsche_ficticias.xlsx`
- Localização: `data/raw`
- Quantidade de abas: 1
- Nome da aba: `Sanitized`
- Quantidade de registros: 100
- Quantidade de colunas: 21

## Estrutura identificada

A planilha contém colunas com os dados originais e colunas adicionais
com versões previamente sanitizadas.

| Coluna original | Coluna sanitizada |
|---|---|
| `sale_date` | `SaleDateSanitized` |
| `porsche_model` | `PorscheModelSanitized` |
| `model_year` | `ModelYearSanitized` |
| `sale_price` | `SalesPriceSanitized` |
| `vehicle_mileage` | `VehicleMileageSanitized` |
| `payment_method` | `PayMethodSanitized` |
| `city` | `CitySanitized` |
| `state` | `StateSanitized` |
| `delivery_status` | `DeliveryStatusSanitized` |

As colunas `sale_id`, `customer_name` e `salesperson` não possuem uma
coluna sanitizada correspondente.

## Qualidade dos dados

O diagnóstico inicial identificou:

- nenhum valor ausente;
- nenhuma linha totalmente duplicada;
- diferentes tipos de dados nas colunas originais;
- datas armazenadas como texto;
- valores monetários armazenados como texto;
- anos e quilometragens com formatos inconsistentes;
- variações de capitalização e pontuação nos campos textuais.

## Estratégia adotada

As colunas originais serão usadas como entrada do processo de
sanitização desenvolvido no projeto.

As colunas previamente sanitizadas serão usadas apenas como referência
para validar os resultados produzidos pelo agente.

Após a sanitização, os dados tratados serão utilizados para:

1. calcular indicadores de vendas;
2. produzir um resumo executivo com inteligência artificial;
3. gerar um dashboard interativo;
4. exportar uma nova planilha sanitizada.

## Regras preliminares de sanitização

| Campo | Problema esperado | Tratamento planejado |
|---|---|---|
| Data da venda | Diferentes formatos e datas inválidas | Converter para data e identificar valores inválidos |
| Modelo Porsche | Capitalização e grafias inconsistentes | Padronizar nomes dos modelos |
| Ano do modelo | Valores armazenados como texto | Converter para número inteiro |
| Preço de venda | Símbolos monetários e separadores | Converter para valor decimal |
| Quilometragem | Texto, unidades e separadores | Converter para número inteiro |
| Forma de pagamento | Variações de escrita | Padronizar categorias |
| Cidade | Capitalização e pontuação | Padronizar nomes |
| Estado | Nome completo ou abreviação | Padronizar para um formato único |
| Status de entrega | Maiúsculas, pontuação e variações | Padronizar categorias |

## Evidência gerada

O resultado completo da análise foi armazenado no arquivo:

`docs/diagnostico_inicial.txt`