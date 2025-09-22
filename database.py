#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração do banco de dados PostgreSQL - FlashStudy
"""

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://flashstudy:flashstudy123@localhost:5432/flashstudy_db')

db = SQLAlchemy()

def init_db(app):
    """Inicializa o banco de dados"""
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados inicializado com sucesso!")

# Modelos do banco de dados

class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='')
    points = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_nascimento = db.Column(db.Date)
    frase_pessoal = db.Column(db.Text)
    tema = db.Column(db.String(10), default='dark')
    ultimo_uso_ia = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    baralhos = db.relationship('Baralho', backref='dono', lazy='dynamic', cascade='all, delete-orphan')
    amizades_enviadas = db.relationship('Amizade', foreign_keys='Amizade.user1_id', backref='user1', lazy='dynamic')
    amizades_recebidas = db.relationship('Amizade', foreign_keys='Amizade.user2_id', backref='user2', lazy='dynamic')
    competicoes_enviadas = db.relationship('Competicao', foreign_keys='Competicao.user1_id', backref='user1', lazy='dynamic')
    competicoes_recebidas = db.relationship('Competicao', foreign_keys='Competicao.user2_id', backref='user2', lazy='dynamic')
    badges_conquistados = db.relationship('UserBadge', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    atividades = db.relationship('Atividade', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    sessoes_estudo = db.relationship('SessaoEstudo', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    notificacoes = db.relationship('Notificacao', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.senha = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica a senha do usuário"""
        return check_password_hash(self.senha, password)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'avatar': self.avatar,
            'points': self.points,
            'last_seen': self.last_seen.timestamp() if self.last_seen else 0,
            'data_criacao': self.data_criacao.timestamp() if self.data_criacao else 0,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else '',
            'frase_pessoal': self.frase_pessoal or '',
            'tema': self.tema,
            'friends': [amizade.user2_id if amizade.user1_id == self.id else amizade.user1_id 
                       for amizade in self.amizades_enviadas.union(self.amizades_recebidas).filter_by(status='aceita')]
        }

class Baralho(db.Model):
    """Modelo de baralho"""
    __tablename__ = 'baralhos'
    
    id = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cor = db.Column(db.String(7), default='#3b82f6')
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    cards = db.relationship('Card', backref='baralho', lazy='dynamic', cascade='all, delete-orphan')
    membros = db.relationship('BaralhoMembro', backref='baralho', lazy='dynamic', cascade='all, delete-orphan')
    competicoes = db.relationship('Competicao', backref='baralho', lazy='dynamic')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cor': self.cor,
            'cards': [card.to_dict() for card in self.cards],
            'data_criacao': self.data_criacao.timestamp() if self.data_criacao else 0,
            'is_shared': self.is_shared
        }

class Card(db.Model):
    """Modelo de card"""
    __tablename__ = 'cards'
    
    id = db.Column(db.String(50), primary_key=True)
    frente = db.Column(db.Text, nullable=False)
    verso = db.Column(db.Text, nullable=False)
    baralho_id = db.Column(db.String(50), db.ForeignKey('baralhos.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'frente': self.frente,
            'verso': self.verso,
            'data_criacao': self.data_criacao.timestamp() if self.data_criacao else 0
        }

class Amizade(db.Model):
    """Modelo de amizade"""
    __tablename__ = 'amizades'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aceita, recusada
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime)
    
    # Garantir que não há duplicatas
    __table_args__ = (db.UniqueConstraint('user1_id', 'user2_id', name='unique_amizade'),)

class BaralhoMembro(db.Model):
    """Modelo de membro de baralho compartilhado"""
    __tablename__ = 'baralho_membros'
    
    id = db.Column(db.Integer, primary_key=True)
    baralho_id = db.Column(db.String(50), db.ForeignKey('baralhos.id'), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    permissao_ler = db.Column(db.Boolean, default=True)
    permissao_criar = db.Column(db.Boolean, default=False)
    permissao_deletar = db.Column(db.Boolean, default=False)
    data_convite = db.Column(db.DateTime, default=datetime.utcnow)
    data_aceitacao = db.Column(db.DateTime)
    
    # Garantir que não há duplicatas
    __table_args__ = (db.UniqueConstraint('baralho_id', 'user_id', name='unique_baralho_membro'),)

class Competicao(db.Model):
    """Modelo de competição"""
    __tablename__ = 'competicoes'
    
    id = db.Column(db.String(50), primary_key=True)
    user1_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    baralho_id = db.Column(db.String(50), db.ForeignKey('baralhos.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aceita, recusada, ativa, finalizada
    pontuacao1 = db.Column(db.Integer, default=0)
    pontuacao2 = db.Column(db.Integer, default=0)
    vencedor_id = db.Column(db.String(20), db.ForeignKey('users.id'))
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    data_aceitacao = db.Column(db.DateTime)
    
    # Relacionamento com vencedor
    vencedor = db.relationship('User', foreign_keys=[vencedor_id], backref='competicoes_ganhas')

class SessaoEstudo(db.Model):
    """Modelo de sessão de estudo"""
    __tablename__ = 'sessoes_estudo'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    baralho_id = db.Column(db.String(50), db.ForeignKey('baralhos.id'), nullable=False)
    tipo = db.Column(db.String(20), default='normal')  # normal, desafio, competicao
    acertos = db.Column(db.Integer, default=0)
    erros = db.Column(db.Integer, default=0)
    pontos_ganhos = db.Column(db.Integer, default=0)
    tempo_total = db.Column(db.Integer, default=0)  # em segundos
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    competicao_id = db.Column(db.String(50), db.ForeignKey('competicoes.id'))
    
    # Relacionamentos
    baralho = db.relationship('Baralho', backref='sessoes_estudo')
    competicao = db.relationship('Competicao', backref='sessoes_estudo')

class Badge(db.Model):
    """Modelo de badge"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    icone = db.Column(db.String(10), default='🏆')
    categoria = db.Column(db.String(20), default='geral')
    raridade = db.Column(db.String(20), default='comum')
    requisitos = db.Column(db.JSON)  # Armazena requisitos como JSON
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'icone': self.icone,
            'categoria': self.categoria,
            'raridade': self.raridade,
            'requisitos': self.requisitos or {}
        }

class UserBadge(db.Model):
    """Modelo de badge conquistado por usuário"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    data_conquista = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    badge = db.relationship('Badge', backref='conquistadores')
    
    # Garantir que não há duplicatas
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)

class Atividade(db.Model):
    """Modelo de atividade do feed"""
    __tablename__ = 'atividades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # criou_baralho, conquista, desafio, etc.
    descricao = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_extras = db.Column(db.JSON)  # Dados adicionais como JSON
    
    # Relacionamentos
    comentarios = db.relationship('Comentario', backref='atividade', lazy='dynamic', cascade='all, delete-orphan')
    curtidas = db.relationship('Curtida', backref='atividade', lazy='dynamic', cascade='all, delete-orphan')

class Comentario(db.Model):
    """Modelo de comentário"""
    __tablename__ = 'comentarios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('User', backref='comentarios')

class Curtida(db.Model):
    """Modelo de curtida"""
    __tablename__ = 'curtidas'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('User', backref='curtidas')
    
    # Garantir que não há duplicatas
    __table_args__ = (db.UniqueConstraint('user_id', 'atividade_id', name='unique_curtida'),)

class Notificacao(db.Model):
    """Modelo de notificação"""
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # amizade, competicao, badge, etc.
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_extras = db.Column(db.JSON)  # Dados adicionais como JSON

class ConviteBaralho(db.Model):
    """Modelo de convite para baralho"""
    __tablename__ = 'convites_baralho'
    
    id = db.Column(db.Integer, primary_key=True)
    baralho_id = db.Column(db.String(50), db.ForeignKey('baralhos.id'), nullable=False)
    user_from_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    user_to_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aceito, recusado
    data_convite = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime)
    
    # Relacionamentos
    baralho = db.relationship('Baralho', backref='convites')
    user_from = db.relationship('User', foreign_keys=[user_from_id], backref='convites_enviados')
    user_to = db.relationship('User', foreign_keys=[user_to_id], backref='convites_recebidos')

# Funções auxiliares para migração
def migrar_dados_json():
    """Migra dados dos arquivos JSON para o banco de dados"""
    from app import usuarios, baralhos, shared_decks, friend_requests, deck_invites
    
    print("🔄 Iniciando migração de dados...")
    
    # Migrar usuários
    for user_id, user_data in usuarios.items():
        user = User(
            id=user_id,
            nome=user_data.get('nome', ''),
            email=user_data.get('email', ''),
            senha=user_data.get('senha', ''),
            avatar=user_data.get('avatar', ''),
            points=user_data.get('points', 0),
            last_seen=datetime.fromtimestamp(user_data.get('last_seen', 0)) if user_data.get('last_seen') else datetime.utcnow(),
            data_criacao=datetime.fromtimestamp(user_data.get('data_criacao', 0)) if user_data.get('data_criacao') else datetime.utcnow(),
            data_nascimento=datetime.fromtimestamp(user_data.get('data_nascimento', 0)).date() if user_data.get('data_nascimento') else None,
            frase_pessoal=user_data.get('frase_pessoal', ''),
            tema=user_data.get('tema', 'dark'),
            ultimo_uso_ia=datetime.fromtimestamp(user_data.get('ultimo_uso_ia', 0)) if user_data.get('ultimo_uso_ia') else datetime.utcnow()
        )
        db.session.add(user)
    
    # Migrar baralhos
    for user_id, user_baralhos in baralhos.items():
        if isinstance(user_baralhos, dict):
            for deck_id, deck_data in user_baralhos.items():
                baralho = Baralho(
                    id=deck_id,
                    nome=deck_data.get('nome', ''),
                    cor=deck_data.get('cor', '#3b82f6'),
                    user_id=user_id,
                    data_criacao=datetime.utcnow()
                )
                db.session.add(baralho)
                
                # Migrar cards
                for card_data in deck_data.get('cards', []):
                    card = Card(
                        id=card_data.get('id', ''),
                        frente=card_data.get('frente', ''),
                        verso=card_data.get('verso', ''),
                        baralho_id=deck_id
                    )
                    db.session.add(card)
    
    # Migrar baralhos compartilhados
    for deck_id, deck_data in shared_decks.items():
        baralho = Baralho(
            id=deck_id,
            nome=deck_data.get('nome', ''),
            cor=deck_data.get('cor', '#3b82f6'),
            user_id=deck_data.get('owner', ''),
            data_criacao=datetime.fromtimestamp(deck_data.get('created_at', 0)) if deck_data.get('created_at') else datetime.utcnow(),
            is_shared=True
        )
        db.session.add(baralho)
        
        # Migrar membros
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
    
    # Migrar amizades
    for user_id, requests in friend_requests.items():
        for request_data in requests:
            amizade = Amizade(
                user1_id=request_data.get('from', ''),
                user2_id=user_id,
                status='pendente',
                data_solicitacao=datetime.fromtimestamp(request_data.get('timestamp', 0)) if request_data.get('timestamp') else datetime.utcnow()
            )
            db.session.add(amizade)
    
    # Migrar convites de baralho
    for user_id, invites in deck_invites.items():
        for invite_data in invites:
            convite = ConviteBaralho(
                baralho_id=invite_data.get('deck_id', ''),
                user_from_id=invite_data.get('from', ''),
                user_to_id=user_id,
                status='pendente',
                data_convite=datetime.fromtimestamp(invite_data.get('timestamp', 0)) if invite_data.get('timestamp') else datetime.utcnow()
            )
            db.session.add(convite)
    
    try:
        db.session.commit()
        print("✅ Migração concluída com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na migração: {e}")
        raise


