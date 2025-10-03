import time

class Atividade:
    def __init__(self, tipo, usuario_id, descricao, data=None, likes=None, comentarios=None):
        self.tipo = tipo  # Ex: 'criou_baralho', 'conquista', 'desafio', 'comentario'
        self.usuario_id = usuario_id
        self.descricao = descricao
        self.data = data or time.time()
        self.likes = likes if likes is not None else []
        self.comentarios = comentarios if comentarios is not None else []

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "usuario_id": self.usuario_id,
            "descricao": self.descricao,
            "data": self.data,
            "likes": self.likes,
            "comentarios": self.comentarios
        }

class Comentario:
    def __init__(self, usuario_id, texto, data=None):
        self.usuario_id = usuario_id
        self.texto = texto
        self.data = data or time.time()

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "texto": self.texto,
            "data": self.data
        }

class Relato:
    def __init__(self, nome, categoria, descricao, imagem=None, data=None, status='Em análise'):
        self.nome = nome
        self.categoria = categoria
        self.descricao = descricao
        self.imagem = imagem
        self.data = data
        self.status = status

    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'nome': self.nome,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'imagem': self.imagem,
            'data': self.data,
            'status': self.status
        }

class Usuario:
    def __init__(self, uid, nome, email, senha, avatar="", points=0, last_seen=0, friends=None, badges=None, conquistas=None):
        self.id = uid
        self.nome = nome
        self.email = email
        self.senha = senha
        self.avatar = avatar
        self.points = points
        self.last_seen = last_seen
        self.friends = friends if friends is not None else []
        self.competicoes = []  # Lista de competições/desafios ativos
        self.badges = badges if badges is not None else []  # Lista de badges
        self.conquistas = conquistas if conquistas is not None else []  # Lista de conquistas
