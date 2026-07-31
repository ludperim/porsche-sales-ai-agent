from pathlib import Path

import pandas as pd

import re
from datetime import datetime

import json

CAMINHO_ENTRADA = Path("data/raw/vendas_porsche_ficticias.xlsx")
ABA_PLANILHA = "Sanitized"

CAMINHO_SAIDA = Path(
    "data/processed/vendas_porsche_sanitizadas.xlsx"
)

CAMINHO_RELATORIO = Path(
    "data/processed/relatorio_qualidade.json"
)

COLUNAS_ORIGINAIS = [
    "sale_id",
    "sale_date",
    "customer_name",
    "porsche_model",
    "model_year",
    "sale_price",
    "vehicle_mileage",
    "payment_method",
    "city",
    "state",
    "salesperson",
    "delivery_status",
]


def carregar_dados_originais(caminho: Path) -> pd.DataFrame:
    """Carrega apenas as colunas originais da planilha."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    dados = pd.read_excel(
        caminho,
        sheet_name=ABA_PLANILHA,
        usecols=COLUNAS_ORIGINAIS,
    )

    return dados

def sanitizar_datas(dados: pd.DataFrame) -> pd.DataFrame:
    """Converte a coluna de data e identifica valores inválidos."""

    dados_tratados = dados.copy()

    dados_tratados["sale_date_sanitized"] = pd.to_datetime(
        dados_tratados["sale_date"],
        errors="coerce",
        format="mixed",
    )

    dados_tratados["sale_date_status"] = (
        dados_tratados["sale_date_sanitized"]
        .notna()
        .map({True: "válida", False: "inválida"})
    )

    return dados_tratados

def sanitizar_modelos(dados: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços extras sem alterar versões legítimas dos modelos."""

    dados_tratados = dados.copy()

    dados_tratados["porsche_model_sanitized"] = (
        dados_tratados["porsche_model"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    return dados_tratados

def converter_ano(valor: object) -> int | None:
    """Converte diferentes representações de ano para número inteiro."""

    if pd.isna(valor):
        return None

    texto = str(valor).strip().lower()

    # Caso já esteja no formato de quatro dígitos: 2024
    if re.fullmatch(r"\d{4}", texto):
        return int(texto)

    # Formatos como 20-24, 20 24 ou 20/24
    ano_separado = re.fullmatch(r"(\d{2})\D+(\d{2})", texto)

    if ano_separado:
        return int("".join(ano_separado.groups()))

    unidades = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }

    # Formatos como "twenty twenty four"
    palavras = texto.split()

    if (
        len(palavras) == 3
        and palavras[0] == "twenty"
        and palavras[1] == "twenty"
        and palavras[2] in unidades
    ):
        return 2020 + unidades[palavras[2]]

    # Formatos como "two thousand twenty one"
    if (
        len(palavras) == 4
        and palavras[:3] == ["two", "thousand", "twenty"]
        and palavras[3] in unidades
    ):
        return 2020 + unidades[palavras[3]]

    return None

def sanitizar_anos_modelo(dados: pd.DataFrame) -> pd.DataFrame:
    """Converte o ano do modelo e marca valores inválidos."""

    dados_tratados = dados.copy()

    dados_tratados["model_year_sanitized"] = (
        dados_tratados["model_year"]
        .apply(converter_ano)
        .astype("Int64")
    )

    ano_maximo = datetime.now().year + 1

    ano_valido = dados_tratados["model_year_sanitized"].between(
        1900,
        ano_maximo,
    )

    dados_tratados.loc[
        ~ano_valido.fillna(False),
        "model_year_sanitized",
    ] = pd.NA

    dados_tratados["model_year_status"] = (
        dados_tratados["model_year_sanitized"]
        .notna()
        .map({True: "válido", False: "inválido"})
    )

    return dados_tratados

def converter_numero_por_extenso(texto: str) -> float | None:
    """Converte os valores por extenso encontrados na planilha."""

    valores_conhecidos = {
        "eighty two thousand": 82000.0,
        "two hundred thousand": 200000.0,
    }

    return valores_conhecidos.get(texto.strip().lower())

def converter_preco(valor: object) -> float | None:
    """Converte diferentes representações de preço para número decimal."""

    if pd.isna(valor):
        return None

    texto = str(valor).strip().lower()

    texto = (
        texto.replace("usd", "")
        .replace("dollars", "")
        .replace("$", "")
        .strip()
    )

    numero_por_extenso = converter_numero_por_extenso(texto)

    if numero_por_extenso is not None:
        return numero_por_extenso

    # Formatos abreviados como 121k ou 188k
    if texto.endswith("k"):
        numero = texto[:-1].strip()

        try:
            return float(numero.replace(",", ".")) * 1000
        except ValueError:
            return None

    # Formato com ponto e vírgula: 89.750,00
    if "." in texto and "," in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")

    # Apenas vírgula
    elif "," in texto:
        partes = texto.split(",")

        if len(partes[-1]) == 2:
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    # Apenas ponto
    elif "." in texto:
        partes = texto.split(".")

        if len(partes[-1]) == 3:
            texto = texto.replace(".", "")

    try:
        return float(texto)
    except ValueError:
        return None

def sanitizar_precos(dados: pd.DataFrame) -> pd.DataFrame:
    """Converte preços de venda e identifica valores inválidos."""

    dados_tratados = dados.copy()

    dados_tratados["sale_price_sanitized"] = (
        dados_tratados["sale_price"]
        .apply(converter_preco)
        .astype("Float64")
    )

    preco_valido = dados_tratados["sale_price_sanitized"].gt(0)

    dados_tratados.loc[
        ~preco_valido.fillna(False),
        "sale_price_sanitized",
    ] = pd.NA

    dados_tratados["sale_price_status"] = (
        dados_tratados["sale_price_sanitized"]
        .notna()
        .map({True: "válido", False: "inválido"})
    )

    return dados_tratados

UNIDADES_INGLES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


def converter_numero_ingles(texto: str) -> float | None:
    """Converte números simples escritos por extenso em inglês."""

    palavras = (
        texto.lower()
        .replace("-", " ")
        .replace(" and ", " ")
        .split()
    )

    total = 0
    atual = 0

    for palavra in palavras:
        if palavra in UNIDADES_INGLES:
            atual += UNIDADES_INGLES[palavra]
        elif palavra == "hundred":
            atual = max(atual, 1) * 100
        elif palavra == "thousand":
            total += max(atual, 1) * 1000
            atual = 0
        else:
            return None

    return float(total + atual)

def converter_quilometragem(valor: object) -> tuple[float | None, str]:
    """Converte a quilometragem para milhas e informa a unidade original."""

    if pd.isna(valor):
        return None, "desconhecida"

    texto = str(valor).strip().lower()

    if texto in {"new", "new car", "zero", "zero miles"}:
        return 0.0, "milhas"

    unidade_original = "quilômetros" if "km" in texto else "milhas"

    texto_limpo = (
        texto.replace("miles:", "")
        .replace("miles", "")
        .replace("mile", "")
        .replace("mi.", "")
        .replace("mi", "")
        .replace("km", "")
        .strip()
    )

    numero_extenso = converter_numero_ingles(texto_limpo)

    if numero_extenso is not None:
        quilometragem = numero_extenso
    else:
        # Ponto ou vírgula com três dígitos finais representa milhar.
        if re.fullmatch(r"\d+[.,]\d{3}", texto_limpo):
            texto_limpo = texto_limpo.replace(",", "").replace(".", "")

        # Vírgulas restantes são tratadas como separadores de milhar.
        else:
            texto_limpo = texto_limpo.replace(",", "")

        try:
            quilometragem = float(texto_limpo)
        except ValueError:
            return None, unidade_original

    if unidade_original == "quilômetros":
        quilometragem *= 0.621371

    return round(quilometragem, 2), unidade_original

def sanitizar_quilometragem(dados: pd.DataFrame) -> pd.DataFrame:
    """Padroniza a quilometragem em milhas."""

    dados_tratados = dados.copy()

    resultado = dados_tratados["vehicle_mileage"].apply(
        converter_quilometragem
    )

    dados_tratados["vehicle_mileage_sanitized"] = (
        resultado.map(lambda item: item[0]).astype("Float64")
    )

    dados_tratados["vehicle_mileage_original_unit"] = resultado.map(
        lambda item: item[1]
    )

    quilometragem_valida = (
        dados_tratados["vehicle_mileage_sanitized"]
        .ge(0)
        .fillna(False)
    )

    dados_tratados.loc[
        ~quilometragem_valida,
        "vehicle_mileage_sanitized",
    ] = pd.NA

    dados_tratados["vehicle_mileage_status"] = (
        dados_tratados["vehicle_mileage_sanitized"]
        .notna()
        .map({True: "válida", False: "inválida"})
    )

    return dados_tratados

def normalizar_texto(valor: object) -> str | None:
    """Normaliza textos para facilitar comparações entre categorias."""

    if pd.isna(valor):
        return None

    texto = str(valor).strip().lower()

    texto = re.sub(r"[_\-]+", " ", texto)
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()

def converter_forma_pagamento(valor: object) -> str | None:
    """Converte variações de forma de pagamento para categorias padronizadas."""

    texto = normalizar_texto(valor)

    if texto is None:
        return None

    categorias = {
        "cash": "Cash",
        "cash payment": "Cash",

        "credit": "Credit Card",
        "credit card": "Credit Card",
        "creditcard": "Credit Card",
        "credit card payment": "Credit Card",

        "debit card": "Debit Card",

        "wire": "Bank Transfer",
        "wire transfer": "Bank Transfer",
        "wiretransfer": "Bank Transfer",
        "bank wire": "Bank Transfer",
        "bank transfer": "Bank Transfer",
        "ach payment": "Bank Transfer",

        "finance": "Financing",
        "financing": "Financing",
        "financing plan": "Financing",

        "lease": "Leasing",
        "leasing": "Leasing",
        "lease plan": "Leasing",

        "crypto": "Crypto",
        "crypto payment": "Crypto",
    }

    return categorias.get(texto)

def sanitizar_formas_pagamento(dados: pd.DataFrame) -> pd.DataFrame:
    """Padroniza as formas de pagamento e marca valores desconhecidos."""

    dados_tratados = dados.copy()

    dados_tratados["payment_method_sanitized"] = (
        dados_tratados["payment_method"]
        .apply(converter_forma_pagamento)
        .astype("string")
    )

    dados_tratados["payment_method_status"] = (
        dados_tratados["payment_method_sanitized"]
        .notna()
        .map({True: "válida", False: "inválida"})
    )

    return dados_tratados

ESTADOS_EUA = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}

def converter_estado(valor: object) -> str | None:
    """Converte nomes e siglas de estados para siglas em maiúsculas."""

    texto = normalizar_texto(valor)

    if texto is None:
        return None

    if len(texto) == 2 and texto.isalpha():
        return texto.upper()

    return ESTADOS_EUA.get(texto)

def sanitizar_estados(dados: pd.DataFrame) -> pd.DataFrame:
    """Padroniza estados dos EUA para siglas de duas letras."""

    dados_tratados = dados.copy()

    dados_tratados["state_sanitized"] = (
        dados_tratados["state"]
        .apply(converter_estado)
        .astype("string")
    )

    dados_tratados["state_status"] = (
        dados_tratados["state_sanitized"]
        .notna()
        .map({True: "válido", False: "inválido"})
    )

    return dados_tratados

def converter_status_entrega(valor: object) -> str | None:
    """Padroniza os diferentes status de entrega."""

    texto = normalizar_texto(valor)

    if texto is None:
        return None

    if texto in {"delivered", "deliverd"}:
        return "Delivered"

    if texto.startswith("pending"):
        return "Pending"

    if texto in {"in transit", "intransit"}:
        return "In Transit"

    if texto == "shipped":
        return "Shipped"

    if texto.startswith("awaiting"):
        return "Awaiting"

    if texto == "cancelled":
        return "Cancelled"

    return None

def sanitizar_status_entrega(dados: pd.DataFrame) -> pd.DataFrame:
    """Padroniza os status de entrega e marca valores desconhecidos."""

    dados_tratados = dados.copy()

    dados_tratados["delivery_status_sanitized"] = (
        dados_tratados["delivery_status"]
        .apply(converter_status_entrega)
        .astype("string")
    )

    dados_tratados["delivery_status_status"] = (
        dados_tratados["delivery_status_sanitized"]
        .notna()
        .map({True: "válido", False: "inválido"})
    )

    return dados_tratados

def converter_cidade(valor: object) -> str | None:
    """Padroniza nomes de cidades sem depender de uma lista predefinida."""

    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    texto = re.sub(r"\s+", " ", texto)

    if not texto:
        return None

    # A cidade precisa conter pelo menos uma letra.
    if not re.search(r"[A-Za-z]", texto):
        return None

    # Permite letras, espaços, hífens, apóstrofos e pontos.
    if not re.fullmatch(r"[A-Za-zÀ-ÿ\s.'-]+", texto):
        return None

    return texto.title()

def sanitizar_cidades(dados: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes de cidades e identifica valores inválidos."""

    dados_tratados = dados.copy()

    dados_tratados["city_sanitized"] = (
        dados_tratados["city"]
        .apply(converter_cidade)
        .astype("string")
    )

    dados_tratados["city_status"] = (
        dados_tratados["city_sanitized"]
        .notna()
        .map({True: "válida", False: "inválida"})
    )

    return dados_tratados

def sanitizar_dados(dados: pd.DataFrame) -> pd.DataFrame:
    """Executa todas as etapas de sanitização dos dados."""

    dados_tratados = dados.copy()

    dados_tratados = sanitizar_datas(dados_tratados)
    dados_tratados = sanitizar_modelos(dados_tratados)
    dados_tratados = sanitizar_anos_modelo(dados_tratados)
    dados_tratados = sanitizar_precos(dados_tratados)
    dados_tratados = sanitizar_quilometragem(dados_tratados)
    dados_tratados = sanitizar_formas_pagamento(dados_tratados)
    dados_tratados = sanitizar_cidades(dados_tratados)
    dados_tratados = sanitizar_estados(dados_tratados)
    dados_tratados = sanitizar_status_entrega(dados_tratados)

    return dados_tratados

def exportar_dados(
    dados: pd.DataFrame,
    caminho: Path,
) -> None:
    """Exporta os dados sanitizados para uma planilha Excel."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dados.to_excel(
        caminho,
        index=False,
        sheet_name="Dados Sanitizados",
    )

def gerar_relatorio_qualidade(
    dados: pd.DataFrame,
) -> dict:
    """Gera métricas sobre a qualidade dos dados sanitizados."""

    total_registros = len(dados)

    campos_status = {
        "datas": "sale_date_status",
        "anos_modelo": "model_year_status",
        "precos": "sale_price_status",
        "quilometragens": "vehicle_mileage_status",
        "formas_pagamento": "payment_method_status",
        "cidades": "city_status",
        "estados": "state_status",
        "status_entrega": "delivery_status_status",
    }

    resumo_campos = {}

    for nome, coluna in campos_status.items():
        validos = int(
            dados[coluna]
            .isin(["válida", "válido"])
            .sum()
        )

        invalidos = total_registros - validos

        resumo_campos[nome] = {
            "validos": validos,
            "invalidos": invalidos,
            "percentual_valido": round(
                validos / total_registros * 100,
                2,
            ),
        }

    total_validacoes = total_registros * len(campos_status)

    total_validas = sum(
        item["validos"]
        for item in resumo_campos.values()
    )

    return {
        "total_registros": total_registros,
        "total_colunas_exportadas": len(dados.columns),
        "qualidade_geral_percentual": round(
            total_validas / total_validacoes * 100,
            2,
        ),
        "campos": resumo_campos,
    }

def exportar_relatorio_qualidade(
    relatorio: dict,
    caminho: Path,
) -> None:
    """Exporta o relatório de qualidade no formato JSON."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with caminho.open(
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

if __name__ == "__main__":
    dataframe = carregar_dados_originais(CAMINHO_ENTRADA)
    dataframe = sanitizar_dados(dataframe)

    exportar_dados(
        dataframe,
        CAMINHO_SAIDA,
    )

    relatorio = gerar_relatorio_qualidade(dataframe)

    exportar_relatorio_qualidade(
        relatorio,
        CAMINHO_RELATORIO,
    )

    print("SANITIZAÇÃO CONCLUÍDA")
    print("=" * 60)
    print(f"Registros processados: {len(dataframe)}")
    print(f"Arquivo exportado: {CAMINHO_SAIDA}")
    print(f"Relatório exportado: {CAMINHO_RELATORIO}")
    print(
        "Qualidade geral: "
        f"{relatorio['qualidade_geral_percentual']}%"
    )
    colunas_status = [
        "sale_date_status",
        "model_year_status",
        "sale_price_status",
        "vehicle_mileage_status",
        "payment_method_status",
        "city_status",
        "state_status",
        "delivery_status_status",
    ]

    print("\nResumo de qualidade:")

    for coluna in colunas_status:
        print(f"\n{coluna}:")
        print(dataframe[coluna].value_counts(dropna=False))