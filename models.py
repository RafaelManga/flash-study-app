
class Usuario:
    def __init__(self, uid, nome, email, senha, avatar="", points=0, last_seen=0, friends=None):
        self.id = uid
        self.nome = nome
        self.email = email
        self.senha = senha
        self.avatar = avatar
        self.points = points
        self.last_seen = last_seen
        self.friends = friends if friends is not None else []
        self.competicoes = []  # Lista de competições/desafios ativos

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "avatar": self.avatar,
            "points": self.points,
            "last_seen": self.last_seen,
            "friends": self.friends
            ,"competicoes": self.competicoes
        }
