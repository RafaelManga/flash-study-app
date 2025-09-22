#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Estatísticas - FlashStudy
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class EstatisticasUsuario:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.dados = {
            "total_cards": 0,
            "total_baralhos": 0,
            "sessoes_estudo": 0,
            "dias_estudo_consecutivos": 0,
            "dias_estudo_diferentes": set(),
            "competicoes_ganhas": 0,
            "competicoes_perdidas": 0,
            "comentarios_feed": 0,
            "uso_ia": 0,
            "max_acertos_seguidos": 0,
            "acertos_seguidos_atual": 0,
            "estudou_noite": False,
            "estudou_madrugada": False,
            "acerto_perfeito": False,
            "tempo_rapido": False,
            "ultimo_estudo": None,
            "dias_estudo_consecutivos_atual": 0,
            "pontos_ganhos_hoje": 0,
            "pontos_ganhos_semana": 0,
            "pontos_ganhos_mes": 0
        }
    
    def atualizar_estatisticas(self, tipo: str, dados: Dict = None):
        """Atualiza estatísticas baseado no tipo de atividade"""
        dados = dados or {}
        agora = int(time.time())
        
        if tipo == "card_criado":
            self.dados["total_cards"] += 1
        
        elif tipo == "baralho_criado":
            self.dados["total_baralhos"] += 1
        
        elif tipo == "sessao_estudo":
            self.dados["sessoes_estudo"] += 1
            self._atualizar_dias_estudo(agora)
            self._verificar_horario_estudo(agora)
        
        elif tipo == "desafio_concluido":
            acertos = dados.get("acertos", 0)
            total = dados.get("total", 1)
            pontos = dados.get("pontos", 0)
            
            # Atualiza acertos seguidos
            if acertos == total:
                self.dados["acertos_seguidos_atual"] += 1
                self.dados["max_acertos_seguidos"] = max(
                    self.dados["max_acertos_seguidos"], 
                    self.dados["acertos_seguidos_atual"]
                )
                self.dados["acerto_perfeito"] = True
            else:
                self.dados["acertos_seguidos_atual"] = 0
            
            # Verifica tempo rápido (menos de 30 segundos por questão)
            tempo_total = dados.get("tempo_total", 0)
            if tempo_total > 0 and (tempo_total / total) < 30:
                self.dados["tempo_rapido"] = True
            
            # Atualiza pontos
            self._atualizar_pontos(pontos)
        
        elif tipo == "competicao_ganha":
            self.dados["competicoes_ganhas"] += 1
        
        elif tipo == "competicao_perdida":
            self.dados["competicoes_perdidas"] += 1
        
        elif tipo == "comentario_feed":
            self.dados["comentarios_feed"] += 1
        
        elif tipo == "geracao_ia":
            self.dados["uso_ia"] += 1
        
        elif tipo == "amigo_adicionado":
            # Pode ser usado para badges sociais
            pass
        
        elif tipo == "baralho_compartilhado":
            # Pode ser usado para badges sociais
            pass
    
    def _atualizar_dias_estudo(self, timestamp: int):
        """Atualiza contadores de dias de estudo"""
        data_estudo = datetime.fromtimestamp(timestamp).date()
        self.dados["dias_estudo_diferentes"].add(data_estudo.isoformat())
        
        # Verifica se é consecutivo
        if self.dados["ultimo_estudo"]:
            ultima_data = datetime.fromtimestamp(self.dados["ultimo_estudo"]).date()
            if (data_estudo - ultima_data).days == 1:
                self.dados["dias_estudo_consecutivos_atual"] += 1
            elif (data_estudo - ultima_data).days > 1:
                self.dados["dias_estudo_consecutivos_atual"] = 1
        else:
            self.dados["dias_estudo_consecutivos_atual"] = 1
        
        self.dados["dias_estudo_consecutivos"] = max(
            self.dados["dias_estudo_consecutivos"],
            self.dados["dias_estudo_consecutivos_atual"]
        )
        
        self.dados["ultimo_estudo"] = timestamp
    
    def _verificar_horario_estudo(self, timestamp: int):
        """Verifica se o estudo foi feito em horários específicos"""
        hora = datetime.fromtimestamp(timestamp).hour
        
        if hora >= 22 or hora <= 6:  # Noite/madrugada
            self.dados["estudou_noite"] = True
        
        if hora <= 6:  # Madrugada
            self.dados["estudou_madrugada"] = True
    
    def _atualizar_pontos(self, pontos: int):
        """Atualiza contadores de pontos por período"""
        agora = int(time.time())
        hoje = datetime.fromtimestamp(agora).date()
        semana = hoje - timedelta(days=7)
        mes = hoje - timedelta(days=30)
        
        self.dados["pontos_ganhos_hoje"] += pontos
        self.dados["pontos_ganhos_semana"] += pontos
        self.dados["pontos_ganhos_mes"] += pontos
    
    def to_dict(self) -> Dict:
        """Converte para dicionário para serialização"""
        dados = self.dados.copy()
        dados["dias_estudo_diferentes"] = len(dados["dias_estudo_diferentes"])
        return dados

class GerenciadorEstatisticas:
    def __init__(self):
        self.estatisticas = {}  # user_id -> EstatisticasUsuario
    
    def get_estatisticas(self, user_id: str) -> EstatisticasUsuario:
        """Obtém ou cria estatísticas para um usuário"""
        if user_id not in self.estatisticas:
            self.estatisticas[user_id] = EstatisticasUsuario(user_id)
        return self.estatisticas[user_id]
    
    def registrar_atividade(self, user_id: str, tipo: str, dados: Dict = None):
        """Registra uma atividade e atualiza estatísticas"""
        stats = self.get_estatisticas(user_id)
        stats.atualizar_estatisticas(tipo, dados)
    
    def calcular_estatisticas_para_badges(self, user_id: str, usuario: Dict, 
                                        baralhos: Dict, atividades: List) -> Dict:
        """Calcula estatísticas necessárias para verificação de badges"""
        stats = self.get_estatisticas(user_id)
        
        # Atualiza dados básicos
        user_baralhos = baralhos.get(user_id, {})
        stats.dados["total_baralhos"] = len(user_baralhos)
        
        total_cards = 0
        for baralho in user_baralhos.values():
            if isinstance(baralho, dict) and "cards" in baralho:
                total_cards += len(baralho["cards"])
        stats.dados["total_cards"] = total_cards
        
        # Analisa atividades para estatísticas específicas
        for atividade in atividades:
            if atividade.get("usuario_id") == user_id:
                tipo = atividade.get("tipo", "")
                if tipo == "estudo_concluido":
                    stats.dados["sessoes_estudo"] += 1
                elif tipo == "desafio_perfeito":
                    stats.dados["acerto_perfeito"] = True
                elif tipo == "desafio_rapido":
                    stats.dados["tempo_rapido"] = True
                elif tipo == "estudo_noite":
                    stats.dados["estudou_noite"] = True
                elif tipo == "estudo_madrugada":
                    stats.dados["estudou_madrugada"] = True
                elif tipo == "comentario":
                    stats.dados["comentarios_feed"] += 1
                elif tipo == "geracao_ia":
                    stats.dados["uso_ia"] += 1
        
        # Verifica competições ganhas
        competicoes = usuario.get("competicoes", [])
        for comp in competicoes:
            if comp.get("status") == "finalizada":
                if comp.get("vencedor") == user_id:
                    stats.dados["competicoes_ganhas"] += 1
        
        return stats.to_dict()
    
    def reset_estatisticas_diarias(self):
        """Reseta estatísticas diárias (chamado diariamente)"""
        for stats in self.estatisticas.values():
            stats.dados["pontos_ganhos_hoje"] = 0
    
    def reset_estatisticas_semanais(self):
        """Reseta estatísticas semanais (chamado semanalmente)"""
        for stats in self.estatisticas.values():
            stats.dados["pontos_ganhos_semana"] = 0
    
    def reset_estatisticas_mensais(self):
        """Reseta estatísticas mensais (chamado mensalmente)"""
        for stats in self.estatisticas.values():
            stats.dados["pontos_ganhos_mes"] = 0

# Instância global do gerenciador de estatísticas
gerenciador_estatisticas = GerenciadorEstatisticas()


