import html
import json
import re
from pathlib import Path
from textwrap import dedent
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.agente_ia import (
    CAMINHO_RESUMO_IA,
    exportar_resumo,
    gerar_resumo_executivo,
)

CAMINHO_DADOS = Path("data/processed/vendas_porsche_sanitizadas.xlsx")
CAMINHO_QUALIDADE = Path("data/processed/relatorio_qualidade.json")

COR_FUNDO = "#09090B"
COR_CARD = "#18181B"
COR_TEXTO = "#F5F5F5"
COR_TEXTO_SECUNDARIO = "#A1A1AA"
COR_VERMELHA = "#D5001C"
COR_DOURADA = "#B89A5B"

st.set_page_config(
    page_title="Porsche Sales Intelligence",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def aplicar_estilos() -> None:
    """Aplica o tema escuro do dashboard."""
    st.markdown(
        f"""
        <style>
            :root {{
                --fundo: {COR_FUNDO};
                --card: {COR_CARD};
                --texto: {COR_TEXTO};
                --texto-secundario: {COR_TEXTO_SECUNDARIO};
                --vermelho: {COR_VERMELHA};
                --dourado: {COR_DOURADA};
            }}

            html, body, [data-testid="stAppViewContainer"], .stApp {{
                background:
                    radial-gradient(
                        circle at top right,
                        rgba(213, 0, 28, 0.12),
                        transparent 30rem
                    ),
                    var(--fundo);
                color: var(--texto);
            }}

            .block-container {{
                max-width: 1480px;
                padding-top: 1.4rem;
                padding-bottom: 4rem;
            }}

            header[data-testid="stHeader"] {{
                background: transparent;
            }}

            #MainMenu, footer, div[data-testid="stToolbar"] {{
                visibility: hidden;
            }}

            h1, h2, h3, p, label {{
                color: var(--texto);
            }}

            .hero {{
                min-height: 410px;
                padding: 3.8rem 4rem;
                margin-bottom: 2rem;
                border: 1px solid #2B2B30;
                border-radius: 2.2rem;
                background:
                    linear-gradient(
                        90deg,
                        rgba(0, 0, 0, 0.98) 0%,
                        rgba(0, 0, 0, 0.84) 58%,
                        rgba(30, 0, 4, 0.68) 100%
                    ),
                    radial-gradient(
                        circle at 90% 70%,
                        rgba(213, 0, 28, 0.42),
                        transparent 25rem
                    );
                box-shadow:
                    0 1.5rem 5rem rgba(0, 0, 0, 0.42),
                    inset 0 -3px 0 var(--vermelho);
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
            }}

            .brand-line {{
                display: flex;
                align-items: center;
                gap: 0.9rem;
                color: #D4D4D8;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.19em;
                text-transform: uppercase;
                margin-bottom: 3.2rem;
            }}

            .brand-mark {{
                width: 1.1rem;
                height: 1.1rem;
                display: inline-block;
                background: var(--dourado);
                clip-path: polygon(0 0, 100% 0, 70% 35%, 45% 100%, 0 100%);
            }}

            .hero-title {{
                max-width: 1050px;
                color: var(--texto);
                font-size: clamp(3rem, 6vw, 5.8rem);
                line-height: 0.95;
                font-weight: 650;
                letter-spacing: -0.06em;
                margin: 0;
            }}

            .hero-description {{
                max-width: 850px;
                color: #D4D4D8;
                font-size: 1.15rem;
                line-height: 1.6;
                margin-top: 1.7rem;
            }}

            .section-eyebrow {{
                color: var(--vermelho);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }}

            .section-title {{
                color: var(--texto);
                font-size: clamp(2rem, 3vw, 3.1rem);
                font-weight: 650;
                letter-spacing: -0.045em;
                line-height: 1.05;
                margin-bottom: 0.7rem;
            }}

            .section-description {{
                max-width: 850px;
                color: var(--texto-secundario);
                font-size: 1rem;
                line-height: 1.65;
                margin-bottom: 1.7rem;
            }}

            .selection-bar {{
                background: var(--vermelho);
                color: white;
                border-radius: 1.1rem;
                padding: 1rem 1.3rem;
                margin: 1rem 0 2rem;
                font-weight: 650;
                box-shadow: 0 0.6rem 2rem rgba(213, 0, 28, 0.22);
            }}

            .metric-card {{
                min-height: 168px;
                padding: 1.7rem;
                margin-bottom: 1rem;
                background: linear-gradient(145deg, #242427, #151517);
                border: 1px solid #34343A;
                border-radius: 1.7rem;
                box-shadow:
                    inset 0 1px 0 rgba(255, 255, 255, 0.035),
                    0 1rem 2.5rem rgba(0, 0, 0, 0.22);
            }}

            .metric-card.highlight {{
                border-color: rgba(213, 0, 28, 0.72);
                box-shadow:
                    inset 0 1px 0 rgba(255, 255, 255, 0.035),
                    0 0 2.4rem rgba(213, 0, 28, 0.12);
            }}

            .metric-label {{
                color: var(--texto-secundario);
                font-size: 0.75rem;
                font-weight: 800;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 1.15rem;
            }}

            .metric-value {{
                color: var(--texto);
                font-size: clamp(1.65rem, 2.5vw, 2.8rem);
                line-height: 1.05;
                font-weight: 680;
                letter-spacing: -0.045em;
                word-break: break-word;
            }}

            .metric-detail {{
                color: var(--texto-secundario);
                font-size: 0.85rem;
                line-height: 1.45;
                margin-top: 0.85rem;
            }}

            .panel {{
                padding: 1.8rem;
                background: linear-gradient(145deg, #242427, #151517);
                border: 1px solid #34343A;
                border-radius: 1.9rem;
                box-shadow:
                    inset 0 1px 0 rgba(255, 255, 255, 0.035),
                    0 1rem 2.8rem rgba(0, 0, 0, 0.2);
                margin-bottom: 1rem;
            }}

            .panel-eyebrow {{
                color: var(--vermelho);
                font-size: 0.75rem;
                font-weight: 800;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
            }}

            .panel-title {{
                color: var(--texto);
                font-size: 1.8rem;
                font-weight: 650;
                letter-spacing: -0.035em;
                line-height: 1.1;
                margin-bottom: 0.7rem;
            }}

            .panel-description {{
                color: var(--texto-secundario);
                line-height: 1.55;
                margin-bottom: 1rem;
            }}

            .insight-card {{
                padding: 1.1rem 1.2rem;
                margin-bottom: 0.9rem;
                background: #2D2D31;
                border: 1px solid #3C3C42;
                border-radius: 1.1rem;
            }}

            .insight-card strong {{
                display: block;
                color: var(--texto);
                font-size: 1rem;
                margin-bottom: 0.4rem;
            }}

            .insight-card span {{
                color: var(--texto-secundario);
                font-size: 0.9rem;
                line-height: 1.5;
            }}

            .insight-marker {{
                display: inline-block;
                width: 0.48rem;
                height: 0.48rem;
                margin-right: 0.5rem;
                background: var(--vermelho);
                box-shadow: 0 0 1rem var(--vermelho);
            }}

            .quality-alert {{
                padding: 1.2rem 1.4rem;
                margin-bottom: 1.5rem;
                color: #F4F4F5;
                background: rgba(213, 0, 28, 0.12);
                border: 1px solid rgba(213, 0, 28, 0.45);
                border-radius: 1.1rem;
                line-height: 1.55;
            }}

            .legal-note {{
                color: #71717A;
                font-size: 0.78rem;
                line-height: 1.55;
                margin-top: 3rem;
                padding-top: 1.2rem;
                border-top: 1px solid #27272A;
            }}

            div[data-testid="stSelectbox"] > div > div {{
                min-height: 4.1rem;
                color: var(--texto);
                background: #202023;
                border: 1px solid #34343A;
                border-radius: 1.25rem;
            }}

            div[data-baseweb="select"] span {{
                color: var(--texto);
            }}

            div[data-testid="stSelectbox"] label {{
                color: #D4D4D8 !important;
                font-size: 0.82rem;
                font-weight: 650;
            }}

            div[role="listbox"] {{
                color: var(--texto);
                background: #202023;
            }}

            div[role="option"] {{
                color: var(--texto);
            }}

            div[role="option"]:hover {{
                background: #34343A;
            }}

            .stButton > button {{
                width: 100%;
                min-height: 3.5rem;
                color: white;
                font-weight: 750;
                background: var(--vermelho);
                border: 1px solid var(--vermelho);
                border-radius: 1.1rem;
                box-shadow: 0 0.75rem 2rem rgba(213, 0, 28, 0.22);
            }}

            .stButton > button:hover {{
                color: white;
                background: #F00020;
                border-color: #F00020;
            }}

            div[data-testid="stExpander"] {{
                color: var(--texto);
                background: var(--card);
                border: 1px solid #34343A;
                border-radius: 1.3rem;
            }}

            div[data-testid="stDataFrame"] {{
                border: 1px solid #34343A;
                border-radius: 1rem;
                overflow: hidden;
            }}

            div[data-testid="stMarkdownContainer"] hr, hr {{
                border: 0;
                border-top: 1px solid #29292D;
                margin: 3.2rem 0;
            }}

            @media (max-width: 800px) {{
                .block-container {{
                    padding-left: 1rem;
                    padding-right: 1rem;
                }}

                .hero {{
                    min-height: 330px;
                    padding: 2.2rem 1.6rem;
                    border-radius: 1.5rem;
                }}

                .brand-line {{
                    margin-bottom: 2rem;
                }}

                .metric-card {{
                    min-height: 145px;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def carregar_planilha(caminho: Path) -> pd.DataFrame:
    """Carrega a planilha sanitizada."""
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")

    return pd.read_excel(caminho, sheet_name="Dados Sanitizados")


@st.cache_data
def carregar_json(caminho: Path) -> dict[str, Any]:
    """Carrega um arquivo JSON."""
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo JSON não encontrado: {caminho}")

    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_resumo_ia(caminho: Path) -> str | None:
    """Carrega o último resumo gerado pela IA."""
    if not caminho.exists():
        return None

    conteudo = caminho.read_text(encoding="utf-8").strip()
    return conteudo or None


def formatar_moeda(valor: float) -> str:
    """Formata valores monetários no padrão brasileiro."""
    if pd.isna(valor):
        return "US$ 0,00"

    formatado = f"{float(valor):,.2f}"
    formatado = (
        formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    )
    return f"US$ {formatado}"


def formatar_numero(valor: int | float) -> str:
    """Formata números inteiros."""
    if pd.isna(valor):
        return "0"
    return f"{int(valor):,}".replace(",", ".")


def renderizar_html(conteudo: str) -> None:
    """Renderiza HTML sem recuos que possam virar bloco de código."""
    st.markdown(
        dedent(conteudo).strip(),
        unsafe_allow_html=True,
    )


def criar_titulo_secao(marcador: str, titulo: str, descricao: str) -> None:
    """Cria o título editorial de uma seção."""
    st.markdown(
        f"""
        <div class="section-eyebrow">{html.escape(marcador)}</div>
        <div class="section-title">{html.escape(titulo)}</div>
        <div class="section-description">{html.escape(descricao)}</div>
        """,
        unsafe_allow_html=True,
    )


def criar_card(
    titulo: str,
    valor: str,
    detalhe: str,
    destaque: bool = False,
) -> None:
    """Cria um cartão de indicador."""
    classe = "metric-card highlight" if destaque else "metric-card"
    st.markdown(
        f"""
        <div class="{classe}">
            <div class="metric-label">{html.escape(titulo)}</div>
            <div class="metric-value">{html.escape(valor)}</div>
            <div class="metric-detail">{html.escape(detalhe)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def estilizar_grafico(figura: Any, altura: int = 430) -> None:
    """Aplica o tema escuro aos gráficos Plotly."""
    figura.update_layout(
        height=altura,
        paper_bgcolor=COR_CARD,
        plot_bgcolor=COR_CARD,
        font={
            "family": "Arial, Helvetica, sans-serif",
            "color": COR_TEXTO_SECUNDARIO,
        },
        title={"font": {"size": 19, "color": COR_TEXTO}, "x": 0},
        margin={"l": 20, "r": 20, "t": 65, "b": 30},
        legend={"font": {"color": COR_TEXTO_SECUNDARIO}},
        legend_title_text="",
    )
    figura.update_xaxes(
        showgrid=True,
        gridcolor="#303036",
        zeroline=False,
        color=COR_TEXTO_SECUNDARIO,
    )
    figura.update_yaxes(
        showgrid=False,
        zeroline=False,
        color=COR_TEXTO_SECUNDARIO,
    )


def limpar_filtros() -> None:
    """Restaura todos os filtros para a opção geral."""
    for chave in (
        "filtro_modelo",
        "filtro_ano",
        "filtro_cidade",
        "filtro_pagamento",
        "filtro_estado",
        "filtro_status",
    ):
        st.session_state[chave] = "Todos"


def aplicar_filtros(
    dados: pd.DataFrame,
    modelo: str,
    ano: str,
    cidade: str,
    pagamento: str,
    estado: str,
    status: str,
) -> pd.DataFrame:
    """Aplica os filtros selecionados."""
    filtrados = dados.copy()

    filtros = {
        "porsche_model_sanitized": modelo,
        "city_sanitized": cidade,
        "payment_method_sanitized": pagamento,
        "state_sanitized": estado,
        "delivery_status_sanitized": status,
    }

    for coluna, valor in filtros.items():
        if valor != "Todos":
            filtrados = filtrados[filtrados[coluna] == valor]

    if ano != "Todos":
        filtrados = filtrados[
            filtrados["model_year_sanitized"] == int(ano)
        ]

    return filtrados


def calcular_indicadores(dados: pd.DataFrame) -> dict[str, Any]:
    """Calcula os indicadores do recorte selecionado."""
    if dados.empty:
        return {
            "total": 0,
            "receita": 0.0,
            "ticket_medio": 0.0,
            "modelo_lider": "Sem dados",
            "modelo_lider_total": 0,
            "ano_dominante": "Sem dados",
            "ano_dominante_total": 0,
            "cidade_lider": "Sem dados",
            "cidade_lider_total": 0,
            "pagamento_lider": "Sem dados",
            "pagamento_lider_total": 0,
        }

    precos = dados["sale_price_sanitized"].dropna()
    modelos = dados["porsche_model_sanitized"].dropna().value_counts()
    anos = (
        dados["model_year_sanitized"]
        .dropna()
        .astype(int)
        .value_counts()
    )
    cidades = dados["city_sanitized"].dropna().value_counts()
    pagamentos = (
        dados["payment_method_sanitized"].dropna().value_counts()
    )

    return {
        "total": len(dados),
        "receita": float(precos.sum()),
        "ticket_medio": float(precos.mean()) if not precos.empty else 0.0,
        "modelo_lider": modelos.index[0] if not modelos.empty else "Sem dados",
        "modelo_lider_total": int(modelos.iloc[0]) if not modelos.empty else 0,
        "ano_dominante": int(anos.index[0]) if not anos.empty else "Sem dados",
        "ano_dominante_total": int(anos.iloc[0]) if not anos.empty else 0,
        "cidade_lider": cidades.index[0] if not cidades.empty else "Sem dados",
        "cidade_lider_total": int(cidades.iloc[0]) if not cidades.empty else 0,
        "pagamento_lider": (
            pagamentos.index[0] if not pagamentos.empty else "Sem dados"
        ),
        "pagamento_lider_total": (
            int(pagamentos.iloc[0]) if not pagamentos.empty else 0
        ),
    }


def opcoes_texto(
    dados: pd.DataFrame,
    coluna: str,
) -> list[str]:
    """Retorna opções ordenadas para filtros de texto."""
    valores = dados[coluna].dropna().astype(str).unique().tolist()
    return ["Todos", *sorted(valores)]


def exibir_filtros(dados: pd.DataFrame) -> pd.DataFrame:
    """Exibe os filtros da análise."""
    criar_titulo_secao(
        "Exploração",
        "Controle o recorte da análise",
        (
            "Filtre a base por modelo, ano, cidade, pagamento, estado "
            "ou status de entrega. Os indicadores e gráficos são "
            "atualizados imediatamente."
        ),
    )

    linha_1 = st.columns(2)
    linha_2 = st.columns(2)
    linha_3 = st.columns(2)

    modelos = opcoes_texto(dados, "porsche_model_sanitized")
    cidades = opcoes_texto(dados, "city_sanitized")
    pagamentos = opcoes_texto(dados, "payment_method_sanitized")
    estados = opcoes_texto(dados, "state_sanitized")
    status_disponiveis = opcoes_texto(
        dados, "delivery_status_sanitized"
    )
    anos = [
        "Todos",
        *[
            str(valor)
            for valor in sorted(
                dados["model_year_sanitized"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )
        ],
    ]

    modelo = linha_1[0].selectbox(
        "MODELO DA PORSCHE", modelos, key="filtro_modelo"
    )
    ano = linha_1[1].selectbox(
        "MODEL YEAR", anos, key="filtro_ano"
    )
    cidade = linha_2[0].selectbox(
        "CITY", cidades, key="filtro_cidade"
    )
    pagamento = linha_2[1].selectbox(
        "PAY METHOD", pagamentos, key="filtro_pagamento"
    )
    estado = linha_3[0].selectbox(
        "STATE", estados, key="filtro_estado"
    )
    status = linha_3[1].selectbox(
        "DELIVERY STATUS",
        status_disponiveis,
        key="filtro_status",
    )

    st.button(
        "Limpar filtros",
        on_click=limpar_filtros,
        use_container_width=True,
    )

    dados_filtrados = aplicar_filtros(
        dados,
        modelo=modelo,
        ano=ano,
        cidade=cidade,
        pagamento=pagamento,
        estado=estado,
        status=status,
    )

    st.markdown(
        f"""
        <div class="selection-bar">
            {len(dados_filtrados)} vendas no recorte atual ·
            {len(dados)} registros na base completa
        </div>
        """,
        unsafe_allow_html=True,
    )
    return dados_filtrados


def converter_resumo_para_html(texto: str) -> str:
    """Converte o resumo Markdown em cartões HTML."""
    secoes: list[tuple[str, str]] = []
    titulo_atual: str | None = None
    conteudo_atual: list[str] = []

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        if linha.startswith("### "):
            if titulo_atual:
                secoes.append((titulo_atual, " ".join(conteudo_atual)))
            titulo_atual = linha.removeprefix("### ").strip()
            conteudo_atual = []
        else:
            conteudo_atual.append(linha)

    if titulo_atual:
        secoes.append((titulo_atual, " ".join(conteudo_atual)))

    caixas: list[str] = []
    for titulo, conteudo in secoes:
        conteudo_seguro = html.escape(conteudo)
        conteudo_seguro = re.sub(
            r"\*\*(.+?)\*\*",
            r"<strong>\1</strong>",
            conteudo_seguro,
        )
        caixas.append(
            dedent(
                f"""
                <div class="insight-card">
                <strong>
                    <span class="insight-marker"></span>
                    {html.escape(titulo)}
                </strong>
                <span>{conteudo_seguro}</span>
                </div>
                """
            ).strip()
        )

    return "\n".join(caixas)


def construir_tabela_cidades(dados: pd.DataFrame) -> pd.DataFrame:
    """Cria o ranking agregado por cidade."""
    if dados.empty:
        return pd.DataFrame(
            columns=[
                "cidade",
                "vendas",
                "receita",
                "modelo_lider",
                "pagamento_lider",
            ]
        )

    return (
        dados.groupby("city_sanitized")
        .agg(
            vendas=("sale_id", "count"),
            receita=("sale_price_sanitized", "sum"),
            modelo_lider=(
                "porsche_model_sanitized",
                lambda valores: valores.value_counts().index[0],
            ),
            pagamento_lider=(
                "payment_method_sanitized",
                lambda valores: valores.value_counts().index[0],
            ),
        )
        .reset_index()
        .rename(columns={"city_sanitized": "cidade"})
        .sort_values(
            by=["vendas", "receita"],
            ascending=[False, False],
        )
    )


def exibir_dashboard() -> None:
    """Renderiza o dashboard executivo."""
    aplicar_estilos()

    st.markdown(
        """
        <section class="hero">
            <div class="brand-line">
                <span class="brand-mark"></span>
                Porsche Sales Intelligence
            </div>
            <h1 class="hero-title">
                Performance comercial com precisão esportiva.
            </h1>
            <div class="hero-description">
                Dashboard executivo para descobrir quais modelos
                lideram, quais cidades concentram demanda, quais anos
                dominam o portfólio e como o faturamento se distribui.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    try:
        dados = carregar_planilha(CAMINHO_DADOS)
        qualidade = carregar_json(CAMINHO_QUALIDADE)
    except (FileNotFoundError, ValueError, KeyError) as erro:
        st.error(f"Não foi possível carregar os dados: {erro}")
        st.stop()

    dados_filtrados = exibir_filtros(dados)
    indicadores = calcular_indicadores(dados_filtrados)

    criar_titulo_secao(
        "Performance",
        "Indicadores do recorte",
        (
            "Visão imediata do volume, da receita e das lideranças "
            "comerciais dentro dos filtros selecionados."
        ),
    )

    metricas = st.columns(4)

    total_vendas = formatar_numero(indicadores["total"])
    receita_total = formatar_moeda(indicadores["receita"])
    ticket_medio = formatar_moeda(indicadores["ticket_medio"])
    modelo_lider = str(indicadores["modelo_lider"])
    modelo_lider_total = formatar_numero(
        indicadores["modelo_lider_total"]
    )
    ano_dominante = str(indicadores["ano_dominante"])
    ano_dominante_total = formatar_numero(
        indicadores["ano_dominante_total"]
    )

    with metricas[0]:
        criar_card(
            "Vendas filtradas",
            total_vendas,
            "Registros encontrados no recorte",
            destaque=True,
        )

    with metricas[1]:
        criar_card(
            "Receita total",
            receita_total,
            f"Ticket médio {ticket_medio}",
        )

    with metricas[2]:
        criar_card(
            "Modelo líder",
            modelo_lider,
            f"{modelo_lider_total} pedido(s)",
        )

    with metricas[3]:
        criar_card(
            "Ano dominante",
            ano_dominante,
            f"{ano_dominante_total} pedido(s)",
        )

    if dados_filtrados.empty:
        st.warning(
            "Nenhum registro corresponde à combinação de filtros."
        )
        return

    st.divider()

    criar_titulo_secao(
        "Portfólio",
        "Modelos, anos e receita",
        (
            "Compare a força comercial dos modelos, a distribuição "
            "dos anos e o valor financeiro do recorte."
        ),
    )

    modelos = (
        dados_filtrados.groupby("porsche_model_sanitized")
        .agg(
            vendas=("sale_id", "count"),
            receita=("sale_price_sanitized", "sum"),
        )
        .reset_index()
        .rename(columns={"porsche_model_sanitized": "modelo"})
        .sort_values(by=["vendas", "receita"], ascending=[False, False])
        .head(10)
    )

    anos = (
        dados_filtrados.groupby("model_year_sanitized")
        .agg(vendas=("sale_id", "count"))
        .reset_index()
        .rename(columns={"model_year_sanitized": "ano"})
        .sort_values(by="ano")
    )

    grafico_modelos = px.bar(
        modelos.sort_values(by="vendas", ascending=True),
        x="vendas",
        y="modelo",
        orientation="h",
        custom_data=["receita"],
        title="Principais modelos vendidos",
        labels={"vendas": "Pedidos", "modelo": ""},
        color_discrete_sequence=[COR_VERMELHA],
    )
    grafico_modelos.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Pedidos: %{x}<br>"
            "Receita: US$ %{customdata[0]:,.2f}"
            "<extra></extra>"
        )
    )

    grafico_anos = px.pie(
        anos,
        names="ano",
        values="vendas",
        hole=0.54,
        title="Distribuição por ano do modelo",
        color_discrete_sequence=[
            COR_VERMELHA,
            "#F4F4F5",
            COR_DOURADA,
            "#71717A",
            "#3F3F46",
            "#27272A",
        ],
    )
    grafico_anos.update_traces(
        textinfo="percent+label",
        hovertemplate=(
            "<b>Ano %{label}</b><br>"
            "Pedidos: %{value}<br>"
            "Participação: %{percent}"
            "<extra></extra>"
        ),
    )

    estilizar_grafico(grafico_modelos, altura=500)
    estilizar_grafico(grafico_anos, altura=500)

    col_grafico_1, col_grafico_2 = st.columns([1.25, 1])
    with col_grafico_1:
        st.plotly_chart(grafico_modelos, use_container_width=True)
    with col_grafico_2:
        st.plotly_chart(grafico_anos, use_container_width=True)

    st.divider()

    criar_titulo_secao(
        "Mercado local",
        "Insights por cidade",
        (
            "Ranking de cidades, modelo líder, forma de pagamento "
            "mais frequente e receita gerada."
        ),
    )

    cidades = construir_tabela_cidades(dados_filtrados)
    coluna_cidades, coluna_insights = st.columns([1.15, 1])

    with coluna_cidades:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-eyebrow">Ranking local</div>
                <div class="panel-title">Concentração por cidade</div>
                <div class="panel-description">
                    Cidades ordenadas por volume e receita.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabela_cidades = cidades.head(10).copy()
        tabela_cidades["receita"] = tabela_cidades["receita"].apply(
            formatar_moeda
        )
        st.dataframe(
            tabela_cidades,
            use_container_width=True,
            hide_index=True,
            height=430,
        )

    with coluna_insights:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-eyebrow">
                    Inteligência comercial
                </div>
                <div class="panel-title">
                    Leitura instantânea
                </div>
                <div class="panel-description">
                    Insights determinísticos calculados pelo Python.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        insights = [
            (
                "Cidade com maior concentração",
                (
                    f"{indicadores['cidade_lider']} reúne "
                    f"{formatar_numero(indicadores['cidade_lider_total'])} "
                    "pedido(s) no recorte."
                ),
            ),
            (
                "Modelo com maior tração",
                (
                    f"{indicadores['modelo_lider']} lidera com "
                    f"{formatar_numero(indicadores['modelo_lider_total'])} "
                    "pedido(s)."
                ),
            ),
            (
                "Preferência de pagamento",
                (
                    f"{indicadores['pagamento_lider']} aparece em "
                    f"{formatar_numero(indicadores['pagamento_lider_total'])} "
                    "pedido(s)."
                ),
            ),
            (
                "Ano em evidência",
                (
                    f"O ano {indicadores['ano_dominante']} concentra "
                    f"{formatar_numero(indicadores['ano_dominante_total'])} "
                    "pedido(s)."
                ),
            ),
        ]

        for titulo_insight, texto_insight in insights:
            with st.container(border=True):
                st.markdown(f"**🔴 {titulo_insight}**")
                st.caption(texto_insight)

    st.divider()

    criar_titulo_secao(
        "Inteligência artificial",
        "Leitura executiva da base completa",
        (
            "O texto abaixo é gerado pela Groq a partir dos indicadores "
            "previamente calculados pelo Python."
        ),
    )

    resumo_ia = carregar_resumo_ia(CAMINHO_RESUMO_IA)
    coluna_info, coluna_ia = st.columns([0.85, 1.15])

    with coluna_info:
        qualidade_geral = qualidade.get(
            "qualidade_geral_percentual", 0
        )
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-eyebrow">Base completa</div>
                <div class="panel-title">
                    Qualidade e rastreabilidade
                </div>
                <div class="panel-description">
                    O resumo da IA representa a base inteira, enquanto
                    os gráficos acompanham os filtros.
                </div>
                <div class="quality-alert">
                    <strong>{qualidade_geral}% de qualidade geral.</strong>
                    Há 24 datas inválidas, o que limita análises temporais
                    completas.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with coluna_ia:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-eyebrow">Resumo executivo</div>
                <div class="panel-title">Interpretação assistida</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if resumo_ia:
            st.markdown(
                converter_resumo_para_html(resumo_ia),
                unsafe_allow_html=True,
            )
        else:
            st.info("Nenhum resumo executivo foi gerado.")

        if st.button(
            "Gerar nova leitura da base completa",
            key="botao_ia",
        ):
            try:
                with st.spinner("Interpretando os indicadores..."):
                    novo_resumo = gerar_resumo_executivo()
                    exportar_resumo(novo_resumo, CAMINHO_RESUMO_IA)
                st.success("Nova leitura executiva gerada.")
                st.rerun()
            except Exception as erro:  # noqa: BLE001
                st.error(
                    "Não foi possível gerar a análise. "
                    f"{type(erro).__name__}: {erro}"
                )

    st.divider()

    criar_titulo_secao(
        "Operação",
        "Últimas vendas no recorte",
        (
            "Tabela operacional para consultar preço, status, cidade, "
            "modelo e método de pagamento."
        ),
    )

    colunas_tabela = [
        "sale_id",
        "porsche_model_sanitized",
        "model_year_sanitized",
        "city_sanitized",
        "state_sanitized",
        "payment_method_sanitized",
        "delivery_status_sanitized",
        "sale_price_sanitized",
    ]

    tabela = dados_filtrados[colunas_tabela].copy()
    tabela["sale_price_sanitized"] = tabela[
        "sale_price_sanitized"
    ].apply(formatar_moeda)
    tabela = tabela.rename(
        columns={
            "sale_id": "ID",
            "porsche_model_sanitized": "Modelo",
            "model_year_sanitized": "Ano",
            "city_sanitized": "Cidade",
            "state_sanitized": "Estado",
            "payment_method_sanitized": "Pagamento",
            "delivery_status_sanitized": "Entrega",
            "sale_price_sanitized": "Preço",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    st.markdown(
        """
        <div class="legal-note">
            Projeto educacional independente, inspirado em princípios
            públicos de design digital e sem vínculo oficial com a
            Porsche AG, Porsche Brasil ou suas afiliadas. Os dados
            utilizados são inteiramente fictícios.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    exibir_dashboard()
