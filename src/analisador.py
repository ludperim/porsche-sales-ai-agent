import json
from pathlib import Path

import pandas as pd


CAMINHO_DADOS = Path(
    "data/processed/vendas_porsche_sanitizadas.xlsx"
)

CAMINHO_RESUMO = Path(
    "data/processed/resumo_indicadores.json"
)


def carregar_dados_sanitizados(caminho: Path) -> pd.DataFrame:
    """Carrega a planilha produzida pelo processo de sanitização."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo sanitizado não encontrado: {caminho}"
        )

    return pd.read_excel(
        caminho,
        sheet_name="Dados Sanitizados",
    )


def calcular_indicadores_gerais(
    dados: pd.DataFrame,
) -> dict:
    """Calcula os principais indicadores gerais de vendas."""

    precos_validos = dados["sale_price_sanitized"].dropna()

    vendas_entregues = dados[
        dados["delivery_status_sanitized"] == "Delivered"
    ]

    vendas_canceladas = dados[
        dados["delivery_status_sanitized"] == "Cancelled"
    ]

    faturamento_bruto = float(precos_validos.sum())

    faturamento_realizado = float(
        vendas_entregues["sale_price_sanitized"].sum()
    )

    faturamento_cancelado = float(
        vendas_canceladas["sale_price_sanitized"].sum()
    )

    return {
        "total_pedidos": len(dados),
        "faturamento_bruto": round(faturamento_bruto, 2),
        "faturamento_realizado": round(
            faturamento_realizado,
            2,
        ),
        "faturamento_cancelado": round(
            faturamento_cancelado,
            2,
        ),
        "ticket_medio": round(
            float(precos_validos.mean()),
            2,
        ),
        "menor_venda": round(
            float(precos_validos.min()),
            2,
        ),
        "maior_venda": round(
            float(precos_validos.max()),
            2,
        ),
        "vendas_entregues": len(vendas_entregues),
        "vendas_canceladas": len(vendas_canceladas),
    }


def calcular_indicadores_por_modelo(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Agrupa quantidade de pedidos e faturamento por modelo."""

    resumo = (
        dados.groupby(
            "porsche_model_sanitized",
            dropna=False,
        )
        .agg(
            quantidade_vendas=("sale_id", "count"),
            faturamento_total=(
                "sale_price_sanitized",
                "sum",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "porsche_model_sanitized": "modelo",
            }
        )
    )

    resumo["faturamento_total"] = (
        resumo["faturamento_total"]
        .round(2)
    )

    return resumo.sort_values(
        by=[
            "quantidade_vendas",
            "faturamento_total",
        ],
        ascending=[False, False],
    )


def calcular_indicadores_por_estado(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Agrupa quantidade de pedidos e faturamento por estado."""

    resumo = (
        dados.groupby(
            "state_sanitized",
            dropna=False,
        )
        .agg(
            quantidade_vendas=("sale_id", "count"),
            faturamento_total=(
                "sale_price_sanitized",
                "sum",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "state_sanitized": "estado",
            }
        )
    )

    resumo["faturamento_total"] = (
        resumo["faturamento_total"]
        .round(2)
    )

    return resumo.sort_values(
        by="faturamento_total",
        ascending=False,
    )


def calcular_indicadores_por_pagamento(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """Agrupa pedidos e faturamento por forma de pagamento."""

    resumo = (
        dados.groupby(
            "payment_method_sanitized",
            dropna=False,
        )
        .agg(
            quantidade_vendas=("sale_id", "count"),
            faturamento_total=(
                "sale_price_sanitized",
                "sum",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "payment_method_sanitized": "forma_pagamento",
            }
        )
    )

    resumo["faturamento_total"] = (
        resumo["faturamento_total"]
        .round(2)
    )

    return resumo.sort_values(
        by="faturamento_total",
        ascending=False,
    )


def gerar_resumo_indicadores(
    dados: pd.DataFrame,
) -> dict:
    """Gera um resumo estruturado para o dashboard e o agente."""

    gerais = calcular_indicadores_gerais(dados)
    modelos = calcular_indicadores_por_modelo(dados)
    estados = calcular_indicadores_por_estado(dados)
    pagamentos = calcular_indicadores_por_pagamento(dados)

    maior_quantidade = int(
        modelos["quantidade_vendas"].max()
    )

    modelos_mais_vendidos = (
        modelos[
            modelos["quantidade_vendas"]
            == maior_quantidade
        ]["modelo"]
        .tolist()
    )

    modelo_maior_faturamento = (
        modelos
        .sort_values(
            by="faturamento_total",
            ascending=False,
        )
        .iloc[0]
    )

    return {
        "indicadores_gerais": gerais,
        "destaques": {
            "modelos_mais_vendidos": modelos_mais_vendidos,
            "quantidade_por_modelo_lider": maior_quantidade,
            "modelo_maior_faturamento": (
                modelo_maior_faturamento["modelo"]
            ),
            "valor_modelo_maior_faturamento": float(
                modelo_maior_faturamento["faturamento_total"]
            ),
            "estado_maior_faturamento": (
                estados.iloc[0]["estado"]
            ),
            "valor_estado_maior_faturamento": float(
                estados.iloc[0]["faturamento_total"]
            ),
            "forma_pagamento_maior_faturamento": (
                pagamentos.iloc[0]["forma_pagamento"]
            ),
            "valor_pagamento_maior_faturamento": float(
                pagamentos.iloc[0]["faturamento_total"]
            ),
        },
        "top_10_modelos": modelos.head(10).to_dict(
            orient="records"
        ),
        "top_10_estados": estados.head(10).to_dict(
            orient="records"
        ),
        "formas_pagamento": pagamentos.to_dict(
            orient="records"
        ),
    }


def exportar_resumo(
    resumo: dict,
    caminho: Path,
) -> None:
    """Exporta o resumo dos indicadores em JSON."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with caminho.open(
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            resumo,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    dataframe = carregar_dados_sanitizados(CAMINHO_DADOS)

    resumo = gerar_resumo_indicadores(dataframe)

    exportar_resumo(
        resumo,
        CAMINHO_RESUMO,
    )

    print("ANÁLISE CONCLUÍDA")
    print("=" * 60)
    print(
        f"Total de pedidos: "
        f"{resumo['indicadores_gerais']['total_pedidos']}"
    )
    print(
        "Faturamento bruto: "
        f"US$ "
        f"{resumo['indicadores_gerais']['faturamento_bruto']:,.2f}"
    )
    print(
        "Faturamento realizado: "
        f"US$ "
        f"{resumo['indicadores_gerais']['faturamento_realizado']:,.2f}"
    )
    print(
        f"Resumo exportado: {CAMINHO_RESUMO}"
    )