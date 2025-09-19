import time

class Competicao:
    def __init__(self, id, user1, user2, deck_id, status="pendente", pontuacao1=0, pontuacao2=0, inicio=None, fim=None):
        self.id = id
        self.user1 = user1
        self.user2 = user2
        self.deck_id = deck_id
        self.status = status  # pendente, ativa, finalizada
        self.pontuacao1 = pontuacao1
        self.pontuacao2 = pontuacao2
        self.inicio = inicio if inicio else time.time()
        self.fim = fim

    def to_dict(self):
        return {
            "id": self.id,
            "user1": self.user1,
            "user2": self.user2,
            "deck_id": self.deck_id,
            "status": self.status,
            "pontuacao1": self.pontuacao1,
            "pontuacao2": self.pontuacao2,
            "inicio": self.inicio,
            "fim": self.fim
        }

def criar_competicao(user1, user2, deck_id):
    comp_id = f"comp_{int(time.time())}_{user1}_{user2}"
    return Competicao(comp_id, user1, user2, deck_id)
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