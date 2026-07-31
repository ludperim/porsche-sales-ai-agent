# 6. Testes Automatizados

## Objetivo

Esta etapa teve como objetivo validar automaticamente as principais
regras de sanitização implementadas no projeto.

Os testes foram desenvolvidos com o framework `pytest`.

## Arquivo de testes

Os testes estão localizados em:

`tests/test_sanitizador.py`

## Regras testadas

Foram criados testes para:

- conversão de anos numéricos;
- conversão de anos separados por hífen;
- conversão de anos escritos por extenso;
- conversão de preços com símbolo de dólar;
- conversão de preços abreviados com `k`;
- conversão de preços escritos por extenso;
- conversão de quilometragem em milhas;
- conversão de quilômetros para milhas;
- identificação de veículos novos;
- padronização de formas de pagamento;
- conversão de nomes de estados para siglas;
- normalização de siglas em minúsculas;
- padronização do status de entrega;
- padronização de nomes de cidades;
- rejeição de cidades inválidas;
- tratamento de valores ausentes.

## Estrutura dos testes

Cada teste utiliza uma entrada conhecida e compara o resultado com o
valor esperado.

Exemplo:

```python
def test_converter_preco_com_k() -> None:
    assert converter_preco("$121k") == 121000.0