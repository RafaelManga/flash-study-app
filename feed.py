from flask import Blueprint, render_template, request, session, jsonify
import time
import os
import json
from models import Atividade, Comentario


from flask import current_app
feed_bp = Blueprint('feed', __name__)

# Garante registro do filtro Jinja2 'datetime' no contexto do blueprint
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    from datetime import datetime
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime(format)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).strftime(format)
            except Exception:
                pass
        return value.strftime(format)
    except Exception:
        try:
            return str(value)
        except Exception:
            return ''
try:
    current_app.jinja_env.filters['datetime'] = datetime_filter
except Exception:
    pass

# Persistência simples em arquivos JSON
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FEED_PATH = os.path.join(DATA_DIR, 'feed.json')
DM_PATH = os.path.join(DATA_DIR, 'messages.json')

os.makedirs(DATA_DIR, exist_ok=True)

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Carrega atividades em memória
atividades = []
_feed_data = _load_json(FEED_PATH, [])
for item in _feed_data:
    atividades.append(
        Atividade(
            item.get('tipo'),
            item.get('usuario_id'),
            item.get('descricao'),
            data=item.get('data'),
            likes=item.get('likes', []),
            comentarios=item.get('comentarios', []),
        )
    )

@feed_bp.route('/feed')
def feed():
    user_id = session.get('user_id')
    # Exibe atividades dos amigos e do próprio usuário
    amigos = []
    if user_id and 'usuarios' in globals():
        amigos = globals()['usuarios'][user_id].get('friends', [])
    atividades_exibir = [a for a in atividades if a.usuario_id == user_id or a.usuario_id in amigos]
    atividades_exibir.sort(key=lambda x: x.data, reverse=True)
    amigos_info = []
    if 'usuarios' in globals():
        for fid in amigos:
            nome = globals()['usuarios'].get(fid, {}).get('nome', fid)
            amigos_info.append({'id': fid, 'nome': nome})
    # Enriquecer atividades com nomes e ícone por tipo
    atividades_dicts = []
    get_nome = (lambda uid: globals()['usuarios'].get(uid, {}).get('nome', uid)) if 'usuarios' in globals() else (lambda x: x)
    tipo_icone = {
        'criou_baralho': '📚',
        'conquista': '🏅',
        'desafio': '🎯',
        'mensagem': '✉️',
        'resultado': '🏆'
    }
    for a in atividades_exibir:
        d = a.to_dict()
        d['usuario_nome'] = get_nome(d['usuario_id'])
        d['icone'] = tipo_icone.get(d['tipo'], '📰')
        atividades_dicts.append(d)
    return render_template('feed.html', atividades=atividades_dicts, amigos=amigos_info)

@feed_bp.route('/feed/list')
def feed_list():
    """Retorna atividades recentes do usuário e amigos (para polling)."""
    user_id = session.get('user_id')
    amigos = []
    if user_id and 'usuarios' in globals():
        amigos = globals()['usuarios'][user_id].get('friends', [])
    atividades_exibir = [a for a in atividades if a.usuario_id == user_id or a.usuario_id in amigos]
    atividades_exibir.sort(key=lambda x: x.data, reverse=True)
    since = float(request.args.get('since', 0) or 0)
    if since:
        atividades_exibir = [a for a in atividades_exibir if a.data > since]
    return jsonify({
        'atividades': [a.to_dict() for a in atividades_exibir],
        'now': time.time()
    })

@feed_bp.route('/feed/comentar', methods=['POST'])
def comentar_feed():
    user_id = session.get('user_id')
    atividade_idx = int(request.json.get('atividade_idx'))
    texto = request.json.get('texto')
    if user_id and texto and 0 <= atividade_idx < len(atividades):
        comentario = Comentario(user_id, texto)
        atividades[atividade_idx].comentarios.append(comentario.to_dict())
        _save_json(FEED_PATH, [a.to_dict() for a in atividades])
        return jsonify({'msg': 'Comentário adicionado!'})
    return jsonify({'msg': 'Erro ao comentar.'}), 400

@feed_bp.route('/feed/curtir', methods=['POST'])
def curtir_feed():
    user_id = session.get('user_id')
    atividade_idx = int(request.json.get('atividade_idx'))
    if user_id and 0 <= atividade_idx < len(atividades):
        if user_id not in atividades[atividade_idx].likes:
            atividades[atividade_idx].likes.append(user_id)
            _save_json(FEED_PATH, [a.to_dict() for a in atividades])
        return jsonify({'msg': 'Curtido!'})
    return jsonify({'msg': 'Erro ao curtir.'}), 400

# Função para registrar atividade

def registrar_atividade(tipo, usuario_id, descricao):
    atividades.append(Atividade(tipo, usuario_id, descricao))
    # Mantém tamanho razoável do feed (opcional)
    if len(atividades) > 500:
        del atividades[:100]
    _save_json(FEED_PATH, [a.to_dict() for a in atividades])


# --- Mensagens Diretas (DM) ---

def _conv_key(u1, u2):
    return '::'.join(sorted([u1, u2]))

@feed_bp.route('/feed/dm/list')
def dm_list():
    user_id = session.get('user_id')
    friend_id = request.args.get('friend_id')
    if not user_id or not friend_id:
        return jsonify({'msgs': []})
    store = _load_json(DM_PATH, {})
    conv = store.get(_conv_key(user_id, friend_id), [])
    return jsonify({'msgs': conv})

@feed_bp.route('/feed/dm/send', methods=['POST'])
def dm_send():
    user_id = session.get('user_id')
    data = request.get_json(silent=True) or {}
    friend_id = data.get('friend_id')
    texto = data.get('texto', '').strip()
    if not user_id or not friend_id or not texto:
        return jsonify({'msg': 'Dados inválidos.'}), 400
    store = _load_json(DM_PATH, {})
    key = _conv_key(user_id, friend_id)
    store.setdefault(key, []).append({
        'from': user_id,
        'to': friend_id,
        'texto': texto,
        'ts': time.time()
    })
    _save_json(DM_PATH, store)
    try:
        registrar_atividade('mensagem', user_id, f'Enviou uma mensagem para {friend_id}')
        # Stats para conquistas
        try:
            from achievements import increment_stat, award_if_eligible
            from app import usuarios, salvar_dados, USERS_PATH
            increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), user_id, 'messages_sent', 1)
            award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, user_id)
        except Exception:
            pass
    except Exception:
        pass
    return jsonify({'msg': 'Enviado!'})


# --- Consulta auxiliar para páginas ---
def atividades_do_usuario(user_id):
    """Retorna atividades (dict) de um usuário específico, mais recentes primeiro."""
    itens = [a.to_dict() for a in atividades if a.usuario_id == user_id]
    itens.sort(key=lambda x: x.get('data', 0), reverse=True)
    return itens

# Exemplo de uso: registrar_atividade('criou_baralho', 'USR123', 'Criou o baralho Matemática')
