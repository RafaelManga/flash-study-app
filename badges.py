#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Badges e Conquistas - FlashStudy
"""

import time
from typing import Dict, List, Optional

class Badge:
    def __init__(self, id: int, nome: str, descricao: str, icone: str = "🏆", 
                 categoria: str = "geral", raridade: str = "comum", 
                 requisitos: Optional[Dict] = None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.icone = icone
        self.categoria = categoria
        self.raridade = raridade
        self.requisitos = requisitos or {}
        self.data_conquista = None

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "icone": self.icone,
            "categoria": self.categoria,
            "raridade": self.raridade,
            "data_conquista": self.data_conquista
        }

class SistemaBadges:
    def __init__(self):
        self.badges_disponiveis = self._criar_badges_padrao()
    
    def _criar_badges_padrao(self) -> Dict[int, Badge]:
        """Cria todos os badges disponíveis no sistema"""
        badges = {}
        
        # Badges de Criação
        badges[1] = Badge(1, "Primeiro Flashcard!", "Crie seu primeiro flashcard", "🎯", "criacao", "comum")
        badges[2] = Badge(2, "Criador de Baralhos", "Crie 5 flashcards", "📚", "criacao", "comum", {"cards_criados": 5})
        badges[3] = Badge(3, "Mestre dos Baralhos", "Crie 25 flashcards", "📖", "criacao", "raro", {"cards_criados": 25})
        badges[4] = Badge(4, "Lenda dos Cards", "Crie 100 flashcards", "👑", "criacao", "epico", {"cards_criados": 100})
        
        # Badges de Estudo
        badges[5] = Badge(5, "Estudioso", "Conclua 3 sessões de estudo", "📖", "estudo", "comum", {"sessoes_concluidas": 3})
        badges[6] = Badge(6, "Persistente", "Estude por 5 dias consecutivos", "🔥", "estudo", "raro", {"dias_consecutivos": 5})
        badges[7] = Badge(7, "Maratonista", "Estude por 30 dias consecutivos", "🏃‍♂️", "estudo", "epico", {"dias_consecutivos": 30})
        badges[8] = Badge(8, "Noite em Claro", "Estude após as 22h", "🌙", "estudo", "comum", {"estudou_noite": True})
        
        # Badges Sociais
        badges[9] = Badge(9, "Conectado", "Adicione seu primeiro amigo", "🤝", "social", "comum")
        badges[10] = Badge(10, "Popular", "Tenha 10 amigos", "👥", "social", "raro", {"amigos": 10})
        badges[11] = Badge(11, "Influenciador", "Tenha 50 amigos", "🌟", "social", "epico", {"amigos": 50})
        badges[12] = Badge(12, "Compartilhador", "Compartilhe seu primeiro baralho", "📤", "social", "comum")
        
        # Badges de Competição
        badges[13] = Badge(13, "Desafiante", "Participe do seu primeiro desafio", "⚔️", "competicao", "comum")
        badges[14] = Badge(14, "Competidor", "Entre em uma competição", "🏆", "competicao", "comum")
        badges[15] = Badge(15, "Vencedor", "Ganhe sua primeira competição", "🥇", "competicao", "raro")
        badges[16] = Badge(16, "Campeão", "Ganhe 10 competições", "👑", "competicao", "epico", {"competicoes_ganhas": 10})
        badges[17] = Badge(17, "Lenda das Competições", "Ganhe 50 competições", "🏆", "competicao", "lendario", {"competicoes_ganhas": 50})
        
        # Badges de Pontuação
        badges[18] = Badge(18, "Primeiros Pontos", "Ganhe seus primeiros 100 pontos", "💯", "pontuacao", "comum", {"pontos": 100})
        badges[19] = Badge(19, "Mil Pontos", "Ganhe 1000 pontos", "💎", "pontuacao", "raro", {"pontos": 1000})
        badges[20] = Badge(20, "Dez Mil Pontos", "Ganhe 10000 pontos", "💎💎", "pontuacao", "epico", {"pontos": 10000})
        
        # Badges Divertidos/Memes
        badges[21] = Badge(21, "Madrugador", "Estude antes das 6h", "🌅", "divertido", "comum", {"estudou_madrugada": True})
        badges[22] = Badge(22, "Viciado em IA", "Use a IA 10 vezes", "🤖", "divertido", "raro", {"uso_ia": 10})
        badges[23] = Badge(23, "Perfeccionista", "Acertou 100% em um desafio", "✨", "divertido", "raro", {"acerto_perfeito": True})
        badges[24] = Badge(24, "Velocista", "Complete um desafio em menos de 30 segundos", "⚡", "divertido", "raro", {"tempo_rapido": True})
        badges[25] = Badge(25, "Colecionador", "Tenha 10 baralhos diferentes", "📚", "divertido", "comum", {"baralhos_diferentes": 10})
        badges[26] = Badge(26, "Memorizador", "Acertou 50 respostas seguidas", "🧠", "divertido", "raro", {"acertos_seguidos": 50})
        badges[27] = Badge(27, "Explorador", "Estude em 7 dias diferentes", "🗺️", "divertido", "comum", {"dias_estudo": 7})
        badges[28] = Badge(28, "Mestre da IA", "Use a IA 50 vezes", "🤖👑", "divertido", "epico", {"uso_ia": 50})
        badges[29] = Badge(29, "Social Butterfly", "Comente em 20 atividades do feed", "🦋", "social", "raro", {"comentarios": 20})
        badges[30] = Badge(30, "Lenda Viva", "Complete todos os outros badges", "🏆👑", "especial", "lendario", {"todos_badges": True})
        
        return badges
    
    def verificar_badges_usuario(self, user_id: str, usuario: Dict, estatisticas: Dict) -> List[Badge]:
        """Verifica quais badges o usuário pode conquistar baseado em suas estatísticas"""
        badges_conquistados = []
        
        for badge_id, badge in self.badges_disponiveis.items():
            if self._verificar_requisitos_badge(badge, usuario, estatisticas):
                badges_conquistados.append(badge)
        
        return badges_conquistados
    
    def _verificar_requisitos_badge(self, badge: Badge, usuario: Dict, estatisticas: Dict) -> bool:
        """Verifica se o usuário atende aos requisitos de um badge específico"""
        if not badge.requisitos:
            return True
        
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
                if len(usuario.get("friends", [])) < valor_necessario:
                    return False
            elif requisito == "competicoes_ganhas":
                if estatisticas.get("competicoes_ganhas", 0) < valor_necessario:
                    return False
            elif requisito == "pontos":
                if usuario.get("points", 0) < valor_necessario:
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
                total_badges = len(self.badges_disponiveis) - 1
                if len(usuario.get("badges", [])) < total_badges:
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
    
    def calcular_estatisticas_usuario(self, user_id: str, usuario: Dict, baralhos: Dict, 
                                    atividades: List) -> Dict:
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
            "tempo_rapido": False
        }
        
        # Conta cards e baralhos
        user_baralhos = baralhos.get(user_id, {})
        estatisticas["total_baralhos"] = len(user_baralhos)
        
        for baralho in user_baralhos.values():
            if isinstance(baralho, dict) and "cards" in baralho:
                estatisticas["total_cards"] += len(baralho["cards"])
        
        # Analisa atividades para estatísticas de estudo
        for atividade in atividades:
            if atividade.get("usuario_id") == user_id:
                if atividade.get("tipo") == "estudo_concluido":
                    estatisticas["sessoes_estudo"] += 1
                elif atividade.get("tipo") == "desafio_perfeito":
                    estatisticas["acerto_perfeito"] = True
                elif atividade.get("tipo") == "desafio_rapido":
                    estatisticas["tempo_rapido"] = True
                elif atividade.get("tipo") == "estudo_noite":
                    estatisticas["estudou_noite"] = True
                elif atividade.get("tipo") == "estudo_madrugada":
                    estatisticas["estudou_madrugada"] = True
                elif atividade.get("tipo") == "comentario":
                    estatisticas["comentarios_feed"] += 1
                elif atividade.get("tipo") == "geracao_ia":
                    estatisticas["uso_ia"] += 1
        
        # Verifica competições ganhas
        competicoes = usuario.get("competicoes", [])
        for comp in competicoes:
            if comp.get("status") == "finalizada":
                if comp.get("vencedor") == user_id:
                    estatisticas["competicoes_ganhas"] += 1
        
        return estatisticas
    
    def adicionar_badge_usuario(self, user_id: str, badge_id: int, usuarios: Dict) -> bool:
        """Adiciona um badge ao usuário se ele ainda não o possui"""
        if user_id not in usuarios:
            return False
        
        if "badges" not in usuarios[user_id]:
            usuarios[user_id]["badges"] = []
        
        # Verifica se já possui o badge
        if badge_id in usuarios[user_id]["badges"]:
            return False
        
        # Adiciona o badge
        usuarios[user_id]["badges"].append(badge_id)
        
        # Adiciona data de conquista
        if "badges_data" not in usuarios[user_id]:
            usuarios[user_id]["badges_data"] = {}
        usuarios[user_id]["badges_data"][badge_id] = int(time.time())
        
        return True
    
    def get_badge_info(self, badge_id: int) -> Optional[Badge]:
        """Retorna informações de um badge específico"""
        return self.badges_disponiveis.get(badge_id)
    
    def get_badges_por_categoria(self, categoria: str) -> List[Badge]:
        """Retorna todos os badges de uma categoria específica"""
        return [badge for badge in self.badges_disponiveis.values() 
                if badge.categoria == categoria]
    
    def get_badges_por_raridade(self, raridade: str) -> List[Badge]:
        """Retorna todos os badges de uma raridade específica"""
        return [badge for badge in self.badges_disponiveis.values() 
                if badge.raridade == raridade]

# Instância global do sistema de badges
sistema_badges = SistemaBadges()


