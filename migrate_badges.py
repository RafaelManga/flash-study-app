#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar badges padrão para o banco de dados
"""

from database import db, Badge

def criar_badges_padrao():
    """Cria todos os badges padrão no banco de dados"""
    badges_data = [
        # Badges de Criação
        (1, "Primeiro Flashcard!", "Crie seu primeiro flashcard", "🎯", "criacao", "comum", {}),
        (2, "Criador de Baralhos", "Crie 5 flashcards", "📚", "criacao", "comum", {"cards_criados": 5}),
        (3, "Mestre dos Baralhos", "Crie 25 flashcards", "📖", "criacao", "raro", {"cards_criados": 25}),
        (4, "Lenda dos Cards", "Crie 100 flashcards", "👑", "criacao", "epico", {"cards_criados": 100}),
        
        # Badges de Estudo
        (5, "Estudioso", "Conclua 3 sessões de estudo", "📖", "estudo", "comum", {"sessoes_concluidas": 3}),
        (6, "Persistente", "Estude por 5 dias consecutivos", "🔥", "estudo", "raro", {"dias_consecutivos": 5}),
        (7, "Maratonista", "Estude por 30 dias consecutivos", "🏃‍♂️", "estudo", "epico", {"dias_consecutivos": 30}),
        (8, "Noite em Claro", "Estude após as 22h", "🌙", "estudo", "comum", {"estudou_noite": True}),
        
        # Badges Sociais
        (9, "Conectado", "Adicione seu primeiro amigo", "🤝", "social", "comum", {}),
        (10, "Popular", "Tenha 10 amigos", "👥", "social", "raro", {"amigos": 10}),
        (11, "Influenciador", "Tenha 50 amigos", "🌟", "social", "epico", {"amigos": 50}),
        (12, "Compartilhador", "Compartilhe seu primeiro baralho", "📤", "social", "comum", {}),
        
        # Badges de Competição
        (13, "Desafiante", "Participe do seu primeiro desafio", "⚔️", "competicao", "comum", {}),
        (14, "Competidor", "Entre em uma competição", "🏆", "competicao", "comum", {}),
        (15, "Vencedor", "Ganhe sua primeira competição", "🥇", "competicao", "raro", {}),
        (16, "Campeão", "Ganhe 10 competições", "👑", "competicao", "epico", {"competicoes_ganhas": 10}),
        (17, "Lenda das Competições", "Ganhe 50 competições", "🏆", "competicao", "lendario", {"competicoes_ganhas": 50}),
        
        # Badges de Pontuação
        (18, "Primeiros Pontos", "Ganhe seus primeiros 100 pontos", "💯", "pontuacao", "comum", {"pontos": 100}),
        (19, "Mil Pontos", "Ganhe 1000 pontos", "💎", "pontuacao", "raro", {"pontos": 1000}),
        (20, "Dez Mil Pontos", "Ganhe 10000 pontos", "💎💎", "pontuacao", "epico", {"pontos": 10000}),
        
        # Badges Divertidos/Memes
        (21, "Madrugador", "Estude antes das 6h", "🌅", "divertido", "comum", {"estudou_madrugada": True}),
        (22, "Viciado em IA", "Use a IA 10 vezes", "🤖", "divertido", "raro", {"uso_ia": 10}),
        (23, "Perfeccionista", "Acertou 100% em um desafio", "✨", "divertido", "raro", {"acerto_perfeito": True}),
        (24, "Velocista", "Complete um desafio em menos de 30 segundos", "⚡", "divertido", "raro", {"tempo_rapido": True}),
        (25, "Colecionador", "Tenha 10 baralhos diferentes", "📚", "divertido", "comum", {"baralhos_diferentes": 10}),
        (26, "Memorizador", "Acertou 50 respostas seguidas", "🧠", "divertido", "raro", {"acertos_seguidos": 50}),
        (27, "Explorador", "Estude em 7 dias diferentes", "🗺️", "divertido", "comum", {"dias_estudo": 7}),
        (28, "Mestre da IA", "Use a IA 50 vezes", "🤖👑", "divertido", "epico", {"uso_ia": 50}),
        (29, "Social Butterfly", "Comente em 20 atividades do feed", "🦋", "social", "raro", {"comentarios": 20}),
        (30, "Lenda Viva", "Complete todos os outros badges", "🏆👑", "especial", "lendario", {"todos_badges": True})
    ]
    
    for badge_id, nome, descricao, icone, categoria, raridade, requisitos in badges_data:
        # Verifica se o badge já existe
        existing_badge = Badge.query.filter_by(id=badge_id).first()
        if not existing_badge:
            badge = Badge(
                id=badge_id,
                nome=nome,
                descricao=descricao,
                icone=icone,
                categoria=categoria,
                raridade=raridade,
                requisitos=requisitos
            )
            db.session.add(badge)
            print(f"✅ Badge criado: {nome}")
        else:
            print(f"⚠️ Badge já existe: {nome}")
    
    try:
        db.session.commit()
        print("🎉 Todos os badges foram criados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar badges: {e}")
        raise

if __name__ == "__main__":
    from app import app
    with app.app_context():
        criar_badges_padrao()


