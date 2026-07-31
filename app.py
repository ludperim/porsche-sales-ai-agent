import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.agente_ia import (
    CAMINHO_RESUMO_IA,
    exportar_resumo,
    gerar_resumo_executivo,
)


CAMINHO_DADOS = Path(
    "data/processed/vendas_porsche_sanitizadas.xlsx"
)

CAMINHO_RESUMO = Path(
    "data/processed/resumo_indicadores.json"
)

CAMINHO_QUALIDADE = Path(
    "data/processed/relatorio_qualidade.json"
)


st.set_page_config(
    page_title="Porsche Sales AI Agent",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def carregar_planilha(caminho: Path) -> pd.DataFrame:
    """Carrega a planilha sanitizada."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Planilha não encontrada: {caminho}"
        )

    return pd.read_excel(
        caminho,
        sheet_name="Dados Sanitizados",
    )


@st.cache_data
def carregar_json(caminho: Path) -> dict:
    """Carrega um arquivo JSON."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo JSON não encontrado: {caminho}"
        )

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        return json.load(arquivo)


def carregar_resumo_ia(caminho: Path) -> str | None:
    """Carrega o resumo executivo gerado pela IA."""

    if not caminho.exists():
        return None

    conteudo = caminho.read_text(
        encoding="utf-8"
    ).strip()

    return conteudo or None


def formatar_moeda(valor: float) -> str:
    """Formata valores monetários em dólar."""

    return f"US$ {valor:,.2f}"


def exibir_resumo_ia() -> None:
    """Exibe e permite atualizar o resumo executivo."""

    st.subheader("Resumo executivo com IA")

    st.caption(
        "O texto é produzido pela Groq a partir dos indicadores "
        "calculados pelo Python. A IA não realiza os cálculos."
    )

    resumo_atual = carregar_resumo_ia(
        CAMINHO_RESUMO_IA
    )

    if resumo_atual:
        st.markdown(resumo_atual)
    else:
        st.info(
            "Nenhum resumo executivo foi gerado ainda."
        )

    if st.button(
        "Gerar novo resumo com IA",
        type="primary",
    ):
        try:
            with st.spinner(
                "Analisando os indicadores..."
            ):
                novo_resumo = gerar_resumo_executivo()

                exportar_resumo(
                    novo_resumo,
                    CAMINHO_RESUMO_IA,
                )

            st.success(
                "Resumo executivo gerado com sucesso."
            )

            st.markdown(novo_resumo)

        except Exception as erro:
            st.error(
                "Não foi possível gerar o resumo executivo. "
                f"Detalhes: {type(erro).__name__}: {erro}"
            )


def exibir_dashboard() -> None:
    """Renderiza o dashboard principal."""

    st.title("Porsche Sales AI Agent")

    st.write(
        "Dashboard criado a partir de uma planilha fictícia "
        "de vendas da Porsche."
    )

    try:
        dados = carregar_planilha(CAMINHO_DADOS)
        resumo = carregar_json(CAMINHO_RESUMO)
        qualidade = carregar_json(CAMINHO_QUALIDADE)

    except FileNotFoundError as erro:
        st.error(str(erro))
        st.stop()

    indicadores = resumo["indicadores_gerais"]

    st.subheader("Indicadores gerais")

    coluna_1, coluna_2, coluna_3, coluna_4 = st.columns(4)

    coluna_1.metric(
        "Total de pedidos",
        indicadores["total_pedidos"],
    )

    coluna_2.metric(
        "Faturamento bruto",
        formatar_moeda(
            indicadores["faturamento_bruto"]
        ),
    )

    coluna_3.metric(
        "Faturamento realizado",
        formatar_moeda(
            indicadores["faturamento_realizado"]
        ),
    )

    coluna_4.metric(
        "Ticket médio",
        formatar_moeda(
            indicadores["ticket_medio"]
        ),
    )

    coluna_5, coluna_6, coluna_7, coluna_8 = st.columns(4)

    coluna_5.metric(
        "Maior venda",
        formatar_moeda(
            indicadores["maior_venda"]
        ),
    )

    coluna_6.metric(
        "Menor venda",
        formatar_moeda(
            indicadores["menor_venda"]
        ),
    )

    coluna_7.metric(
        "Vendas entregues",
        indicadores["vendas_entregues"],
    )

    coluna_8.metric(
        "Vendas canceladas",
        indicadores["vendas_canceladas"],
    )

    st.divider()

    exibir_resumo_ia()

    st.divider()

    st.subheader("Qualidade dos dados")

    st.metric(
        "Qualidade geral",
        f"{qualidade['qualidade_geral_percentual']}%",
    )

    qualidade_campos = pd.DataFrame(
        [
            {
                "campo": campo,
                "validos": valores["validos"],
                "invalidos": valores["invalidos"],
                "percentual_valido": valores[
                    "percentual_valido"
                ],
            }
            for campo, valores in qualidade[
                "campos"
            ].items()
        ]
    )

    grafico_qualidade = px.bar(
        qualidade_campos,
        x="campo",
        y="percentual_valido",
        title="Percentual de validade por campo",
        labels={
            "campo": "Campo",
            "percentual_valido": "Percentual válido",
        },
    )

    st.plotly_chart(
        grafico_qualidade,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Análise por modelo")

    modelos = pd.DataFrame(
        resumo["top_10_modelos"]
    )

    grafico_modelos = px.bar(
        modelos,
        x="modelo",
        y="faturamento_total",
        hover_data=["quantidade_vendas"],
        title="Top 10 modelos por faturamento",
        labels={
            "modelo": "Modelo",
            "faturamento_total": "Faturamento",
            "quantidade_vendas": "Quantidade",
        },
    )

    st.plotly_chart(
        grafico_modelos,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Análise por estado")

    estados = pd.DataFrame(
        resumo["top_10_estados"]
    )

    grafico_estados = px.bar(
        estados,
        x="estado",
        y="faturamento_total",
        hover_data=["quantidade_vendas"],
        title="Top 10 estados por faturamento",
        labels={
            "estado": "Estado",
            "faturamento_total": "Faturamento",
            "quantidade_vendas": "Quantidade",
        },
    )

    st.plotly_chart(
        grafico_estados,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Formas de pagamento")

    pagamentos = pd.DataFrame(
        resumo["formas_pagamento"]
    )

    grafico_pagamentos = px.pie(
        pagamentos,
        names="forma_pagamento",
        values="faturamento_total",
        title=(
            "Participação no faturamento "
            "por forma de pagamento"
        ),
    )

    st.plotly_chart(
        grafico_pagamentos,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Dados sanitizados")

    st.dataframe(
        dados,
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    exibir_dashboard()