from baralho import Baralho
from estudo import iniciar_sessao

def menu():
    baralho = Baralho()

    while True:
        print("\n===============================")
        print("      📚 Flash Study (CLI)")
        print("===============================")
        print("1 - Criar flashcard")
        print("2 - Listar flashcards")
        print("3 - Estudar")
        print("4 - Sair")

        opcao = input("> ")

        if opcao == "1":
            frente = input("Digite a pergunta: ")
            verso = input("Digite a resposta: ")
            baralho.adicionar(frente, verso)
            print("✅ Card adicionado!")
        elif opcao == "2":
            baralho.listar()
        elif opcao == "3":
            iniciar_sessao(baralho)
        elif opcao == "4":
            print("👋 Até a próxima!")
            break
        else:
            print("❌ Opção inválida.")

if __name__ == "__main__":
    menu()
