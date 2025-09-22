#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Badges e Conquistas com Banco de Dados - FlashStudy
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import db, Badge, UserBadge, User, Baralho, SessaoEstudo, Competicao, Atividade

class SistemaBadgesDB:
    def __init__(self):
        pass
    
    def verificar_badges_usuario(self, user_id: str) -> List[Badge]:
        """Verifica quais badges o usuário pode conquistar baseado em suas estatísticas"""
        badges_conquistados = []
        
        # Obtém todos os badges disponíveis
        todos_badges = Badge.query.all()
        
        for badge in todos_badges:
            if self._verificar_requisitos_badge(badge, user_id):
                badges_conquistados.append(badge)
        
        return badges_conquistados
    
    def _verificar_requisitos_badge(self, badge: Badge, user_id: str) -> bool:
        """Verifica se o usuário atende aos requisitos de um badge específico"""
        # Verifica se já possui o badge
        if UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
            return False
        
        if not badge.requisitos:
            return True
        
        # Obtém estatísticas do usuário
        estatisticas = self._calcular_estatisticas_usuario(user_id)
        
        for requisito, valor_necessario in badge.requisitos.items():
            if requisito == "cards_criados":
                if estatisticas.get("total_cards", 0) < valor_necessario:
                    return False
            elif requisito == "sessoes_concluidas":
                if estatisticas.get("sessoes_estudo", 0) < valor_necessario:
                    return False
            elif requisito == "dias_consecutivos":
                if estatisticas.get("dias_estudo_consecutivos", 0) < valor_necessario:
                    return False
            elif requisito == "amigos":
                if estatisticas.get("total_amigos", 0) < valor_necessario:
                    return False
            elif requisito == "competicoes_ganhas":
                if estatisticas.get("competicoes_ganhas", 0) < valor_necessario:
                    return False
            elif requisito == "pontos":
                user = User.query.get(user_id)
                if not user or user.points < valor_necessario:
                    return False
            elif requisito == "baralhos_diferentes":
                if estatisticas.get("total_baralhos", 0) < valor_necessario:
                    return False
            elif requisito == "comentarios":
                if estatisticas.get("comentarios_feed", 0) < valor_necessario:
                    return False
            elif requisito == "dias_estudo":
                if estatisticas.get("dias_estudo_diferentes", 0) < valor_necessario:
                    return False
            elif requisito == "uso_ia":
                if estatisticas.get("uso_ia", 0) < valor_necessario:
                    return False
            elif requisito == "acertos_seguidos":
                if estatisticas.get("max_acertos_seguidos", 0) < valor_necessario:
                    return False
            elif requisito == "todos_badges":
                # Verifica se tem todos os outros badges (exceto este)
                total_badges = Badge.query.count() - 1
                badges_conquistados = UserBadge.query.filter_by(user_id=user_id).count()
                if badges_conquistados < total_badges:
                    return False
            elif requisito == "estudou_noite":
                if not estatisticas.get("estudou_noite", False):
                    return False
            elif requisito == "estudou_madrugada":
                if not estatisticas.get("estudou_madrugada", False):
                    return False
            elif requisito == "acerto_perfeito":
                if not estatisticas.get("acerto_perfeito", False):
                    return False
            elif requisito == "tempo_rapido":
                if not estatisticas.get("tempo_rapido", False):
                    return False
        
        return True
    
    def _calcular_estatisticas_usuario(self, user_id: str) -> Dict:
        """Calcula estatísticas do usuário para verificação de badges"""
        estatisticas = {
            "total_cards": 0,
            "total_baralhos": 0,
            "sessoes_estudo": 0,
            "dias_estudo_consecutivos": 0,
            "dias_estudo_diferentes": 0,
            "competicoes_ganhas": 0,
            "comentarios_feed": 0,
            "uso_ia": 0,
            "max_acertos_seguidos": 0,
            "estudou_noite": False,
            "estudou_madrugada": False,
            "acerto_perfeito": False,
            "tempo_rapido": False,
            "total_amigos": 0
        }
        
        # Conta cards e baralhos
        user = User.query.get(user_id)
        if not user:
            return estatisticas
        
        estatisticas["total_baralhos"] = user.baralhos.count()
        
        for baralho in user.baralhos:
            estatisticas["total_cards"] += baralho.cards.count()
        
        # Conta sessões de estudo
        estatisticas["sessoes_estudo"] = SessaoEstudo.query.filter_by(user_id=user_id).count()
        
        # Conta competições ganhas
        estatisticas["competicoes_ganhas"] = Competicao.query.filter_by(
            vencedor_id=user_id, 
            status='finalizada'
        ).count()
        
        # Conta amigos
        estatisticas["total_amigos"] = user.amizades_enviadas.filter_by(status='aceita').count() + \
                                     user.amizades_recebidas.filter_by(status='aceita').count()
        
        # Analisa atividades para estatísticas específicas
        atividades = Atividade.query.filter_by(user_id=user_id).all()
        for atividade in atividades:
            if atividade.tipo == "desafio_perfeito":
                estatisticas["acerto_perfeito"] = True
            elif atividade.tipo == "desafio_rapido":
                estatisticas["tempo_rapido"] = True
            elif atividade.tipo == "estudo_noite":
                estatisticas["estudou_noite"] = True
            elif atividade.tipo == "estudo_madrugada":
                estatisticas["estudou_madrugada"] = True
            elif atividade.tipo == "comentario":
                estatisticas["comentarios_feed"] += 1
            elif atividade.tipo == "geracao_ia":
                estatisticas["uso_ia"] += 1
        
        # Calcula dias de estudo consecutivos
        sessoes = SessaoEstudo.query.filter_by(user_id=user_id).order_by(SessaoEstudo.data_inicio.desc()).all()
        if sessoes:
            dias_consecutivos = 1
            data_anterior = sessoes[0].data_inicio.date()
            
            for sessao in sessoes[1:]:
                data_atual = sessao.data_inicio.date()
                if (data_anterior - data_atual).days == 1:
                    dias_consecutivos += 1
                    data_anterior = data_atual
                else:
                    break
            
            estatisticas["dias_estudo_consecutivos"] = dias_consecutivos
            
            # Conta dias diferentes
            dias_unicos = set(sessao.data_inicio.date() for sessao in sessoes)
            estatisticas["dias_estudo_diferentes"] = len(dias_unicos)
        
        return estatisticas
    
    def adicionar_badge_usuario(self, user_id: str, badge_id: int) -> bool:
        """Adiciona um badge ao usuário se ele ainda não o possui"""
        # Verifica se já possui o badge
        if UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first():
            return False
        
        # Adiciona o badge
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            data_conquista=datetime.utcnow()
        )
        
        try:
            db.session.add(user_badge)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar badge: {e}")
            return False
    
    def verificar_e_adicionar_badges(self, user_id: str) -> List[Badge]:
        """Verifica e adiciona novos badges para o usuário"""
        badges_conquistados = self.verificar_badges_usuario(user_id)
        novos_badges = []
        
        for badge in badges_conquistados:
            if self.adicionar_badge_usuario(user_id, badge.id):
                novos_badges.append(badge)
        
        return novos_badges
    
    def get_badges_usuario(self, user_id: str) -> List[Badge]:
        """Retorna todos os badges conquistados pelo usuário"""
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        return [user_badge.badge for user_badge in user_badges]
    
    def get_badges_por_categoria(self, categoria: str) -> List[Badge]:
        """Retorna todos os badges de uma categoria específica"""
        return Badge.query.filter_by(categoria=categoria).all()
    
    def get_badges_por_raridade(self, raridade: str) -> List[Badge]:
        """Retorna todos os badges de uma raridade específica"""
        return Badge.query.filter_by(raridade=raridade).all()
    
    def get_badge_info(self, badge_id: int) -> Optional[Badge]:
        """Retorna informações de um badge específico"""
        return Badge.query.get(badge_id)

# Instância global do sistema de badges
sistema_badges_db = SistemaBadgesDB()



