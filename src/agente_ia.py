import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    Groq,
    RateLimitError,
)


CAMINHO_PROMPT = Path(
    "prompts/resumo_executivo.md"
)

CAMINHO_INDICADORES = Path(
    "data/processed/resumo_indicadores.json"
)

CAMINHO_QUALIDADE = Path(
    "data/processed/relatorio_qualidade.json"
)

CAMINHO_RESUMO_IA = Path(
    "data/processed/resumo_executivo_ia.txt"
)

MODELO_IA = "llama-3.3-70b-versatile"


def carregar_texto(caminho: Path) -> str:
    """Carrega um arquivo de texto em UTF-8."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    return caminho.read_text(
        encoding="utf-8"
    ).strip()


def carregar_json(caminho: Path) -> dict:
    """Carrega um arquivo JSON."""

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        return json.load(arquivo)


def montar_contexto(
    indicadores: dict,
    qualidade: dict,
) -> str:
    """Monta o contexto estruturado enviado ao modelo."""

    dados = {
        "indicadores_de_vendas": indicadores,
        "qualidade_dos_dados": qualidade,
    }

    return json.dumps(
        dados,
        ensure_ascii=False,
        indent=2,
    )


def gerar_resumo_executivo() -> str:
    """Gera um resumo executivo usando a API da Groq."""

    load_dotenv()

    chave_api = os.getenv("GROQ_API_KEY")

    if not chave_api:
        raise RuntimeError(
            "A variável GROQ_API_KEY não foi configurada."
        )

    prompt = carregar_texto(CAMINHO_PROMPT)
    indicadores = carregar_json(CAMINHO_INDICADORES)
    qualidade = carregar_json(CAMINHO_QUALIDADE)

    contexto = montar_contexto(
        indicadores,
        qualidade,
    )

    cliente = Groq(
        api_key=chave_api,
    )

    resposta = cliente.chat.completions.create(
        model=MODELO_IA,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": (
                    "Produza o resumo executivo usando apenas "
                    "os dados JSON apresentados abaixo.\n\n"
                    f"{contexto}"
                ),
            },
        ],
        temperature=0.0,
        max_completion_tokens=1800,
    )

    resumo = resposta.choices[0].message.content

    if resumo is None or not resumo.strip():
        raise RuntimeError(
            "A API retornou uma resposta vazia."
        )

    return resumo.strip()


def exportar_resumo(
    resumo: str,
    caminho: Path,
) -> None:
    """Salva o resumo executivo em um arquivo de texto."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho.write_text(
        resumo,
        encoding="utf-8",
    )


def executar_agente() -> None:
    """Executa o agente e trata erros de maneira controlada."""

    try:
        resumo = gerar_resumo_executivo()

        exportar_resumo(
            resumo,
            CAMINHO_RESUMO_IA,
        )

        print("RESUMO EXECUTIVO GERADO")
        print("=" * 60)
        print(resumo)

        print("\nArquivo exportado:")
        print(CAMINHO_RESUMO_IA)

    except FileNotFoundError as erro:
        print(f"Erro de arquivo: {erro}")

    except AuthenticationError:
        print(
            "Erro de autenticação: verifique a chave da Groq."
        )

    except RateLimitError:
        print(
            "Limite gratuito ou cota da Groq atingido."
        )

    except APIConnectionError:
        print(
            "Não foi possível conectar à API da Groq."
        )

    except APIStatusError as erro:
        print(
            "A API da Groq retornou um erro: "
            f"status {erro.status_code}."
        )

    except RuntimeError as erro:
        print(f"Configuração pendente: {erro}")

    except Exception as erro:
        print(
            "O agente encontrou um erro inesperado: "
            f"{type(erro).__name__}: {erro}"
        )


if __name__ == "__main__":
    executar_agente()