import json
import os
import time
import uuid

def carregar_dados(caminho, default=None):
    """
    Carrega dados de um arquivo JSON.
    Se o arquivo não existir ou estiver corrompido, retorna o default.
    """
    if default is None:
        default = {}
    if not os.path.exists(caminho):
        return default
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default

def salvar_dados(caminho, dados):
    """
    Salva dados em um arquivo JSON, criando diretórios se necessário.
    """
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def gerar_id_usuario():
    """
    Gera um ID único para usuário no formato USR-xxxxxxxx.
    """
    return f"USR-{uuid.uuid4().hex[:8]}"

def agora_timestamp():
    """
    Retorna o timestamp atual (segundos desde epoch).
    """
    return int(time.time())