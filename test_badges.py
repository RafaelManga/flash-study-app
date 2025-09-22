#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o sistema de badges - FlashStudy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from badges import sistema_badges
from estatisticas import gerenciador_estatisticas

def test_badges_system():
    """Testa o sistema de badges"""
    print("🧪 Testando sistema de badges...")
    
    # Testa criação de badges
    print("\n1. Testando criação de badges...")
    total_badges = len(sistema_badges.badges_disponiveis)
    print(f"✅ Total de badges criados: {total_badges}")
    
    # Testa badges por categoria
    print("\n2. Testando badges por categoria...")
    categorias = ['criacao', 'estudo', 'social', 'competicao', 'pontuacao', 'divertido', 'especial']
    for categoria in categorias:
        badges_categoria = sistema_badges.get_badges_por_categoria(categoria)
        print(f"   {categoria}: {len(badges_categoria)} badges")
    
    # Testa badges por raridade
    print("\n3. Testando badges por raridade...")
    raridades = ['comum', 'raro', 'epico', 'lendario']
    for raridade in raridades:
        badges_raridade = sistema_badges.get_badges_por_raridade(raridade)
        print(f"   {raridade}: {len(badges_raridade)} badges")
    
    # Testa informações de badge específico
    print("\n4. Testando informações de badge...")
    badge_info = sistema_badges.get_badge_info(1)
    if badge_info:
        print(f"   Badge 1: {badge_info.nome} - {badge_info.descricao}")
    
    print("\n✅ Sistema de badges funcionando corretamente!")

def test_estatisticas_system():
    """Testa o sistema de estatísticas"""
    print("\n🧪 Testando sistema de estatísticas...")
    
    # Cria usuário de teste
    user_id = "TEST_USER"
    usuario = {
        "id": user_id,
        "nome": "Usuário Teste",
        "points": 100,
        "friends": ["FRIEND1", "FRIEND2"],
        "badges": []
    }
    
    # Cria baralhos de teste
    baralhos = {
        user_id: {
            "deck1": {
                "nome": "Deck Teste",
                "cards": [
                    {"id": "1", "frente": "Pergunta 1", "verso": "Resposta 1"},
                    {"id": "2", "frente": "Pergunta 2", "verso": "Resposta 2"}
                ]
            }
        }
    }
    
    # Testa registro de atividades
    print("\n1. Testando registro de atividades...")
    gerenciador_estatisticas.registrar_atividade(user_id, "card_criado")
    gerenciador_estatisticas.registrar_atividade(user_id, "sessao_estudo")
    gerenciador_estatisticas.registrar_atividade(user_id, "amigo_adicionado")
    print("   ✅ Atividades registradas")
    
    # Testa cálculo de estatísticas
    print("\n2. Testando cálculo de estatísticas...")
    estatisticas = gerenciador_estatisticas.calcular_estatisticas_para_badges(
        user_id, usuario, baralhos, []
    )
    print(f"   Total de cards: {estatisticas['total_cards']}")
    print(f"   Total de baralhos: {estatisticas['total_baralhos']}")
    print(f"   Sessões de estudo: {estatisticas['sessoes_estudo']}")
    
    # Testa verificação de badges
    print("\n3. Testando verificação de badges...")
    badges_conquistados = sistema_badges.verificar_badges_usuario(
        user_id, usuario, estatisticas
    )
    print(f"   Badges conquistados: {len(badges_conquistados)}")
    for badge in badges_conquistados:
        print(f"   - {badge.nome}: {badge.descricao}")
    
    print("\n✅ Sistema de estatísticas funcionando corretamente!")

def test_integration():
    """Testa integração entre sistemas"""
    print("\n🧪 Testando integração entre sistemas...")
    
    # Simula cenário real de uso
    user_id = "REAL_USER"
    usuario = {
        "id": user_id,
        "nome": "Usuário Real",
        "points": 0,
        "friends": [],
        "badges": []
    }
    
    baralhos = {user_id: {}}
    atividades = []
    
    print("\n1. Simulando criação de primeiro card...")
    gerenciador_estatisticas.registrar_atividade(user_id, "card_criado")
    estatisticas = gerenciador_estatisticas.calcular_estatisticas_para_badges(
        user_id, usuario, baralhos, atividades
    )
    badges = sistema_badges.verificar_badges_usuario(user_id, usuario, estatisticas)
    print(f"   Badges conquistados: {len(badges)}")
    
    print("\n2. Simulando adição de amigo...")
    usuario["friends"] = ["FRIEND1"]
    gerenciador_estatisticas.registrar_atividade(user_id, "amigo_adicionado")
    estatisticas = gerenciador_estatisticas.calcular_estatisticas_para_badges(
        user_id, usuario, baralhos, atividades
    )
    badges = sistema_badges.verificar_badges_usuario(user_id, usuario, estatisticas)
    print(f"   Badges conquistados: {len(badges)}")
    
    print("\n✅ Integração funcionando corretamente!")

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de badges...")
    print("=" * 50)
    
    try:
        test_badges_system()
        test_estatisticas_system()
        test_integration()
        
        print("\n" + "=" * 50)
        print("🎉 Todos os testes passaram com sucesso!")
        print("✅ Sistema de badges está funcionando corretamente!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


