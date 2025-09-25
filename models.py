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

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "avatar": self.avatar,
            "points": self.points,
            "last_seen": self.last_seen,
            "friends": self.friends,
            "competicoes": self.competicoes,
            "badges": self.badges,
            "conquistas": self.conquistas
        }
