class Flashcard:
    def __init__(self, frente, verso):
        self.frente = frente
        self.verso = verso
        self.acertos = 0
        self.erros = 0

    def registrar_resposta(self, acertou: bool):
        if acertou:
            self.acertos += 1
        else:
            self.erros += 1
