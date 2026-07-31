import pandas as pd

from src.sanitizador import (
    converter_ano,
    converter_cidade,
    converter_estado,
    converter_forma_pagamento,
    converter_preco,
    converter_quilometragem,
    converter_status_entrega,
)


def test_converter_ano_numerico() -> None:
    assert converter_ano(2024) == 2024


def test_converter_ano_separado() -> None:
    assert converter_ano("20-24") == 2024


def test_converter_ano_por_extenso() -> None:
    assert converter_ano("twenty twenty five") == 2025


def test_converter_preco_com_dolar() -> None:
    assert converter_preco("$79,500.00") == 79500.0


def test_converter_preco_com_k() -> None:
    assert converter_preco("$121k") == 121000.0


def test_converter_preco_por_extenso() -> None:
    assert converter_preco("eighty two thousand USD") == 82000.0


def test_converter_quilometragem_em_milhas() -> None:
    valor, unidade = converter_quilometragem("9,800 miles")

    assert valor == 9800.0
    assert unidade == "milhas"


def test_converter_quilometragem_em_quilometros() -> None:
    valor, unidade = converter_quilometragem("KM 18,900")

    assert valor == 11743.91
    assert unidade == "quilômetros"


def test_converter_quilometragem_veiculo_novo() -> None:
    valor, unidade = converter_quilometragem("new car")

    assert valor == 0.0
    assert unidade == "milhas"


def test_converter_forma_pagamento() -> None:
    assert converter_forma_pagamento(
        "wire-transfer"
    ) == "Bank Transfer"


def test_converter_estado_nome_completo() -> None:
    assert converter_estado("California") == "CA"


def test_converter_estado_sigla_minuscula() -> None:
    assert converter_estado("tx") == "TX"


def test_converter_status_entrega() -> None:
    assert converter_status_entrega(
        "delivered!!!"
    ) == "Delivered"


def test_converter_cidade() -> None:
    assert converter_cidade(
        "san francisco"
    ) == "San Francisco"


def test_converter_cidade_invalida() -> None:
    assert converter_cidade(".") is None


def test_valor_ausente() -> None:
    assert converter_ano(pd.NA) is None