# Representação de um flashcard

class Flashcard:
    def __init__(self, frente, verso, card_id):
        self.frente = frente
        self.verso = verso
        self.id = card_id

    def to_dict(self):
        return {
            "id": self.id,
            "frente": self.frente,
            "verso": self.verso
        }