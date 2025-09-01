class Flashcard:
    def __init__(self, frente, verso):
        self.frente = frente
        self.verso = verso

class Baralho:
    def __init__(self, cards=None):
        self.cards = cards if cards else []

    def adicionar(self, frente, verso):
        self.cards.append({"frente": frente, "verso": verso})
        return {"frente": frente, "verso": verso}

class Usuario:
    def __init__(self, email, senha):
        self.email = email
        self.senha = senha
