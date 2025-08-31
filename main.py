# --- main.py ---
# Código base para o projeto Flash Study

# Lista para armazenar os flashcards em memória.
# No futuro, isso pode ser substituído por um banco de dados.
baralho = []


# --- PARTE 1: DEFINIÇÃO DO FLASHCARD (ESTRUTURA DE DADOS) ---
class Flashcard:
    """
    Representa um único flashcard com uma frente (pergunta) e um verso (resposta).
    """

    def __init__(self, frente, verso):
        self.frente = frente
        self.verso = verso

    def mostrar(self):
        """Exibe a frente e o verso do card."""
        print(f"  Frente: {self.frente} | Verso: {self.verso}")


# --- PARTE 2: FUNCIONALIDADES ESSENCIAIS (CRUD) ---
# Create, Read, Update, Delete

def criar_card():
    """Cria um novo flashcard e o adiciona ao baralho."""
    print("\n--- Criar Novo Flashcard ---")
    frente = input("Digite a pergunta (frente): ")
    verso = input("Digite a resposta (verso): ")

    novo_card = Flashcard(frente, verso)
    baralho.append(novo_card)

    print("\n✅ Flashcard criado com sucesso!")


def listar_cards():
    """Exibe todos os flashcards do baralho (Read)."""
    print("\n--- Meus Flashcards ---")
    if not baralho:
        print("Você ainda não tem nenhum card. Crie um!")
    else:
        for i, card in enumerate(baralho):
            print(f"Card #{i + 1}:")
            card.mostrar()


# --- PARTE 3: FUNCIONALIDADE DE ESTUDO (NAVEGAÇÃO) ---
def iniciar_sessao_estudo():
    """Inicia um loop de estudo para revisar os cards."""
    print("\n--- Sessão de Estudo Iniciada ---")
    if not baralho:
        print("Você não tem cards para estudar. Crie alguns primeiro.")
        return

    print("Para cada card, pressione 'Enter' para ver a resposta.")
    print("Digite 'sair' a qualquer momento para voltar ao menu.")

    for card in baralho:
        print("\n------------------------------")
        print(f"FRENTE: {card.frente}")

        acao = input("Pressione Enter para ver a resposta...")
        if acao.lower() == 'sair':
            break

        print(f"VERSO: {card.verso}")

        feedback = input("Pressione Enter para ir para o próximo card...")
        if feedback.lower() == 'sair':
            break

    print("\n🎉 Sessão de estudo finalizada!")


# --- PARTE 4: MENU PRINCIPAL DA APLICAÇÃO ---
def menu_principal():
    """Exibe o menu principal e gerencia a navegação do usuário."""
    print("\n===============================")
    print("  Bem-vindo(a) ao Flash Study!")
    print("===============================")

    while True:
        print("\nEscolha uma opção:")
        print("  1 - Criar um novo flashcard")
        print("  2 - Listar todos os flashcards")
        print("  3 - Iniciar sessão de estudo")
        print("  4 - Sair")

        escolha = input("> ")

        if escolha == '1':
            criar_card()
        elif escolha == '2':
            listar_cards()
        elif escolha == '3':
            iniciar_sessao_estudo()
        elif escolha == '4':
            print("\nAté a próxima! Bons estudos!")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")


# --- PONTO DE ENTRADA DA APLICAÇÃO ---
# O programa começa a ser executado aqui.
if __name__ == "__main__":
    menu_principal()