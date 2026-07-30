from pathlib import Path

import pandas as pd


CAMINHO_PLANILHA = Path("data/raw/vendas_porsche_ficticias.xlsx")


def analisar_planilha(caminho: Path) -> None:
    """Exibe informações básicas sobre todas as abas da planilha."""

    if not caminho.exists():
        print(f"Erro: arquivo não encontrado em {caminho}")
        return

    arquivo_excel = pd.ExcelFile(caminho)

    print("=" * 60)
    print("DIAGNÓSTICO INICIAL DA PLANILHA")
    print("=" * 60)
    print(f"Arquivo: {caminho.name}")
    print(f"Quantidade de abas: {len(arquivo_excel.sheet_names)}")
    print(f"Abas encontradas: {arquivo_excel.sheet_names}")

    for nome_aba in arquivo_excel.sheet_names:
        print("\n" + "-" * 60)
        print(f"ABA: {nome_aba}")
        print("-" * 60)

        dados = pd.read_excel(caminho, sheet_name=nome_aba)

        print(f"Quantidade de linhas: {len(dados)}")
        print(f"Quantidade de colunas: {len(dados.columns)}")

        print("\nColunas encontradas:")
        for coluna in dados.columns:
            print(f"- {coluna}")

        print("\nTipos de dados:")
        print(dados.dtypes)

        print("\nValores ausentes por coluna:")
        print(dados.isna().sum())

        print("\nQuantidade de linhas duplicadas:")
        print(dados.duplicated().sum())

        print("\nPrimeiras 5 linhas:")
        print(dados.head())


if __name__ == "__main__":
    analisar_planilha(CAMINHO_PLANILHA)