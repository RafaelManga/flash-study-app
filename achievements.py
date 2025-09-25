import time


ACHIEVEMENTS = {
    # Estudo e Criação
    'primeiro_card': {
        'name': '🧠 Primeiro Card',
        'desc': 'Criou seu primeiro flashcard',
        'category': 'Estudo',
        'difficulty': 'Fácil',
        'check': lambda s, ctx: s.get('cards_created', 0) >= 1,
    },
    'baralho_completo': {
        'name': '📦 Baralho Completo',
        'desc': 'Criou um baralho com 10+ cards',
        'category': 'Estudo',
        'difficulty': 'Médio',
        'check': lambda s, ctx: ctx.get('deck_cards_count', 0) >= 10,
    },
    'genio_ia': {
        'name': '💡 Gênio da IA',
        'desc': 'Gerou 10 cards com ajuda da IA',
        'category': 'Estudo',
        'difficulty': 'Médio',
        'check': lambda s, ctx: s.get('ia_cards_generated', 0) >= 10,
    },
    'revisador_profissional': {
        'name': '🔁 Revisador Profissional',
        'desc': 'Revisou o mesmo baralho 5 vezes',
        'category': 'Estudo',
        'difficulty': 'Médio',
        'check': lambda s, ctx: max(s.get('deck_review_counts', {}).values() or [0]) >= 5,
    },

    # Sociais
    'primeiro_amigo': {
        'name': '🤝 Primeiro Amigo',
        'desc': 'Adicionou seu primeiro amigo',
        'category': 'Social',
        'difficulty': 'Fácil',
        'check': lambda s, ctx: s.get('friends_added', 0) >= 1,
    },
    'mensageiro': {
        'name': '📨 Mensageiro',
        'desc': 'Enviou 10 mensagens privadas',
        'category': 'Social',
        'difficulty': 'Médio',
        'check': lambda s, ctx: s.get('messages_sent', 0) >= 10,
    },
    'primeiro_amigo_recusado3': {
        'name': '🧃 Amigo da Onça',
        'desc': 'Recusou 3 convites seguidos',
        'category': 'Social',
        'difficulty': 'Meme',
        'check': lambda s, ctx: s.get('invites_refused_streak', 0) >= 3,
    },

    # Competição
    'destruidor_de_baralhos': {
        'name': '🧨 Destruidor de Baralhos',
        'desc': 'Ganhou 5 desafios seguidos',
        'category': 'Competição',
        'difficulty': 'Difícil',
        'check': lambda s, ctx: s.get('challenges_won_streak', 0) >= 5,
    },
    'resposta_relampago': {
        'name': '⚡ Resposta Relâmpago',
        'desc': 'Respondeu em menos de 2 segundos',
        'category': 'Competição',
        'difficulty': 'Médio',
        'check': lambda s, ctx: s.get('fast_answers', 0) >= 1,
    },

    # Humor e Memes
    'card_shrek': {
        'name': '🐸 Card do Shrek',
        'desc': 'Criou um card com referência a meme',
        'category': 'Humor',
        'difficulty': 'Meme',
        'check': lambda s, ctx: s.get('meme_cards', 0) >= 1,
    },
    'madrugada': {
        'name': '🐱 Estudante de Madrugada',
        'desc': 'Usou o app entre 2h e 4h da manhã',
        'category': 'Humor',
        'difficulty': 'Meme',
        'check': lambda s, ctx: s.get('late_night_visits', 0) >= 1,
    },
    'congelado': {
        'name': '🧊 Congelado',
        'desc': 'Ficou 7 dias sem usar o app',
        'category': 'Humor',
        'difficulty': 'Meme',
        'check': lambda s, ctx: s.get('inactive_7_days', 0) >= 1,
    },
    'python_no_card': {
        'name': '🐍 Python no Card',
        'desc': 'Criou um card com código Python',
        'category': 'Humor',
        'difficulty': 'Meme',
        'check': lambda s, ctx: s.get('python_cards', 0) >= 1,
    },
}


def _ensure_user_struct(user):
    user.setdefault('badges', [])
    user.setdefault('conquistas', [])
    user.setdefault('stats', {})


def increment_stat(usuarios, salvar, user_id, key, amount=1):
    if user_id not in usuarios:
        return
    user = usuarios[user_id]
    _ensure_user_struct(user)
    stats = user['stats']
    stats[key] = stats.get(key, 0) + amount
    salvar()


def set_stat(usuarios, salvar, user_id, key, value):
    if user_id not in usuarios:
        return
    user = usuarios[user_id]
    _ensure_user_struct(user)
    user['stats'][key] = value
    salvar()


def award_if_eligible(usuarios, salvar, registrar_atividade, user_id, context=None):
    if user_id not in usuarios:
        return []
    user = usuarios[user_id]
    _ensure_user_struct(user)
    stats = user['stats']
    context = context or {}
    unlocked = []
    owned = set(user.get('conquistas', [])) | set(user.get('badges', []))
    for key, cfg in ACHIEVEMENTS.items():
        if cfg['name'] in owned:
            continue
        try:
            if cfg['check'](stats, context):
                user['conquistas'].append(cfg['name'])
                unlocked.append(cfg['name'])
                try:
                    registrar_atividade('conquista', user_id, f"Desbloqueou a conquista {cfg['name']} – {cfg['desc']}")
                except Exception:
                    pass
        except Exception:
            # ignora checagem com erro
            pass
    if unlocked:
        salvar()
    return unlocked


