from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
import time
from models import Atividade, Comentario


from flask import current_app
feed_bp = Blueprint('feed', __name__)

# Garante registro do filtro Jinja2 'datetime' no contexto do blueprint
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    from datetime import datetime
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format)
try:
    current_app.jinja_env.filters['datetime'] = datetime_filter
except Exception:
    pass

# Simulação de armazenamento (substituir por banco/arquivo)
atividades = []

@feed_bp.route('/feed')
def feed():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Exibe atividades dos amigos e do próprio usuário
    amigos = []
    try:
        from app import usuarios
        if user_id in usuarios:
            amigos = usuarios[user_id].get('friends', [])
    except ImportError:
        pass
    
    atividades_exibir = [a for a in atividades if a.usuario_id == user_id or a.usuario_id in amigos]
    atividades_exibir.sort(key=lambda x: x.data, reverse=True)
    return render_template('feed.html', atividades=[a.to_dict() for a in atividades_exibir])

@feed_bp.route('/feed/comentar', methods=['POST'])
def comentar_feed():
    user_id = session.get('user_id')
    atividade_idx = int(request.json.get('atividade_idx'))
    texto = request.json.get('texto')
    if user_id and texto and 0 <= atividade_idx < len(atividades):
        comentario = Comentario(user_id, texto)
        atividades[atividade_idx].comentarios.append(comentario.to_dict())
        return jsonify({'msg': 'Comentário adicionado!'})
    return jsonify({'msg': 'Erro ao comentar.'}), 400

@feed_bp.route('/feed/curtir', methods=['POST'])
def curtir_feed():
    user_id = session.get('user_id')
    atividade_idx = int(request.json.get('atividade_idx'))
    if user_id and 0 <= atividade_idx < len(atividades):
        if user_id not in atividades[atividade_idx].likes:
            atividades[atividade_idx].likes.append(user_id)
        return jsonify({'msg': 'Curtido!'})
    return jsonify({'msg': 'Erro ao curtir.'}), 400

# Função para registrar atividade

def registrar_atividade(tipo, usuario_id, descricao):
    atividades.append(Atividade(tipo, usuario_id, descricao))

# Exemplo de uso: registrar_atividade('criou_baralho', 'USR123', 'Criou o baralho Matemática')
