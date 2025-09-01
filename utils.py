import json
import os


def carregar_dados(caminho, default):
    """Carrega dados de um arquivo JSON, se existir e for válido.
    Caso contrário, retorna um valor padrão ({} ou [])."""
    if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
        return default

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return default


def salvar_dados(caminho, dados):
    """Salva os dados em um arquivo JSON, criando a pasta se necessário."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
