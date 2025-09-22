#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar dados dos arquivos JSON para PostgreSQL
"""

import os
import json
from datetime import datetime
from database import db, init_db, migrar_dados_json, User, Baralho, Card, Amizade, Competicao, SessaoEstudo, Atividade, Notificacao, ConviteBaralho, BaralhoMembro, Badge, UserBadge

def carregar_dados_json():
    """Carrega dados dos arquivos JSON existentes"""
    data_dir = "data"
    
    def carregar_arquivo(nome_arquivo, default=None):
        caminho = os.path.join(data_dir, nome_arquivo)
        if not os.path.exists(caminho):
            return default or {}
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                content = f.read()
                return json.loads(content) if content else (default or {})
        except (json.JSONDecodeError, FileNotFoundError):
            return default or {}
    
    return {
        'usuarios': carregar_arquivo('users.json', {}),
        'baralhos': carregar_arquivo('baralhos.json', {}),
        'shared_decks': carregar_arquivo('shared_decks.json', {}),
        'friend_requests': carregar_arquivo('friend_requests.json', {}),
        'deck_invites': carregar_arquivo('deck_invites.json', {})
    }

def migrar_usuarios(usuarios_data):
    """Migra usuários do JSON para o banco"""
    print("🔄 Migrando usuários...")
    
    for user_id, user_data in usuarios_data.items():
        try:
            # Converte timestamps para datetime
            last_seen = datetime.fromtimestamp(user_data.get('last_seen', 0)) if user_data.get('last_seen') else datetime.utcnow()
            data_criacao = datetime.fromtimestamp(user_data.get('data_criacao', 0)) if user_data.get('data_criacao') else datetime.utcnow()
            ultimo_uso_ia = datetime.fromtimestamp(user_data.get('ultimo_uso_ia', 0)) if user_data.get('ultimo_uso_ia') else datetime.utcnow()
            
            # Converte data de nascimento
            data_nascimento = None
            if user_data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.fromtimestamp(user_data['data_nascimento']).date()
                except:
                    pass
            
            user = User(
                id=user_id,
                nome=user_data.get('nome', ''),
                email=user_data.get('email', ''),
                senha=user_data.get('senha', ''),
                avatar=user_data.get('avatar', ''),
                points=user_data.get('points', 0),
                last_seen=last_seen,
                data_criacao=data_criacao,
                data_nascimento=data_nascimento,
                frase_pessoal=user_data.get('frase_pessoal', ''),
                tema=user_data.get('tema', 'dark'),
                ultimo_uso_ia=ultimo_uso_ia
            )
            
            db.session.add(user)
            print(f"  ✅ Usuário migrado: {user.nome}")
            
        except Exception as e:
            print(f"  ❌ Erro ao migrar usuário {user_id}: {e}")
    
    db.session.commit()
    print(f"✅ {len(usuarios_data)} usuários migrados!")

def migrar_baralhos(baralhos_data):
    """Migra baralhos do JSON para o banco"""
    print("🔄 Migrando baralhos...")
    
    total_baralhos = 0
    total_cards = 0
    
    for user_id, user_baralhos in baralhos_data.items():
        if isinstance(user_baralhos, dict):
            for deck_id, deck_data in user_baralhos.items():
                try:
                    baralho = Baralho(
                        id=deck_id,
                        nome=deck_data.get('nome', ''),
                        cor=deck_data.get('cor', '#3b82f6'),
                        user_id=user_id,
                        data_criacao=datetime.utcnow()
                    )
                    
                    db.session.add(baralho)
                    total_baralhos += 1
                    
                    # Migra cards
                    for card_data in deck_data.get('cards', []):
                        card = Card(
                            id=card_data.get('id', ''),
                            frente=card_data.get('frente', ''),
                            verso=card_data.get('verso', ''),
                            baralho_id=deck_id
                        )
                        db.session.add(card)
                        total_cards += 1
                    
                    print(f"  ✅ Baralho migrado: {deck_data.get('nome', deck_id)}")
                    
                except Exception as e:
                    print(f"  ❌ Erro ao migrar baralho {deck_id}: {e}")
    
    db.session.commit()
    print(f"✅ {total_baralhos} baralhos e {total_cards} cards migrados!")

def migrar_baralhos_compartilhados(shared_decks_data):
    """Migra baralhos compartilhados do JSON para o banco"""
    print("🔄 Migrando baralhos compartilhados...")
    
    total_baralhos = 0
    total_membros = 0
    
    for deck_id, deck_data in shared_decks_data.items():
        try:
            baralho = Baralho(
                id=deck_id,
                nome=deck_data.get('nome', ''),
                cor=deck_data.get('cor', '#3b82f6'),
                user_id=deck_data.get('owner', ''),
                data_criacao=datetime.fromtimestamp(deck_data.get('created_at', 0)) if deck_data.get('created_at') else datetime.utcnow(),
                is_shared=True
            )
            
            db.session.add(baralho)
            total_baralhos += 1
            
            # Migra membros
            for member_id in deck_data.get('members', []):
                membro = BaralhoMembro(
                    baralho_id=deck_id,
                    user_id=member_id,
                    permissao_ler=True,
                    permissao_criar=deck_data.get('permissoes', {}).get(member_id, {}).get('criar', False),
                    permissao_deletar=deck_data.get('permissoes', {}).get(member_id, {}).get('deletar', False),
                    data_aceitacao=datetime.utcnow()
                )
                db.session.add(membro)
                total_membros += 1
            
            print(f"  ✅ Baralho compartilhado migrado: {deck_data.get('nome', deck_id)}")
            
        except Exception as e:
            print(f"  ❌ Erro ao migrar baralho compartilhado {deck_id}: {e}")
    
    db.session.commit()
    print(f"✅ {total_baralhos} baralhos compartilhados e {total_membros} membros migrados!")

def migrar_amizades(friend_requests_data):
    """Migra pedidos de amizade do JSON para o banco"""
    print("🔄 Migrando pedidos de amizade...")
    
    total_pedidos = 0
    
    for user_id, requests in friend_requests_data.items():
        for request_data in requests:
            try:
                amizade = Amizade(
                    user1_id=request_data.get('from', ''),
                    user2_id=user_id,
                    status='pendente',
                    data_solicitacao=datetime.fromtimestamp(request_data.get('timestamp', 0)) if request_data.get('timestamp') else datetime.utcnow()
                )
                
                db.session.add(amizade)
                total_pedidos += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar pedido de amizade: {e}")
    
    db.session.commit()
    print(f"✅ {total_pedidos} pedidos de amizade migrados!")

def migrar_convites_baralho(deck_invites_data):
    """Migra convites de baralho do JSON para o banco"""
    print("🔄 Migrando convites de baralho...")
    
    total_convites = 0
    
    for user_id, invites in deck_invites_data.items():
        for invite_data in invites:
            try:
                convite = ConviteBaralho(
                    baralho_id=invite_data.get('deck_id', ''),
                    user_from_id=invite_data.get('from', ''),
                    user_to_id=user_id,
                    status='pendente',
                    data_convite=datetime.fromtimestamp(invite_data.get('timestamp', 0)) if invite_data.get('timestamp') else datetime.utcnow()
                )
                
                db.session.add(convite)
                total_convites += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao migrar convite de baralho: {e}")
    
    db.session.commit()
    print(f"✅ {total_convites} convites de baralho migrados!")

def criar_badges_padrao():
    """Cria badges padrão no banco"""
    print("🔄 Criando badges padrão...")
    
    from migrate_badges import criar_badges_padrao
    criar_badges_padrao()

def main():
    """Função principal de migração"""
    print("🚀 Iniciando migração de dados para PostgreSQL...")
    print("=" * 60)
    
    # Carrega dados do JSON
    dados = carregar_dados_json()
    
    if not any(dados.values()):
        print("⚠️  Nenhum dado encontrado nos arquivos JSON.")
        print("   Certifique-se de que os arquivos estão na pasta 'data/'")
        return
    
    try:
        # Migra cada tipo de dado
        migrar_usuarios(dados['usuarios'])
        migrar_baralhos(dados['baralhos'])
        migrar_baralhos_compartilhados(dados['shared_decks'])
        migrar_amizades(dados['friend_requests'])
        migrar_convites_baralho(dados['deck_invites'])
        criar_badges_padrao()
        
        print("\n" + "=" * 60)
        print("🎉 Migração concluída com sucesso!")
        print("✅ Todos os dados foram transferidos para PostgreSQL")
        print("\n📋 Resumo da migração:")
        print(f"   - Usuários: {len(dados['usuarios'])}")
        print(f"   - Baralhos: {sum(len(user_decks) if isinstance(user_decks, dict) else 0 for user_decks in dados['baralhos'].values())}")
        print(f"   - Baralhos compartilhados: {len(dados['shared_decks'])}")
        print(f"   - Pedidos de amizade: {sum(len(requests) for requests in dados['friend_requests'].values())}")
        print(f"   - Convites de baralho: {sum(len(invites) for invites in dados['deck_invites'].values())}")
        print(f"   - Badges: 30")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

if __name__ == "__main__":
    from app_db import app
    with app.app_context():
        main()



