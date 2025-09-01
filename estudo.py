def iniciar_sessao(baralho):
    if not baralho.cards:
        print("⚠ Nenhum flashcard disponível.")
        return

    print("\n--- Sessão de Estudo ---")
    for card in baralho.cards:
        print(f"\nPergunta: {card.frente}")
        input("Pressione Enter para ver a resposta...")
        print(f"Resposta: {card.verso}")
