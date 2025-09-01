from flashcard import Flashcard

class Baralho:
    def __init__(self):
        self.cards = []

    def adicionar(self, frente, verso):
        novo = Flashcard(frente, verso)
        self.cards.append(novo)
        return novo

    def listar(self):
        return self.cards
