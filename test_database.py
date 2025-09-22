#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se a migração para PostgreSQL funcionou
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("🧪 Testando conexão com banco de dados...")
    
    try:
        from app_db import app
        with app.app_context():
            from database import db, User, Baralho, Card, Amizade, Competicao, Badge, UserBadge
            
            # Testa query simples
            result = db.session.execute("SELECT 1").scalar()
            if result == 1:
                print("✅ Conexão com banco de dados OK")
                return True
            else:
                print("❌ Erro na conexão com banco de dados")
                return False
    except Exception as e:
        print(f"❌ Erro ao conectar com banco de dados: {e}")
        return False

def test_models():
    """Testa se os modelos estão funcionando"""
    print("🧪 Testando modelos do banco de dados...")
    
    try:
        from app_db import app
        with app.app_context():
            from database import db, User, Baralho, Card, Amizade, Competicao, Badge, UserBadge
            
            # Testa contagem de registros
            total_users = User.query.count()
            total_baralhos = Baralho.query.count()
            total_cards = Card.query.count()
            total_badges = Badge.query.count()
            
            print(f"  📊 Usuários: {total_users}")
            print(f"  📊 Baralhos: {total_baralhos}")
            print(f"  📊 Cards: {total_cards}")
            print(f"  📊 Badges: {total_badges}")
            
            if total_badges > 0:
                print("✅ Modelos funcionando corretamente")
                return True
            else:
                print("⚠️  Nenhum badge encontrado - execute migrate_badges.py")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar modelos: {e}")
        return False

def test_competitions():
    """Testa funcionalidade de competições"""
    print("🧪 Testando funcionalidade de competições...")
    
    try:
        from app_db import app
        with app.app_context():
            from database import db, User, Competicao, Baralho
            
            # Verifica se há usuários para testar
            users = User.query.limit(2).all()
            if len(users) < 2:
                print("⚠️  Necessário pelo menos 2 usuários para testar competições")
                return True
            
            # Testa criação de competição
            user1, user2 = users[0], users[1]
            
            # Verifica se há baralhos
            baralho = Baralho.query.filter_by(user_id=user1.id).first()
            if not baralho:
                print("⚠️  Necessário pelo menos 1 baralho para testar competições")
                return True
            
            # Cria competição de teste
            comp_id = f"test_comp_{int(time.time())}"
            comp = Competicao(
                id=comp_id,
                user1_id=user1.id,
                user2_id=user2.id,
                baralho_id=baralho.id,
                status='pendente'
            )
            
            db.session.add(comp)
            db.session.commit()
            
            # Verifica se foi criada
            comp_criada = Competicao.query.get(comp_id)
            if comp_criada:
                print("✅ Competição criada com sucesso")
                
                # Remove competição de teste
                db.session.delete(comp_criada)
                db.session.commit()
                
                print("✅ Funcionalidade de competições OK")
                return True
            else:
                print("❌ Erro ao criar competição")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar competições: {e}")
        return False

def test_badges_system():
    """Testa sistema de badges"""
    print("🧪 Testando sistema de badges...")
    
    try:
        from app_db import app
        with app.app_context():
            from badges_db import sistema_badges_db
            from database import User, Badge, UserBadge
            
            # Verifica se há usuários
            user = User.query.first()
            if not user:
                print("⚠️  Necessário pelo menos 1 usuário para testar badges")
                return True
            
            # Testa verificação de badges
            badges_conquistados = sistema_badges_db.verificar_badges_usuario(user.id)
            print(f"  📊 Badges disponíveis para {user.nome}: {len(badges_conquistados)}")
            
            # Testa adição de badge
            if badges_conquistados:
                badge = badges_conquistados[0]
                sucesso = sistema_badges_db.adicionar_badge_usuario(user.id, badge.id)
                if sucesso:
                    print("✅ Badge adicionado com sucesso")
                    
                    # Remove badge de teste
                    user_badge = UserBadge.query.filter_by(
                        user_id=user.id, 
                        badge_id=badge.id
                    ).first()
                    if user_badge:
                        db.session.delete(user_badge)
                        db.session.commit()
                    
                    print("✅ Sistema de badges OK")
                    return True
                else:
                    print("⚠️  Badge já possuído pelo usuário")
                    return True
            else:
                print("⚠️  Nenhum badge disponível para conquista")
                return True
                
    except Exception as e:
        print(f"❌ Erro ao testar sistema de badges: {e}")
        return False

def test_migration():
    """Testa se a migração foi bem-sucedida"""
    print("🧪 Testando migração de dados...")
    
    try:
        from app_db import app
        with app.app_context():
            from database import db, User, Baralho, Card, Amizade, Competicao, Badge
            
            # Verifica se há dados migrados
            total_users = User.query.count()
            total_baralhos = Baralho.query.count()
            total_cards = Card.query.count()
            total_badges = Badge.query.count()
            
            print(f"  📊 Dados migrados:")
            print(f"    - Usuários: {total_users}")
            print(f"    - Baralhos: {total_baralhos}")
            print(f"    - Cards: {total_cards}")
            print(f"    - Badges: {total_badges}")
            
            if total_badges > 0:
                print("✅ Migração aparentemente bem-sucedida")
                return True
            else:
                print("⚠️  Nenhum badge encontrado - execute migrate_badges.py")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar migração: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Testando migração para PostgreSQL...")
    print("=" * 60)
    
    import time
    
    tests = [
        ("Conexão com banco", test_database_connection),
        ("Modelos do banco", test_models),
        ("Sistema de badges", test_badges_system),
        ("Competições", test_competitions),
        ("Migração de dados", test_migration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSOU")
            else:
                print(f"❌ {test_name} - FALHOU")
        except Exception as e:
            print(f"❌ {test_name} - ERRO: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A migração foi bem-sucedida!")
        print("\n📋 Próximos passos:")
        print("1. Execute: python app_db.py")
        print("2. Acesse: http://localhost:5000")
        print("3. Teste as funcionalidades no navegador")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        print("\n🔧 Possíveis soluções:")
        print("1. Execute: python setup_database.py")
        print("2. Execute: python migrate_data.py")
        print("3. Execute: python migrate_badges.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



