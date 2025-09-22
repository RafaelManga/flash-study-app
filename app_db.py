#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashStudy - Plataforma de Flashcards com IA e Banco de Dados
Versão: 3.0
Autor: FlashStudy Team
"""

import os
import json
import time
import random
import string
from datetime import datetime, timedelta
from uuid import uuid4
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import google.generativeai as genai

# Importar configuração do banco de dados
from database import db, init_db, User, Baralho, Card, Amizade, Competicao, SessaoEstudo, Atividade, Notificacao, ConviteBaralho, BaralhoMembro
from badges_db import sistema_badges_db

# --- Configuração da Aplicação ---
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "flashstudy_secret_key_2024")
bcrypt = Bcrypt(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Filtro Jinja2 para formatar datas
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format)
app.jinja_env.filters['datetime'] = datetime_filter

# --- Configuração da IA (Google Gemini) ---
gemini_key = os.environ.get("GEMINI_API_KEY", "SUA_CHAVE_GEMINI_AQUI")

if gemini_key == "SUA_CHAVE_GEMINI_AQUI":
    print("⚠️  GEMINI_API_KEY: usando chave padrão - configure a variável de ambiente para produção")

# Definição global da variável model
model = None
try:
    genai.configure(api_key=gemini_key)
    print("✅ Gemini API configurada com sucesso")
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    print(f"❌ Erro ao configurar Gemini API: {e}")

# Import e registro do blueprint do feed social
from feed import feed_bp
app.register_blueprint(feed_bp)

# Inicializar banco de dados
init_db(app)

# --- Constantes e Caminhos ---
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# --- Criação de Pastas ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Funções Auxiliares ---
def gerar_id_usuario(prefix="USR", length=7):
    return f"{prefix}{''.join(random.choices(string.ascii_uppercase + string.digits, k=length))}"

def agora_timestamp():
    return int(time.time())

def data_formatada(timestamp):
    if not timestamp:
        return "Data não disponível"
    try:
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")
    except:
        return "Data inválida"

def usuario_online(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    last_seen = user.last_seen
    return (datetime.utcnow() - last_seen).total_seconds() < 300  # 5 minutos

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def pode_usar_ia(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    ultimo_uso = user.ultimo_uso_ia
    return (datetime.utcnow() - ultimo_uso).total_seconds() >= 120  # 2 minutos

def tempo_restante_ia(user_id):
    user = User.query.get(user_id)
    if not user:
        return 0
    ultimo_uso = user.ultimo_uso_ia
    tempo_passado = (datetime.utcnow() - ultimo_uso).total_seconds()
    return max(0, 120 - tempo_passado)  # 2 minutos

def contar_notificacoes(user_id):
    """Conta total de notificações pendentes"""
    return Notificacao.query.filter_by(user_id=user_id, lida=False).count()

# --- Decorador de Login ---
def login_required_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Você precisa fazer login para acessar esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processor ---
@app.context_processor
def inject_user():
    user_data = None
    notificacoes = 0
    if current_user.is_authenticated:
        user_data = current_user.to_dict()
        notificacoes = contar_notificacoes(current_user.id)
    
    return {
        "usuario": user_data,
        "notificacoes_count": notificacoes,
        "data_formatada": data_formatada,
        "usuario_online": usuario_online
    }

# --- Rotas de Competição entre Amigos ---
@app.route('/competicao/desafios')
@login_required_db
def desafios_pendentes():
    competicoes = Competicao.query.filter_by(
        user2_id=current_user.id, 
        status='pendente'
    ).all()
    
    desafios = []
    for comp in competicoes:
        user1 = User.query.get(comp.user1_id)
        baralho = Baralho.query.get(comp.baralho_id)
        if user1 and baralho:
            desafios.append({
                "id": comp.id,
                "de": user1.nome,
                "baralho": baralho.nome
            })
    
    return jsonify({"desafios": desafios})

@app.route('/competicao/recusar', methods=['POST'])
@login_required_db
def recusar_competicao():
    data = request.json
    comp_id = data.get('comp_id')
    
    comp = Competicao.query.filter_by(
        id=comp_id, 
        user2_id=current_user.id
    ).first()
    
    if comp:
        comp.status = 'recusada'
        comp.data_resposta = datetime.utcnow()
        db.session.commit()
        return jsonify({"msg": "Desafio recusado!"})
    
    return jsonify({"msg": "Desafio não encontrado."}), 404

@app.route('/competicao/convidar', methods=['POST'])
@login_required_db
def convidar_competicao():
    data = request.json
    user2_id = data.get('user2')
    deck_ids = data.get('deck_ids', [])
    criados = []
    
    if User.query.get(user2_id):
        for deck_id in deck_ids:
            # Verifica se o baralho pertence ao usuário
            baralho = Baralho.query.filter_by(id=deck_id, user_id=current_user.id).first()
            if baralho:
                comp_id = f"comp_{int(time.time())}_{current_user.id}_{user2_id}_{deck_id}"
                comp = Competicao(
                    id=comp_id,
                    user1_id=current_user.id,
                    user2_id=user2_id,
                    baralho_id=deck_id,
                    status='pendente'
                )
                db.session.add(comp)
                criados.append(comp.to_dict())
        
        db.session.commit()
    
    return jsonify({"msg": f"{len(criados)} desafio(s) enviado(s)!", "competicoes": criados})

@app.route('/competicao/aceitar', methods=['POST'])
@login_required_db
def aceitar_competicao():
    data = request.json
    comp_id = data.get('comp_id')
    
    comp = Competicao.query.filter_by(
        id=comp_id, 
        user2_id=current_user.id
    ).first()
    
    if comp:
        comp.status = 'aceita'
        comp.data_aceitacao = datetime.utcnow()
        db.session.commit()
        
        # Verifica badges
        novos_badges = sistema_badges_db.verificar_e_adicionar_badges(current_user.id)
        
        # Registra atividade
        atividade = Atividade(
            user_id=current_user.id,
            tipo='desafio_aceito',
            descricao='Aceitou um desafio!'
        )
        db.session.add(atividade)
        db.session.commit()
        
        return jsonify({
            "msg": "Competição aceita!", 
            "comp_id": comp_id,
            "novos_badges": [badge.to_dict() for badge in novos_badges]
        })
    
    return jsonify({"msg": "Desafio não encontrado."}), 404

@app.route('/competicao/ranking', methods=['GET'])
@login_required_db
def ranking_competicao():
    # Obtém amigos do usuário
    amigos_ids = []
    for amizade in current_user.amizades_enviadas.filter_by(status='aceita').all():
        amigos_ids.append(amizade.user2_id)
    for amizade in current_user.amizades_recebidas.filter_by(status='aceita').all():
        amigos_ids.append(amizade.user1_id)
    
    # Inclui o próprio usuário no ranking
    participantes_ids = [current_user.id] + amigos_ids
    
    ranking = []
    for user_id in participantes_ids:
        user = User.query.get(user_id)
        if user:
            # Calcula pontos totais (pontos + bônus de competições)
            pontos_base = user.points
            competicoes_ganhas = Competicao.query.filter_by(
                vencedor_id=user_id, 
                status='finalizada'
            ).count()
            pontos_bonus = competicoes_ganhas * 50  # 50 pontos por competição ganha
            pontos_totais = pontos_base + pontos_bonus
            
            ranking.append({
                "id": user_id,
                "nome": user.nome,
                "pontos": pontos_totais,
                "competicoes_ganhas": competicoes_ganhas,
                "badges": user.badges_conquistados.count()
            })
    
    # Ordena por pontos (maior primeiro)
    ranking.sort(key=lambda x: x["pontos"], reverse=True)
    
    return jsonify({"ranking": ranking})

# --- Página de Competição ---
@app.route("/competicao")
@login_required_db
def pagina_competicao():
    # Buscar amigos do usuário logado
    amigos = []
    for amizade in current_user.amizades_enviadas.filter_by(status='aceita').all():
        amigo = User.query.get(amizade.user2_id)
        if amigo:
            amigos.append({
                "id": amigo.id,
                "nome": amigo.nome
            })
    for amizade in current_user.amizades_recebidas.filter_by(status='aceita').all():
        amigo = User.query.get(amizade.user1_id)
        if amigo:
            amigos.append({
                "id": amigo.id,
                "nome": amigo.nome
            })
    
    # Lista de baralhos do usuário
    user_baralhos = []
    for baralho in current_user.baralhos:
        user_baralhos.append({
            "id": baralho.id,
            "nome": baralho.nome
        })
    
    return render_template("competicao.html", 
                         usuario=current_user.to_dict(), 
                         amigos=amigos, 
                         baralhos=user_baralhos)

# --- Autenticação ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]
        
        if not email or not senha:
            flash("Email e senha são obrigatórios.", "warning")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(senha):
            login_user(user)
            user.last_seen = datetime.utcnow()
            db.session.commit()
            flash(f"Bem-vindo de volta, {user.nome}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Email ou senha incorretos. Verifique suas credenciais.", "danger")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]
        data_nascimento = request.form.get("data_nascimento", "").strip()
        
        if not nome or not email or not senha:
            flash("Nome, email e senha são obrigatórios.", "warning")
            return render_template("register.html")
        
        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "warning")
            return render_template("register.html")
        
        # Verifica se email já existe
        if User.query.filter_by(email=email).first():
            flash("Este email já está cadastrado. Tente fazer login ou use outro email.", "danger")
            return render_template("register.html")
        
        # Cria novo usuário
        user_id = gerar_id_usuario()
        user = User(
            id=user_id,
            nome=nome,
            email=email,
            data_nascimento=datetime.strptime(data_nascimento, "%Y-%m-%d").date() if data_nascimento else None
        )
        user.set_password(senha)
        
        db.session.add(user)
        db.session.commit()
        
        flash("Conta criada com sucesso! Agora você pode fazer login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/logout")
@login_required_db
def logout():
    logout_user()
    flash("Você saiu da sua conta com sucesso.", "success")
    return redirect(url_for("login"))

# --- Rotas Principais ---
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/home")
@login_required_db
def home():
    user_baralhos = current_user.baralhos.all()
    
    # Baralhos compartilhados onde o usuário tem acesso
    baralhos_compartilhados = Baralho.query.join(BaralhoMembro).filter(
        BaralhoMembro.user_id == current_user.id
    ).all()
    
    return render_template("index.html",
                         baralhos=[baralho.to_dict() for baralho in user_baralhos],
                         baralhos_compartilhados=[baralho.to_dict() for baralho in baralhos_compartilhados])

# --- Sistema de Amizade ---
@app.route("/amigos")
@login_required_db
def amigos():
    # Buscar informações dos amigos
    amigos_info = []
    for amizade in current_user.amizades_enviadas.filter_by(status='aceita').all():
        amigo = User.query.get(amizade.user2_id)
        if amigo:
            amigos_info.append({
                "id": amigo.id,
                "nome": amigo.nome,
                "avatar": amigo.avatar,
                "online": usuario_online(amigo.id),
                "points": amigo.points
            })
    for amizade in current_user.amizades_recebidas.filter_by(status='aceita').all():
        amigo = User.query.get(amizade.user1_id)
        if amigo:
            amigos_info.append({
                "id": amigo.id,
                "nome": amigo.nome,
                "avatar": amigo.avatar,
                "online": usuario_online(amigo.id),
                "points": amigo.points
            })
    
    # Pedidos de amizade recebidos
    pedidos_recebidos = []
    for amizade in current_user.amizades_recebidas.filter_by(status='pendente').all():
        sender = User.query.get(amizade.user1_id)
        if sender:
            pedidos_recebidos.append({
                "id": sender.id,
                "nome": sender.nome,
                "avatar": sender.avatar,
                "timestamp": amizade.data_solicitacao.timestamp()
            })
    
    # Convites para baralhos recebidos
    convites_recebidos = []
    for convite in current_user.convites_recebidos.filter_by(status='pendente').all():
        sender = User.query.get(convite.user_from_id)
        baralho = Baralho.query.get(convite.baralho_id)
        if sender and baralho:
            convites_recebidos.append({
                "id": convite.baralho_id,
                "from_id": convite.user_from_id,
                "from_nome": sender.nome,
                "deck_nome": baralho.nome,
                "timestamp": convite.data_convite.timestamp()
            })
    
    return render_template("amigos.html",
                         amigos=amigos_info,
                         pedidos_recebidos=pedidos_recebidos,
                         convites_recebidos=convites_recebidos)

@app.route("/enviar_pedido_amizade", methods=["POST"])
@login_required_db
def enviar_pedido_amizade():
    friend_id = request.form.get("friend_id", "").strip().upper()
    
    if not friend_id:
        flash("ID do amigo não pode ser vazio.", "warning")
        return redirect(url_for("amigos"))
    
    if friend_id == current_user.id:
        flash("Você não pode adicionar a si mesmo como amigo.", "warning")
        return redirect(url_for("amigos"))
    
    friend = User.query.get(friend_id)
    if not friend:
        flash("Usuário não encontrado. Verifique se o ID está correto.", "danger")
        return redirect(url_for("amigos"))
    
    # Verifica se já são amigos
    existing_amizade = Amizade.query.filter(
        ((Amizade.user1_id == current_user.id) & (Amizade.user2_id == friend_id)) |
        ((Amizade.user1_id == friend_id) & (Amizade.user2_id == current_user.id))
    ).first()
    
    if existing_amizade:
        if existing_amizade.status == 'aceita':
            flash("Este usuário já é seu amigo.", "info")
        else:
            flash("Já existe um pedido de amizade pendente com este usuário.", "info")
        return redirect(url_for("amigos"))
    
    # Cria pedido de amizade
    amizade = Amizade(
        user1_id=current_user.id,
        user2_id=friend_id,
        status='pendente'
    )
    
    db.session.add(amizade)
    db.session.commit()
    
    flash(f"Pedido de amizade enviado para {friend.nome}!", "success")
    return redirect(url_for("amigos"))

@app.route("/aceitar_amizade/<friend_id>", methods=["POST"])
@login_required_db
def aceitar_amizade(friend_id):
    amizade = Amizade.query.filter_by(
        user1_id=friend_id,
        user2_id=current_user.id,
        status='pendente'
    ).first()
    
    if amizade:
        amizade.status = 'aceita'
        amizade.data_resposta = datetime.utcnow()
        db.session.commit()
        
        # Verifica badges
        novos_badges = sistema_badges_db.verificar_e_adicionar_badges(current_user.id)
        
        friend = User.query.get(friend_id)
        if novos_badges:
            flash(f"Agora você e {friend.nome} são amigos! 🎉 Conquistou {len(novos_badges)} novo(s) badge(s)!", "success")
        else:
            flash(f"Agora você e {friend.nome} são amigos!", "success")
    else:
        flash("Pedido de amizade não encontrado.", "danger")
    
    return redirect(url_for("amigos"))

@app.route("/recusar_amizade/<friend_id>", methods=["POST"])
@login_required_db
def recusar_amizade(friend_id):
    amizade = Amizade.query.filter_by(
        user1_id=friend_id,
        user2_id=current_user.id,
        status='pendente'
    ).first()
    
    if amizade:
        amizade.status = 'recusada'
        amizade.data_resposta = datetime.utcnow()
        db.session.commit()
        flash("Pedido de amizade recusado.", "info")
    else:
        flash("Pedido de amizade não encontrado.", "danger")
    
    return redirect(url_for("amigos"))

@app.route("/remover_amigo/<friend_id>", methods=["POST"])
@login_required_db
def remover_amigo(friend_id):
    # Remove amizade mutuamente
    amizade = Amizade.query.filter(
        ((Amizade.user1_id == current_user.id) & (Amizade.user2_id == friend_id)) |
        ((Amizade.user1_id == friend_id) & (Amizade.user2_id == current_user.id))
    ).first()
    
    if amizade:
        db.session.delete(amizade)
        db.session.commit()
        flash("Amigo removido da sua lista.", "success")
    else:
        flash("Amizade não encontrada.", "danger")
    
    return redirect(url_for("amigos"))

# --- Rota para exibir badges ---
@app.route("/badges")
@login_required_db
def badges():
    # Obtém badges do usuário
    badges_usuario = sistema_badges_db.get_badges_usuario(current_user.id)
    
    # Obtém todos os badges disponíveis para mostrar progresso
    todos_badges = Badge.query.all()
    
    # Marca quais badges foram conquistados
    badges_conquistados_ids = {badge.id for badge in badges_usuario}
    for badge in todos_badges:
        badge.conquistado = badge.id in badges_conquistados_ids
    
    # Agrupa por categoria
    badges_por_categoria = {}
    for badge in todos_badges:
        categoria = badge.categoria
        if categoria not in badges_por_categoria:
            badges_por_categoria[categoria] = []
        badges_por_categoria[categoria].append(badge)
    
    return render_template("badges.html", 
                         badges_usuario=[badge.to_dict() for badge in badges_usuario],
                         badges_por_categoria=badges_por_categoria,
                         total_badges=len(todos_badges),
                         badges_conquistados=len(badges_usuario))

# --- Rota de Heartbeat ---
@app.route("/heartbeat", methods=["POST"])
@login_required_db
def heartbeat():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ok"})

# --- Execução ---
if __name__ == "__main__":
    print("🚀 FlashStudy iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)



