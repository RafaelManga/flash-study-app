#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashStudy - Plataforma de Flashcards com IA
Versão: 2.0
Autor: FlashStudy Team
"""

import os
import json
import time
import random
import string
from datetime import datetime
from uuid import uuid4
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_bcrypt import Bcrypt
import google.generativeai as genai

# --- Configuração da Aplicação ---
app = Flask(__name__)

# Filtro Jinja2 para formatar datas
from datetime import datetime
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    try:
        # Aceita timestamps numéricos (epoch)
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value)
            return dt.strftime(format)
        # Aceita strings ISO
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return dt.strftime(format)
            except Exception:
                pass
        # Objetos datetime ou similares
        return value.strftime(format)
    except Exception:
        # Fallback seguro
        try:
            return str(value)
        except Exception:
            return ''
app.jinja_env.filters['datetime'] = datetime_filter

def ensure_user_defaults(user: dict):
    if not isinstance(user, dict):
        return user
    user.setdefault('badges', [])
    user.setdefault('conquistas', [])
    user.setdefault('stats', {})
    return user

# Importações necessárias (apenas uma vez, no topo do arquivo)
from feed import feed_bp
from achievements import increment_stat, award_if_eligible, ACHIEVEMENTS

ACHIEVEMENTS_MAP = { cfg['name']: { 'desc': cfg['desc'], 'category': cfg['category'], 'difficulty': cfg['difficulty'] } for cfg in ACHIEVEMENTS.values() }
app.secret_key = os.environ.get("SECRET_KEY", "flashstudy_secret_key_2024")
bcrypt = Bcrypt(app)
app.register_blueprint(feed_bp)

def adicionar_conquista(user_id, conquista):
    if user_id in usuarios:
        user = usuarios[user_id]
        if "conquistas" not in user:
            user["conquistas"] = []
        if conquista not in user["conquistas"]:
            user["conquistas"].append(conquista)
            salvar_dados(USERS_PATH, usuarios)

def adicionar_badge(user_id, badge):
    if user_id in usuarios:
        user = usuarios[user_id]
        if "badges" not in user:
            user["badges"] = []
        if badge not in user["badges"]:
            user["badges"].append(badge)
            salvar_dados(USERS_PATH, usuarios)
# --- Rotas de competição (após definição do app e dados) ---
# ...existing code...


# --- Configuração da IA (Google Gemini) ---
gemini_key = os.environ.get("GEMINI_API_KEY", "SUA_CHAVE_GEMINI_AQUI")

if gemini_key == "SUA_CHAVE_GEMINI_AQUI":
    print("⚠️  GEMINI_API_KEY: usando chave padrão - configure a variável de ambiente para produção")

def salvar_dados(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# Definição global da variável model
model = None
try:
    genai.configure(api_key=gemini_key)
    print("✅ Gemini API configurada com sucesso")
    # Se a configuração for bem-sucedida, inicialize o modelo
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    print(f"❌ Erro ao configurar Gemini API: {e}")

DATA_DIR = "data"
# --- Constantes e Caminhos ---
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

USERS_PATH = os.path.join(DATA_DIR, "users.json")
BARALHOS_PATH = os.path.join(DATA_DIR, "baralhos.json")
SHARED_DECKS_PATH = os.path.join(DATA_DIR, "shared_decks.json")
FRIEND_REQUESTS_PATH = os.path.join(DATA_DIR, "friend_requests.json")
DECK_INVITES_PATH = os.path.join(DATA_DIR, "deck_invites.json")

# --- Criação de Pastas ---
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# --- Funções de Utilidade para Dados ---
def carregar_dados(caminho, default=None):
    if not os.path.exists(caminho):
        return default or {}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content) if content else (default or {})
    except (json.JSONDecodeError, FileNotFoundError):
        return default or {}


def salvar_dados(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


# --- Carregamento Inicial de Dados ---
usuarios = carregar_dados(USERS_PATH, {})
baralhos = carregar_dados(BARALHOS_PATH, {})
shared_decks = carregar_dados(SHARED_DECKS_PATH, {})
friend_requests = carregar_dados(FRIEND_REQUESTS_PATH, {})
deck_invites = carregar_dados(DECK_INVITES_PATH, {})

# --- Rota para listar desafios pendentes ---
@app.route('/competicao/desafios')
def desafios_pendentes():
    if "user_id" not in session:
        return jsonify({"desafios": []})
    user_id = session["user_id"]
    usuario = usuarios[user_id]
    desafios = []
    for comp in usuario.get("competicoes", []):
        if comp.get("user2") == user_id and comp.get("status") == "pendente":
            desafios.append({
                "id": comp["id"],
                "de": usuarios[comp["user1"]]["nome"] if comp["user1"] in usuarios else comp["user1"],
                "baralho": comp.get("deck_id", "")
            })
    return jsonify({"desafios": desafios})

# --- Rota para recusar desafio ---
@app.route('/competicao/recusar', methods=['POST'])
def recusar_competicao():
    data = request.json
    comp_id = data.get('comp_id')
    for uid, user in usuarios.items():
        for comp in user.get("competicoes", []):
            if comp.get("id") == comp_id:
                comp["status"] = "recusado"
                salvar_dados(USERS_PATH, usuarios)
                # Marca sequência de recusas
                try:
                    from achievements import increment_stat, award_if_eligible
                    from feed import registrar_atividade
                    increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), uid, 'invites_refused_streak', 1)
                    award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, uid)
                except Exception:
                    pass
                return jsonify({"msg": "Desafio recusado!"})
    return jsonify({"msg": "Desafio não encontrado."}), 404

# --- Rotas de Competição entre Amigos ---
from utils import Competicao, criar_competicao

@app.route('/competicao/convidar', methods=['POST'])
def convidar_competicao():
    data = request.json
    user1 = data.get('user1')
    user2 = data.get('user2')
    deck_ids = data.get('deck_ids', [])
    criados = []
    if user2 in usuarios:
        for deck_id in deck_ids:
            comp = criar_competicao(user1, user2, deck_id)
            usuarios[user2].setdefault("competicoes", []).append(comp.to_dict())
            criados.append(comp.to_dict())
        salvar_dados(USERS_PATH, usuarios)
        try:
            from feed import registrar_atividade
            registrar_atividade('desafio', user1, f'Enviou um desafio para {usuarios[user2]["nome"]} (deck {deck_ids[0]})')
        except Exception:
            pass
    return jsonify({"msg": f"{len(criados)} desafio(s) enviado(s)!", "competicoes": criados})

@app.route('/competicao/aceitar', methods=['POST'])
def aceitar_competicao():
    data = request.json
    comp_id = data.get('comp_id')
    # Procurar e atualizar status do desafio para 'aceita'
    for uid, user in usuarios.items():
        for comp in user.get("competicoes", []):
            if comp.get("id") == comp_id:
                comp["status"] = "aceita"
                salvar_dados(USERS_PATH, usuarios)
                adicionar_conquista(uid, "Desafio Aceito")
                try:
                    from feed import registrar_atividade
                    registrar_atividade('desafio', uid, f'Aceitou um desafio!')
                except Exception:
                    pass
                return jsonify({"msg": "Competição aceita!", "comp_id": comp_id})
    return jsonify({"msg": "Desafio não encontrado."}), 404

@app.route('/competicao/ranking', methods=['GET'])
def ranking_competicao():
    # Aqui você buscaria e retornaria o ranking dos amigos
    ranking = []
    return jsonify({"ranking": ranking})

@app.route('/competicao/finalizar', methods=['POST'])
def finalizar_competicao():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('comp_id')
    winner_id = data.get('winner_id')
    pontos1 = data.get('pontos1')
    pontos2 = data.get('pontos2')
    deck_id = None
    user1 = None
    user2 = None
    # Localiza competição e marca como finalizada
    for uid, user in usuarios.items():
        for comp in user.get('competicoes', []):
            if comp.get('id') == comp_id:
                comp['status'] = 'finalizada'
                deck_id = comp.get('deck_id')
                user1 = comp.get('user1')
                user2 = comp.get('user2')
    salvar_dados(USERS_PATH, usuarios)
    try:
        from feed import registrar_atividade
        nome1 = usuarios.get(user1, {}).get('nome', user1)
        nome2 = usuarios.get(user2, {}).get('nome', user2)
        deck_nome = deck_id
        vencedor_nome = usuarios.get(winner_id, {}).get('nome', winner_id)
        perdedor_nome = nome1 if winner_id == user2 else nome2
        registrar_atividade('resultado', winner_id, f"{vencedor_nome} venceu {perdedor_nome} em um desafio usando o baralho '{deck_nome}'!")
    except Exception:
        pass
    return jsonify({"msg": "Resultado registrado no feed."})


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
    user = usuarios.get(user_id)
    if not user:
        return False
    last_seen = user.get("last_seen", 0)
    return (agora_timestamp() - last_seen) < 300  # 5 minutos


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def pode_usar_ia(user_id):
    user = usuarios.get(user_id)
    if not user:
        return False
    ultimo_uso = user.get("ultimo_uso_ia", 0)
    return (agora_timestamp() - ultimo_uso) >= 120  # 2 minutos


def tempo_restante_ia(user_id):
    user = usuarios.get(user_id)
    if not user:
        return 0
    ultimo_uso = user.get("ultimo_uso_ia", 0)
    tempo_passado = agora_timestamp() - ultimo_uso
    return max(0, 120 - tempo_passado)  # 2 minutos


def contar_notificacoes(user_id):
    """Conta total de notificações pendentes"""
    pedidos_amizade = len(friend_requests.get(user_id, []))
    convites_baralho = len(deck_invites.get(user_id, []))
    return pedidos_amizade + convites_baralho


# --- Decorador de Login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Você precisa fazer login para acessar esta página.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]
        if user_id not in usuarios:
            session.clear()
            flash("Sessão inválida. Faça login novamente.", "danger")
            return redirect(url_for("login"))

        g.user = usuarios[user_id]
        return f(*args, **kwargs)

    return decorated_function


# --- Context Processor ---
@app.context_processor
def inject_user():
    user_data = None
    notificacoes = 0
    if "user_id" in session and session["user_id"] in usuarios:
        user_data = ensure_user_defaults(usuarios[session["user_id"]])
        notificacoes = contar_notificacoes(session["user_id"])

    return {
        "usuario": user_data,
        "notificacoes_count": notificacoes,
        "data_formatada": data_formatada,
        "usuario_online": usuario_online
    }


# --- Rota Raiz ---
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

# --- Página de Competição ---
@app.route("/competicao")
def pagina_competicao():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    usuario = usuarios[user_id]

    # Buscar amigos do usuário logado (nomes reais)
    # Lista de amigos: id e nome
    amigos = []
    for friend_id in usuario.get("friends", []):
        amigo = usuarios.get(friend_id)
        if amigo:
            amigos.append({
                "id": friend_id,
                "nome": amigo.get("nome") or amigo.get("email") or friend_id
            })

    # Lista de baralhos: id e nome
    user_baralhos = []
    baralhos_usuario = baralhos.get(user_id) or baralhos.get(usuario.get("email")) or baralhos.get(usuario.get("nome"))
    if baralhos_usuario:
        if isinstance(baralhos_usuario, dict):
            for deck_id, deck in baralhos_usuario.items():
                if isinstance(deck, dict):
                    nome = deck.get("nome") or deck_id
                else:
                    nome = deck_id
                user_baralhos.append({"id": deck_id, "nome": nome})
        elif isinstance(baralhos_usuario, list):
            for idx, deck in enumerate(baralhos_usuario):
                if isinstance(deck, dict):
                    nome = deck.get("nome") or f"Baralho {idx+1}"
                else:
                    nome = f"Baralho {idx+1}"
                user_baralhos.append({"id": str(idx), "nome": nome})
    return render_template("competicao.html", usuario=usuario, amigos=amigos, baralhos=user_baralhos)


# --- Autenticação ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        if not email or not senha:
            flash("Email e senha são obrigatórios.", "warning")
            return render_template("login.html")

        user_id, user_data = next(((uid, u) for uid, u in usuarios.items()
                                   if u.get("email", "").lower() == email), (None, None))

        if user_data and bcrypt.check_password_hash(user_data["senha"], senha):
            session["user_id"] = user_id
            user_data["last_seen"] = agora_timestamp()
            salvar_dados(USERS_PATH, usuarios)
            flash(f"Bem-vindo de volta, {user_data['nome']}!", "success")
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
        if any(u.get("email", "").lower() == email for u in usuarios.values()):
            flash("Este email já está cadastrado. Tente fazer login ou use outro email.", "danger")
            return render_template("register.html")

        # Cria novo usuário
        user_id = gerar_id_usuario()
        hashed_senha = bcrypt.generate_password_hash(senha).decode("utf-8")
        agora = agora_timestamp()

        usuarios[user_id] = {
            "id": user_id, "nome": nome, "email": email, "senha": hashed_senha,
            "avatar": "", "points": 0, "last_seen": agora,
            "friends": [], "ultimo_uso_ia": 0, "data_criacao": agora,
            "data_nascimento": data_nascimento, "frase_pessoal": "",
            "tema": "dark"
        }
        baralhos[user_id] = {}
        friend_requests[user_id] = []
        deck_invites[user_id] = []

        salvar_dados(USERS_PATH, usuarios)
        salvar_dados(BARALHOS_PATH, baralhos)
        salvar_dados(FRIEND_REQUESTS_PATH, friend_requests)
        salvar_dados(DECK_INVITES_PATH, deck_invites)

        flash("Conta criada com sucesso! Agora você pode fazer login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        nome = request.form["nome"].strip()
        nova_senha = request.form["senha"]

        if not email or not nome or not nova_senha:
            flash("Todos os campos são obrigatórios.", "warning")
            return render_template("reset_password.html")

        user_id, user_data = next(((uid, u) for uid, u in usuarios.items()
                                   if u.get("email", "").lower() == email and u.get("nome") == nome), (None, None))

        if user_data:
            if len(nova_senha) < 6:
                flash("A nova senha deve ter pelo menos 6 caracteres.", "warning")
                return render_template("reset_password.html")

            hashed_senha = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
            usuarios[user_id]["senha"] = hashed_senha
            salvar_dados(USERS_PATH, usuarios)
            flash("Senha redefinida com sucesso! Agora você pode fazer login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Usuário não encontrado com os dados fornecidos. Verifique o email e nome.", "danger")

    return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta com sucesso.", "success")
    return redirect(url_for("login"))


# --- Rotas Principais ---
@app.route("/home")
@login_required
def home():
    user_baralhos = baralhos.get(g.user["id"], {})

    # Baralhos compartilhados onde o usuário tem acesso
    baralhos_compartilhados = {}
    for deck_id, deck_data in shared_decks.items():
        if g.user["id"] in deck_data.get("members", []) or deck_data.get("owner") == g.user["id"]:
            baralhos_compartilhados[deck_id] = deck_data

    return render_template("index.html",
                           baralhos=user_baralhos,
                           baralhos_compartilhados=baralhos_compartilhados)

@app.route('/insights')
@login_required
def insights():
    # Coleta dados simples para gráficos
    stats = g.user.get('stats', {})
    history = stats.get('study_history', [])
    error_patterns = stats.get('error_patterns', {})
    # Heatmap por hora do dia
    heat = [0]*24
    for item in history:
        try:
            ts = int(item.get('ts', 0))
            from datetime import datetime
            hour = datetime.fromtimestamp(ts).hour
            heat[hour] += 1
        except Exception:
            pass
    return render_template('insights.html', heat=heat, error_patterns=error_patterns)

@app.route("/meus_baralhos")
@login_required
def listar_baralhos():
    # Monta visão unificada: próprios e compartilhados
    user_baralhos = baralhos.get(g.user["id"], {})
    baralhos_compartilhados = {}
    for deck_id, deck_data in shared_decks.items():
        if g.user["id"] in deck_data.get("members", []) or deck_data.get("owner") == g.user["id"]:
            baralhos_compartilhados[deck_id] = deck_data
    return render_template("meus_baralhos.html",
                           baralhos=user_baralhos,
                           baralhos_compartilhados=baralhos_compartilhados,
                           usuarios=usuarios)


@app.route("/alternar_tema", methods=["POST"])
@login_required
def alternar_tema():
    tema_atual = g.user.get("tema", "dark")
    novo_tema = "light" if tema_atual == "dark" else "dark"
    g.user["tema"] = novo_tema
    salvar_dados(USERS_PATH, usuarios)
    return jsonify({"tema": novo_tema})


# --- Sistema de Amizade ---
@app.route("/amigos")
@login_required
def amigos():
    # Buscar informações dos amigos
    amigos_info = []
    for friend_id in g.user.get("friends", []):
        friend = usuarios.get(friend_id)
        if friend:
            amigos_info.append({
                "id": friend_id,
                "nome": friend["nome"],
                "avatar": friend.get("avatar", ""),
                "online": usuario_online(friend_id),
                "points": friend.get("points", 0)
            })

    # Pedidos de amizade recebidos
    pedidos_recebidos = []
    for request_data in friend_requests.get(g.user["id"], []):
        sender = usuarios.get(request_data["from"])
        if sender:
            pedidos_recebidos.append({
                "id": request_data["from"],
                "nome": sender["nome"],
                "avatar": sender.get("avatar", ""),
                "timestamp": request_data["timestamp"]
            })

    # Convites para baralhos recebidos
    convites_recebidos = []
    for invite_data in deck_invites.get(g.user["id"], []):
        sender = usuarios.get(invite_data["from"])
        deck_data = shared_decks.get(invite_data["deck_id"])
        if sender and deck_data:
            convites_recebidos.append({
                "id": invite_data["deck_id"],
                "from_id": invite_data["from"],
                "from_nome": sender["nome"],
                "deck_nome": deck_data["nome"],
                "timestamp": invite_data["timestamp"]
            })

    return render_template("amigos.html",
                           amigos=amigos_info,
                           pedidos_recebidos=pedidos_recebidos,
                           convites_recebidos=convites_recebidos)


@app.route("/enviar_pedido_amizade", methods=["POST"])
@login_required
def enviar_pedido_amizade():
    friend_id = request.form.get("friend_id", "").strip().upper()

    if not friend_id:
        flash("ID do amigo não pode ser vazio.", "warning")
        return redirect(url_for("amigos"))

    if friend_id == g.user["id"]:
        flash("Você não pode adicionar a si mesmo como amigo.", "warning")
        return redirect(url_for("amigos"))

    if friend_id not in usuarios:
        flash("Usuário não encontrado. Verifique se o ID está correto.", "danger")
        return redirect(url_for("amigos"))

    if friend_id in g.user.get("friends", []):
        flash("Este usuário já é seu amigo.", "info")
        return redirect(url_for("amigos"))

    # Verifica se já existe um pedido pendente
    pedidos_existentes = friend_requests.get(friend_id, [])
    if any(p["from"] == g.user["id"] for p in pedidos_existentes):
        flash("Você já enviou um pedido de amizade para este usuário.", "info")
        return redirect(url_for("amigos"))

    # Adiciona o pedido de amizade
    if friend_id not in friend_requests:
        friend_requests[friend_id] = []

    friend_requests[friend_id].append({
        "from": g.user["id"],
        "timestamp": agora_timestamp()
    })

    salvar_dados(FRIEND_REQUESTS_PATH, friend_requests)

    friend_name = usuarios[friend_id]["nome"]
    flash(f"Pedido de amizade enviado para {friend_name}!", "success")
    try:
        from feed import registrar_atividade
        registrar_atividade('amizade', g.user["id"], f'Você enviou um pedido de amizade para {friend_name}')
    except Exception:
        pass
    return redirect(url_for("amigos"))


@app.route("/aceitar_amizade/<friend_id>", methods=["POST"])
@login_required
def aceitar_amizade(friend_id):
    # Remove o pedido da lista
    pedidos = friend_requests.get(g.user["id"], [])
    friend_requests[g.user["id"]] = [p for p in pedidos if p["from"] != friend_id]

    # Adiciona aos amigos mutuamente
    if friend_id not in g.user.get("friends", []):
        g.user.setdefault("friends", []).append(friend_id)

    if g.user["id"] not in usuarios[friend_id].get("friends", []):
        usuarios[friend_id].setdefault("friends", []).append(g.user["id"])

    salvar_dados(USERS_PATH, usuarios)
    salvar_dados(FRIEND_REQUESTS_PATH, friend_requests)

    friend_name = usuarios[friend_id]["nome"]
    flash(f"Agora você e {friend_name} são amigos!", "success")
    try:
        from feed import registrar_atividade
        registrar_atividade('amizade', g.user["id"], f'Você adicionou {friend_name} como amigo')
        registrar_atividade('amizade', friend_id, f'Você adicionou {g.user["nome"]} como amigo')
    except Exception:
        pass
    # Stats e conquistas sociais
    try:
        from achievements import increment_stat, award_if_eligible
        increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'friends_added', 1)
        award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"])
    except Exception:
        pass
    return redirect(url_for("amigos"))


@app.route("/recusar_amizade/<friend_id>", methods=["POST"])
@login_required
def recusar_amizade(friend_id):
    # Remove o pedido da lista
    pedidos = friend_requests.get(g.user["id"], [])
    friend_requests[g.user["id"]] = [p for p in pedidos if p["from"] != friend_id]

    salvar_dados(FRIEND_REQUESTS_PATH, friend_requests)

    flash("Pedido de amizade recusado.", "info")
    return redirect(url_for("amigos"))


@app.route("/remover_amigo/<friend_id>", methods=["POST"])
@login_required
def remover_amigo(friend_id):
    # Remove mutuamente
    if friend_id in g.user.get("friends", []):
        g.user["friends"].remove(friend_id)

    if g.user["id"] in usuarios[friend_id].get("friends", []):
        usuarios[friend_id]["friends"].remove(g.user["id"])

    salvar_dados(USERS_PATH, usuarios)
    flash("Amigo removido da sua lista.", "success")
    return redirect(url_for("amigos"))


@app.route("/perfil_amigo/<friend_id>")
@login_required
def perfil_amigo(friend_id):
    if friend_id not in g.user.get("friends", []):
        flash("Você só pode ver o perfil de seus amigos.", "warning")
        return redirect(url_for("amigos"))

    friend = ensure_user_defaults(usuarios.get(friend_id))
    if not friend:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("amigos"))
    # Estatísticas derivadas
    stats = friend.get('stats', {})
    cards_created = stats.get('cards_created', 0)
    desafios_vencidos = stats.get('challenges_won', 0)
    mensagens_enviadas = stats.get('messages_sent', 0)
    # Histórico de atividades do amigo
    try:
        from feed import atividades_do_usuario
        historico = atividades_do_usuario(friend_id)[:20]
    except Exception:
        historico = []
    from achievements import ACHIEVEMENTS as _ACH
    ACHIEVEMENTS_MAP = { cfg['name']: { 'desc': cfg['desc'], 'category': cfg['category'], 'difficulty': cfg['difficulty'] } for cfg in _ACH.values() }
    return render_template("perfil_amigo.html", amigo=friend, stats={
        'cards_created': cards_created,
        'challenges_won': desafios_vencidos,
        'messages_sent': mensagens_enviadas
    }, historico=historico, ACHIEVEMENTS_MAP=ACHIEVEMENTS_MAP)


# --- Sistema de Compartilhamento ---
@app.route("/compartilhar_baralho/<baralho_id>")
@login_required
def compartilhar_baralho(baralho_id):
    # Verifica se o baralho existe e pertence ao usuário
    if baralho_id not in baralhos.get(g.user["id"], {}):
        flash("Baralho não encontrado.", "danger")
        return redirect(url_for("home"))

    baralho = baralhos[g.user["id"]][baralho_id]
    amigos_info = []

    for friend_id in g.user.get("friends", []):
        friend = usuarios.get(friend_id)
        if friend:
            amigos_info.append({
                "id": friend_id,
                "nome": friend["nome"],
                "avatar": friend.get("avatar", ""),
                "online": usuario_online(friend_id)
            })

    return render_template("compartilhar_baralho.html",
                           baralho=baralho,
                           baralho_id=baralho_id,
                           amigos=amigos_info)


@app.route("/enviar_convite_baralho", methods=["POST"])
@login_required
def enviar_convite_baralho():
    baralho_id = request.form.get("baralho_id")
    friend_id = request.form.get("friend_id")

    if not baralho_id or not friend_id:
        flash("Dados inválidos.", "danger")
        return redirect(url_for("home"))

    if baralho_id not in baralhos.get(g.user["id"], {}):
        flash("Baralho não encontrado.", "danger")
        return redirect(url_for("home"))

    if friend_id not in g.user.get("friends", []):
        flash("Você só pode enviar convites para seus amigos.", "danger")
        return redirect(url_for("compartilhar_baralho", baralho_id=baralho_id))

    # Cria baralho compartilhado se não existir
    shared_deck_id = f"shared_{baralho_id}"
    if shared_deck_id not in shared_decks:
        baralho_original = baralhos[g.user["id"]][baralho_id]
        shared_decks[shared_deck_id] = {
            "nome": baralho_original["nome"],
            "cor": baralho_original["cor"],
            "cards": baralho_original["cards"].copy(),
            "owner": g.user["id"],
            "members": [],
            "created_at": agora_timestamp()
        }
        salvar_dados(SHARED_DECKS_PATH, shared_decks)

    # Adiciona o convite
    if friend_id not in deck_invites:
        deck_invites[friend_id] = []

    deck_invites[friend_id].append({
        "deck_id": shared_deck_id,
        "from": g.user["id"],
        "timestamp": agora_timestamp()
    })

    salvar_dados(DECK_INVITES_PATH, deck_invites)

    friend_name = usuarios[friend_id]["nome"]
    baralho_nome = baralhos[g.user["id"]][baralho_id]["nome"]
    flash(f"Convite para o baralho '{baralho_nome}' enviado para {friend_name}!", "success")
    try:
        from feed import registrar_atividade
        registrar_atividade('compartilhar', g.user["id"], f"Você compartilhou o baralho '{baralho_nome}' com {friend_name}")
    except Exception:
        pass
    return redirect(url_for("compartilhar_baralho", baralho_id=baralho_id))


@app.route("/aceitar_convite_baralho/<deck_id>", methods=["POST"])
@login_required
def aceitar_convite_baralho(deck_id):
    # Remove o convite da lista
    convites = deck_invites.get(g.user["id"], [])
    convite = next((c for c in convites if c["deck_id"] == deck_id), None)

    if not convite:
        flash("Convite não encontrado.", "danger")
        return redirect(url_for("amigos"))

    deck_invites[g.user["id"]] = [c for c in convites if c["deck_id"] != deck_id]

    # Adiciona como membro do baralho compartilhado
    if deck_id in shared_decks:
        if g.user["id"] not in shared_decks[deck_id].get("members", []):
            shared_decks[deck_id].setdefault("members", []).append(g.user["id"])
            salvar_dados(SHARED_DECKS_PATH, shared_decks)

    salvar_dados(DECK_INVITES_PATH, deck_invites)

    deck_name = shared_decks[deck_id]["nome"]
    flash(f"Você agora tem acesso ao baralho compartilhado '{deck_name}'!", "success")
    try:
        from feed import registrar_atividade
        registrar_atividade('compartilhar', g.user["id"], f"Você aceitou o convite para o baralho '{deck_name}'")
    except Exception:
        pass
    return redirect(url_for("amigos"))


@app.route("/recusar_convite_baralho/<deck_id>", methods=["POST"])
@login_required
def recusar_convite_baralho(deck_id):
    # Remove o convite da lista
    convites = deck_invites.get(g.user["id"], [])
    deck_invites[g.user["id"]] = [c for c in convites if c["deck_id"] != deck_id]

    salvar_dados(DECK_INVITES_PATH, deck_invites)

    flash("Convite para baralho recusado.", "info")
    return redirect(url_for("amigos"))


# --- Geração com IA ---
@app.route("/gerar_ia", methods=["GET", "POST"])
@login_required
def gerar_ia():
    if request.method == "POST":
        # Verifica se a IA está disponível
        if not model:
            flash("Serviço de IA temporariamente indisponível. Tente novamente mais tarde.", "danger")
            return redirect(url_for("gerar_ia"))

        # Verifica cooldown
        if not pode_usar_ia(g.user["id"]):
            tempo_restante = tempo_restante_ia(g.user["id"])
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            flash(f"Aguarde {minutos}m {segundos}s antes de gerar novos cards com IA.", "warning")
            return redirect(url_for("gerar_ia"))

        tema = request.form.get("tema", "").strip()
        quantidade = int(request.form.get("quantidade", 5))
        nome_baralho = request.form.get("nome_baralho", "").strip()
        cor_baralho = request.form.get("cor_baralho", "#3b82f6")

        if not tema or not nome_baralho:
            flash("Tema e nome do baralho são obrigatórios.", "warning")
            return redirect(url_for("gerar_ia"))

        if quantidade > 15:
            flash("Máximo de 15 cards por geração.", "warning")
            return redirect(url_for("gerar_ia"))

        try:
            print(f"🤖 Gerando {quantidade} cards sobre '{tema}'...")

            prompt = f"""Crie exatamente {quantidade} flashcards educativos sobre o tema \"{tema}\".\n\nIMPORTANTE: Responda APENAS com um array JSON válido, sem texto adicional, sem markdown, sem explicações.\n\nFormato exato esperado:\n[\n  {{\"frente\": \"pergunta 1\", \"verso\": \"resposta 1\"}},\n  {{\"frente\": \"pergunta 2\", \"verso\": \"resposta 2\"}}\n]\n\nRegras:\n- Perguntas claras e diretas\n- Respostas concisas e precisas\n- Exatamente {quantidade} flashcards\n- Apenas JSON válido na resposta\n\nTema: {tema}"""

            response = model.generate_content(prompt)
            content = response.text.strip()

            # Limpa a resposta removendo markdown se presente
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            if content.startswith("```"):
                content = content[3:]

            content = content.strip()

            # Tenta fazer o parse do JSON
            try:
                generated_cards = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ Erro de JSON: {e}")
                raise ValueError("Resposta da IA não está em formato JSON válido")

            # Validação da estrutura
            if not isinstance(generated_cards, list):
                raise ValueError("Resposta deve ser uma lista de cards")

            if len(generated_cards) == 0:
                raise ValueError("Nenhum card foi gerado")

            # Valida cada card
            cards_validos = []
            for i, card_data in enumerate(generated_cards):
                if not isinstance(card_data, dict):
                    continue

                if "frente" not in card_data or "verso" not in card_data:
                    continue

                frente = str(card_data["frente"]).strip()
                verso = str(card_data["verso"]).strip()

                if not frente or not verso:
                    continue

                cards_validos.append({"frente": frente, "verso": verso})

            if not cards_validos:
                raise ValueError("Nenhum card válido foi gerado")

            # Cria o baralho
            baralho_id = ''.join(filter(str.isalnum, nome_baralho)).lower() + f"_{uuid4().hex[:4]}"
            user_id = g.user["id"]

            baralhos.setdefault(user_id, {})[baralho_id] = {
                "nome": nome_baralho,
                "cor": cor_baralho,
                "cards": []
            }

            # Adiciona os cards válidos
            for card_data in cards_validos:
                new_card = {
                    "id": str(uuid4()),
                    "frente": card_data["frente"],
                    "verso": card_data["verso"]
                }
                baralhos[user_id][baralho_id]["cards"].append(new_card)

            # Atualiza o último uso da IA
            usuarios[user_id]["ultimo_uso_ia"] = agora_timestamp()

            salvar_dados(BARALHOS_PATH, baralhos)
            salvar_dados(USERS_PATH, usuarios)

            # Stats IA e checagem de conquistas
            try:
                from achievements import increment_stat, award_if_eligible
                increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), user_id, 'ia_cards_generated', len(cards_validos))
                award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), __import__('feed').feed.registrar_atividade if False else __import__('feed').registrar_atividade, user_id, { 'deck_cards_count': len(baralhos[user_id][baralho_id]["cards"]) })
            except Exception:
                pass

            flash(f"🎉 {len(cards_validos)} cards gerados com IA e adicionados ao baralho '{nome_baralho}'!", "success")
            return redirect(url_for("estudar", baralho_id=baralho_id))

        except Exception as e:
            print(f"❌ Erro na IA: {e}")
            flash("Erro temporário na geração de IA. Tente novamente em alguns minutos.", "danger")

        return redirect(url_for("gerar_ia"))

    # Calcula tempo restante para próximo uso
    tempo_restante = tempo_restante_ia(g.user["id"])
    pode_usar = pode_usar_ia(g.user["id"])

    return render_template("gerar_ia.html",
                           pode_usar_ia=pode_usar,
                           tempo_restante=tempo_restante)


# --- Rotas de Baralhos e Cards ---

# --- Gerenciar Baralho ---
@app.route("/gerenciar_baralho/<baralho_id>")
@login_required
def gerenciar_baralho(baralho_id):
    # Permite ao dono ou membro acessar gerenciamento
    baralho = None
    baralho_compartilhado = False
    is_owner = False

    if baralho_id in baralhos.get(g.user["id"], {}):
        baralho = baralhos[g.user["id"]][baralho_id]
        is_owner = True
    elif baralho_id in shared_decks:
        deck_data = shared_decks[baralho_id]
        if g.user["id"] in deck_data.get("members", []) or deck_data.get("owner") == g.user["id"]:
            baralho = deck_data
            baralho_compartilhado = True
            is_owner = deck_data.get("owner") == g.user["id"]

    if not baralho:
        flash("Baralho não encontrado ou você não tem permissão para acessá-lo.", "danger")
        return redirect(url_for("home"))

    context = dict(
        baralho=baralho,
        baralho_id=baralho_id,
        baralho_compartilhado=baralho_compartilhado,
        is_owner=is_owner
    )
    # Se for compartilhado, passar usuarios para o template
    if baralho_compartilhado:
        context["usuarios"] = usuarios
    return render_template("gerenciar_baralho.html", **context)

# --- Editar Baralho (nome/cor) ---
@app.route("/editar_baralho/<baralho_id>", methods=["GET", "POST"])
@login_required
def editar_baralho(baralho_id):
    # Só o dono pode editar
    if baralho_id in baralhos.get(g.user["id"], {}):
        baralho = baralhos[g.user["id"]][baralho_id]
        is_shared = False
    elif baralho_id in shared_decks and shared_decks[baralho_id].get("owner") == g.user["id"]:
        baralho = shared_decks[baralho_id]
        is_shared = True
    else:
        flash("Apenas o dono pode editar este baralho.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            # Excluir baralho
            if is_shared:
                if baralho_id in shared_decks:
                    del shared_decks[baralho_id]
                    salvar_dados(SHARED_DECKS_PATH, shared_decks)
                    flash("Baralho compartilhado excluído com sucesso!", "success")
                    return redirect(url_for("home"))
                else:
                    flash("Baralho compartilhado não encontrado.", "danger")
                    return redirect(url_for("home"))
            else:
                user_baralhos = baralhos.get(g.user["id"], {})
                if baralho_id in user_baralhos:
                    del user_baralhos[baralho_id]
                    salvar_dados(BARALHOS_PATH, baralhos)
                    flash("Baralho excluído com sucesso!", "success")
                    return redirect(url_for("home"))
                else:
                    flash("Baralho não encontrado.", "danger")
                    return redirect(url_for("home"))
        else:
            nome = request.form.get("nome", "").strip()
            cor = request.form.get("cor", "#3b82f6")
            if not nome:
                flash("O nome do baralho não pode ser vazio.", "warning")
                return render_template("editar_baralho.html", baralho=baralho, baralho_id=baralho_id)
            baralho["nome"] = nome
            baralho["cor"] = cor
            if is_shared:
                salvar_dados(SHARED_DECKS_PATH, shared_decks)
            else:
                salvar_dados(BARALHOS_PATH, baralhos)
            flash("Baralho atualizado com sucesso!", "success")
            return redirect(url_for("gerenciar_baralho", baralho_id=baralho_id))

    return render_template("editar_baralho.html", baralho=baralho, baralho_id=baralho_id)
@app.route("/estudar/<baralho_id>")
@login_required
def estudar(baralho_id):
    # Verifica se é um baralho próprio ou compartilhado
    baralho = None
    baralho_compartilhado = False


    # Primeiro verifica nos baralhos próprios
    if baralho_id in baralhos.get(g.user["id"], {}):
        baralho = baralhos[g.user["id"]][baralho_id]
    # Depois verifica nos baralhos compartilhados
    elif baralho_id in shared_decks:
        deck_data = shared_decks[baralho_id]
        is_owner = deck_data.get("owner") == g.user["id"]
        member_perms = deck_data.get("permissoes", {}).get(g.user["id"], {})
        if is_owner or (g.user["id"] in deck_data.get("members", []) and member_perms.get("ler")):
            baralho = deck_data
            baralho_compartilhado = True
        else:
            flash("Você não tem permissão para acessar este baralho.", "danger")
            return redirect(url_for("home"))

    if not baralho:
        flash("Baralho não encontrado ou você não tem permissão para acessá-lo.", "danger")
        return redirect(url_for("home"))

    # Contagem de revisão por baralho (para conquista)
    try:
        from achievements import award_if_eligible
        stats = g.user.setdefault('stats', {})
        deck_counts = stats.setdefault('deck_review_counts', {})
        deck_counts[baralho_id] = deck_counts.get(baralho_id, 0) + 1
        salvar_dados(USERS_PATH, usuarios)
        from feed import registrar_atividade
        award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"]) 
    except Exception:
        pass

    return render_template("estudar.html",
                           baralho=baralho,
                           baralho_id=baralho_id,
                           baralho_compartilhado=baralho_compartilhado,
                           usuario=g.user,
                           cards=baralho.get("cards", []))


@app.route("/criar_card", methods=["GET", "POST"])
@login_required
def criar_card():
    if request.method == "POST":
        frente = request.form.get("frente", "").strip()
        verso = request.form.get("verso", "").strip()
        baralho_existente = request.form.get("baralho_existente", "").strip()
        novo_baralho = request.form.get("novo_baralho", "").strip()
        cor_baralho = request.form.get("cor_baralho", "#3b82f6")

        if not frente or not verso:
            flash("Pergunta e resposta são obrigatórias.", "warning")
            return redirect(url_for("criar_card"))

        new_card = {"id": str(uuid4()), "frente": frente, "verso": verso}
        # Humor: memecard / python
        try:
            from achievements import increment_stat, award_if_eligible
            from feed import registrar_atividade
            text_blob = f"{frente} {verso}".lower()
            if any(k in text_blob for k in ["shrek", "doge", "rickroll", "sus", "among us"]):
                increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'meme_cards', 1)
                award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"]) 
            if any(k in text_blob for k in ["def ", "print(", "lambda ", "for ", "import ", "class "]):
                increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'python_cards', 1)
                award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"]) 
        except Exception:
            pass
        user_id = g.user["id"]

        # Determina qual baralho usar
        if baralho_existente:
            # Verifica se é baralho próprio ou compartilhado
            if baralho_existente in baralhos.get(user_id, {}):
                baralhos[user_id][baralho_existente]["cards"].append(new_card)
                salvar_dados(BARALHOS_PATH, baralhos)
                target_baralho = baralho_existente
                try:
                    from feed import registrar_atividade
                    deck_nome = baralhos[user_id][baralho_existente]["nome"]
                    registrar_atividade('criou_card', user_id, f"Criou um card no baralho '{deck_nome}'")
                    increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), user_id, 'cards_created', 1)
                    award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, user_id)
                except Exception:
                    pass
            elif baralho_existente in shared_decks:
                # Verifica permissão no baralho compartilhado
                deck_data = shared_decks[baralho_existente]
                if user_id in deck_data.get("members", []) or deck_data.get("owner") == user_id:
                    shared_decks[baralho_existente]["cards"].append(new_card)
                    salvar_dados(SHARED_DECKS_PATH, shared_decks)
                    target_baralho = baralho_existente
                    try:
                        from feed import registrar_atividade
                        deck_nome = deck_data.get("nome", baralho_existente)
                        registrar_atividade('criou_card', user_id, f"Criou um card no baralho compartilhado '{deck_nome}'")
                        increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), user_id, 'cards_created', 1)
                        award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, user_id)
                    except Exception:
                        pass
                else:
                    flash("Você não tem permissão para adicionar cards neste baralho.", "danger")
                    return redirect(url_for("criar_card"))
            else:
                flash("Baralho não encontrado.", "danger")
                return redirect(url_for("criar_card"))
        elif novo_baralho:
            # Cria novo baralho
            baralho_id = ''.join(filter(str.isalnum, novo_baralho)).lower() + f"_{uuid4().hex[:4]}"
            baralhos.setdefault(user_id, {})[baralho_id] = {
                "nome": novo_baralho, "cor": cor_baralho, "cards": [new_card]
            }
            salvar_dados(BARALHOS_PATH, baralhos)
            target_baralho = baralho_id
            try:
                from feed import registrar_atividade
                registrar_atividade('criou_baralho', user_id, f"Criou o baralho '{novo_baralho}'")
                registrar_atividade('criou_card', user_id, f"Criou um card no baralho '{novo_baralho}'")
                increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), user_id, 'cards_created', 1)
                award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, user_id, { 'deck_cards_count': len(baralhos[user_id][baralho_id]["cards"]) })
            except Exception:
                pass
        else:
            flash("Selecione um baralho existente ou crie um novo.", "warning")
            return redirect(url_for("criar_card"))

        flash("Card criado com sucesso!", "success")
        return redirect(url_for("estudar", baralho_id=target_baralho))

    # GET request
    user_baralhos = baralhos.get(g.user["id"], {})

    # Adiciona baralhos compartilhados onde o usuário pode criar cards
    baralhos_editaveis = dict(user_baralhos)
    for deck_id, deck_data in shared_decks.items():
        is_owner = deck_data.get("owner") == g.user["id"]
        member_perms = deck_data.get("permissoes", {}).get(g.user["id"], {})
        if is_owner or (g.user["id"] in deck_data.get("members", []) and member_perms.get("criar")):
            baralhos_editaveis[deck_id] = deck_data

    return render_template("criar_card.html", baralhos=baralhos_editaveis)


@app.route("/editar_card/<baralho_id>/<card_id>", methods=["GET", "POST"])
@login_required
def editar_card(baralho_id, card_id):
    # Encontra o baralho e card
    baralho = None
    is_shared = False


    if baralho_id in baralhos.get(g.user["id"], {}):
        baralho = baralhos[g.user["id"]][baralho_id]
    elif baralho_id in shared_decks:
        deck_data = shared_decks[baralho_id]
        is_owner = deck_data.get("owner") == g.user["id"]
        member_perms = deck_data.get("permissoes", {}).get(g.user["id"], {})
        if is_owner or (g.user["id"] in deck_data.get("members", []) and member_perms.get("deletar")):
            baralho = deck_data
            is_shared = True


    if not baralho:
        flash("Baralho não encontrado ou você não tem permissão para editar/excluir cards.", "danger")
        return redirect(url_for("home"))

    card = next((c for c in baralho["cards"] if c["id"] == card_id), None)
    if not card:
        flash("Card não encontrado.", "danger")
        return redirect(url_for("estudar", baralho_id=baralho_id))

    if request.method == "POST":
        frente = request.form.get("frente", "").strip()
        verso = request.form.get("verso", "").strip()

        if not frente or not verso:
            flash("Pergunta e resposta são obrigatórias.", "warning")
            return render_template("criar_card.html", card=card, baralho_id=baralho_id, editar=True)

        card["frente"] = frente
        card["verso"] = verso

        if is_shared:
            salvar_dados(SHARED_DECKS_PATH, shared_decks)
        else:
            salvar_dados(BARALHOS_PATH, baralhos)

        flash("Card atualizado com sucesso!", "success")
        return redirect(url_for("estudar", baralho_id=baralho_id))

    return render_template("criar_card.html", card=card, baralho_id=baralho_id, editar=True)


@app.route("/excluir_card/<baralho_id>/<card_id>", methods=["POST"])
@login_required
def excluir_card(baralho_id, card_id):
    # Encontra o baralho
    baralho = None
    is_shared = False

    if baralho_id in baralhos.get(g.user["id"], {}):
        baralho = baralhos[g.user["id"]][baralho_id]
    elif baralho_id in shared_decks:
        deck_data = shared_decks[baralho_id]
        if g.user["id"] in deck_data.get("members", []) or deck_data.get("owner") == g.user["id"]:
            baralho = deck_data
            is_shared = True

    if not baralho:
        flash("Baralho não encontrado.", "danger")
        return redirect(url_for("home"))

    # Remove o card
    baralho["cards"] = [c for c in baralho["cards"] if c["id"] != card_id]

    if is_shared:
        salvar_dados(SHARED_DECKS_PATH, shared_decks)
    else:
        salvar_dados(BARALHOS_PATH, baralhos)

    flash("Card excluído com sucesso!", "success")
    return redirect(url_for("estudar", baralho_id=baralho_id))


# --- Sistema de Desafio ---
@app.route("/desafio")
@login_required
def desafio():
    user_baralhos = baralhos.get(g.user["id"], {})
    return render_template("desafio.html", baralhos=user_baralhos)


@app.route("/iniciar_desafio", methods=["POST"])
@login_required
def iniciar_desafio():
    baralhos_selecionados = request.form.getlist("baralhos")
    tempo_por_questao = int(request.form.get("tempo", 30))
    max_questoes = int(request.form.get("max_questoes", 10))

    if not baralhos_selecionados:
        flash("Selecione pelo menos um baralho para o desafio.", "warning")
        return redirect(url_for("desafio"))

    # Coleta todos os cards dos baralhos selecionados
    todas_as_perguntas = []
    user_baralhos = baralhos.get(g.user["id"], {})

    for baralho_id in baralhos_selecionados:
        if baralho_id in user_baralhos:
            baralho = user_baralhos[baralho_id]
            for card in baralho["cards"]:
                todas_as_perguntas.append({
                    "id": card["id"],
                    "frente": card["frente"],
                    "verso": card["verso"],
                    "baralho": baralho["nome"]
                })

    if not todas_as_perguntas:
        flash("Os baralhos selecionados não têm cards.", "warning")
        return redirect(url_for("desafio"))

    # Embaralha e limita questões
    random.shuffle(todas_as_perguntas)
    if max_questoes > 0:
        questoes = todas_as_perguntas[:max_questoes]
    else:
        questoes = todas_as_perguntas

    # Salva na sessão
    session["desafio"] = {
        "cards": questoes,
        "tempo_por_questao": tempo_por_questao,
        "questao_atual": 0,
        "respostas": [],
        "inicio": agora_timestamp()
    }

    # Marca início para medir resposta relâmpago
    session['desafio_started_at'] = agora_timestamp()
    session['ultima_pergunta_ts'] = agora_timestamp()
    return render_template("executar_desafio.html", desafio=session["desafio"])


@app.route("/responder_desafio", methods=["POST"])
@login_required
def responder_desafio():
    data = request.get_json()
    desafio = session.get("desafio")

    if not desafio:
        return jsonify({"error": "Nenhum desafio ativo"}), 400

    card_id = data.get("card_id")
    resposta_usuario = data.get("resposta", "").strip()

    # Encontra o card atual
    card_atual = next((c for c in desafio["cards"] if c["id"] == card_id), None)
    if not card_atual:
        return jsonify({"error": "Card não encontrado"}), 400

    # Verifica se acertou
    resposta_correta = card_atual["verso"].lower().strip()
    resposta_user = resposta_usuario.lower().strip()
    acertou = resposta_user == resposta_correta or (resposta_user in resposta_correta and len(resposta_user) > 2)

    # Medir tempo de resposta
    try:
        agora = agora_timestamp()
        pergunta_ts = session.get('ultima_pergunta_ts', agora)
        elapsed = agora - pergunta_ts
        session['ultima_pergunta_ts'] = agora  # para próxima
        if elapsed <= 2 and acertou:
            from achievements import increment_stat, award_if_eligible
            from feed import registrar_atividade
            increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'fast_answers', 1)
            award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"]) 
    except Exception:
        pass

    # Log leve de estatísticas do estudo
    try:
        stats = g.user.setdefault('stats', {})
        # Histórico de respostas
        h = stats.setdefault('study_history', [])
        h.append({
            'ts': agora_timestamp(),
            'card_id': card_id,
            'acertou': bool(acertou)
        })
        # Padrões de erro simples por tamanho de resposta
        if not acertou:
            patt = stats.setdefault('error_patterns', {})
            key = str(min(50, max(1, len(resposta_user))))
            patt[key] = patt.get(key, 0) + 1
        salvar_dados(USERS_PATH, usuarios)
    except Exception:
        pass

    return jsonify({
        "acertou": acertou,
        "resposta_correta": card_atual["verso"]
    })



@app.route("/finalizar_desafio", methods=["POST"])
@login_required
def finalizar_desafio():
    if request.is_json:
        data = request.get_json()
        acertos = int(data.get("acertos", 0))
        erros = int(data.get("erros", 0))
        pontos = int(data.get("pontos", 0))
        respostas = data.get("respostas", [])
    else:
        acertos = int(request.form.get("acertos", 0))
        erros = int(request.form.get("erros", 0))
        pontos = int(request.form.get("pontos", 0))
        respostas = []

    # Atualiza pontos do usuário
    g.user["points"] = g.user.get("points", 0) + pontos
    salvar_dados(USERS_PATH, usuarios)

    total = acertos + erros
    porcentagem = round((acertos / total) * 100) if total > 0 else 0

    resultado = {
        "acertos": acertos,
        "erros": erros,
        "porcentagem": porcentagem,
        "pontos_ganhos": pontos,
        "respostas": respostas
    }
    session.pop("desafio", None)
    try:
        from feed import registrar_atividade
        registrar_atividade('desafio', g.user["id"], f"Finalizou um desafio: {acertos} acertos, {erros} erros, {pontos} pontos")
    except Exception:
        pass
    # Conquistas relacionadas a desafio/pontos
    try:
        from achievements import increment_stat, award_if_eligible
        increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'quizzes_finished', 1)
        increment_stat(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), g.user["id"], 'points_gained', max(pontos, 0))
        award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"])
    except Exception:
        pass
    return render_template("resultado_desafio.html", resultado=resultado)


@app.route("/resultado_desafio", methods=["GET"])
@login_required
def resultado_desafio():
    resultado = session.get("resultado_desafio")
    if not resultado:
        flash("Nenhum resultado disponível.", "warning")
        return redirect(url_for("desafio"))
    session.pop("resultado_desafio", None)
    return render_template("resultado_desafio.html", resultado=resultado)


@app.route("/cancelar_desafio", methods=["POST"])
@login_required
def cancelar_desafio():
    session.pop("desafio", None)
    flash("Desafio cancelado.", "info")
    return redirect(url_for("desafio"))


# --- Perfil ---
@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        frase_pessoal = request.form.get("frase_pessoal", "").strip()
        avatar_file = request.files.get("avatar")

        if nome:
            g.user["nome"] = nome
        if data_nascimento:
            g.user["data_nascimento"] = data_nascimento
        if frase_pessoal:
            g.user["frase_pessoal"] = frase_pessoal[:100]

        if avatar_file and avatar_file.filename:
            if allowed_file(avatar_file.filename):
                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                filename = f"avatar_{g.user['id']}_{int(time.time())}.{ext}"
                path = os.path.join(UPLOAD_FOLDER, filename)
                avatar_file.save(path)
                g.user["avatar"] = f"uploads/{filename}"
            else:
                flash("Formato de imagem não suportado.", "danger")
                return redirect(url_for("perfil"))

        salvar_dados(USERS_PATH, usuarios)
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil"))

    user_baralhos = baralhos.get(g.user["id"], {})
    def data_formatada(timestamp):
        if not timestamp:
            return "Data não disponível"
        try:
            return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")
        except:
            return "Data inválida"
    # Injeta mapa de conquistas após import disponível
    from achievements import ACHIEVEMENTS as _ACH
    ACHIEVEMENTS_MAP = { cfg['name']: { 'desc': cfg['desc'], 'category': cfg['category'], 'difficulty': cfg['difficulty'] } for cfg in _ACH.values() }
    return render_template(
        "perfil.html",
        baralhos=user_baralhos,
        usuario=g.user,
        data_formatada=data_formatada,
        ACHIEVEMENTS_MAP=ACHIEVEMENTS_MAP
    )


# --- Rota de Heartbeat ---

# --- Remover membro de baralho compartilhado ---
@app.route("/remover_membro/<baralho_id>/<member_id>", methods=["POST"])
@login_required
def remover_membro(baralho_id, member_id):
    if baralho_id not in shared_decks:
        flash("Baralho compartilhado não encontrado.", "danger")
        return redirect(url_for("home"))
    deck = shared_decks[baralho_id]
    if deck.get("owner") != g.user["id"]:
        flash("Apenas o dono pode remover membros.", "danger")
        return redirect(url_for("gerenciar_baralho", baralho_id=baralho_id))
    if "members" in deck and member_id in deck["members"]:
        deck["members"].remove(member_id)
        if "permissoes" in deck and member_id in deck["permissoes"]:
            del deck["permissoes"][member_id]
        salvar_dados(SHARED_DECKS_PATH, shared_decks)
        flash("Membro removido com sucesso!", "success")
    else:
        flash("Membro não encontrado neste baralho.", "warning")
    return redirect(url_for("gerenciar_baralho", baralho_id=baralho_id))

# --- API REST: Atualizar Permissões de Colaboradores ---
from flask import abort

@app.route("/api/baralho/<baralho_id>/permissoes/<member_id>", methods=["POST"])
@login_required
def api_atualizar_permissoes(baralho_id, member_id):
    if baralho_id not in shared_decks:
        return jsonify({"success": False, "error": "Baralho não encontrado."}), 404
    deck = shared_decks[baralho_id]
    if deck.get("owner") != g.user["id"]:
        return jsonify({"success": False, "error": "Apenas o dono pode alterar permissões."}), 403
    data = request.get_json(force=True)
    if "permissoes" not in deck:
        deck["permissoes"] = {}
    rank = data.get("rank")
    if rank == "colider":
        deck["permissoes"][member_id] = {"ler": True, "criar": True, "deletar": True}
    elif rank == "visitante":
        deck["permissoes"][member_id] = {"ler": True, "criar": False, "deletar": False}
    else:
        return jsonify({"success": False, "error": "Rank inválido."}), 400
    salvar_dados(SHARED_DECKS_PATH, shared_decks)
    return jsonify({"success": True, "msg": "Permissões atualizadas com sucesso!"})
@app.route("/heartbeat", methods=["POST"])
@login_required
def heartbeat():
    g.user["last_seen"] = agora_timestamp()
    salvar_dados(USERS_PATH, usuarios)
    # Conquista de madrugada e congelado
    try:
        from achievements import set_stat, award_if_eligible
        from datetime import datetime
        now = datetime.now()
        if 2 <= now.hour < 4:
            stats = g.user.setdefault('stats', {})
            stats['late_night_visits'] = stats.get('late_night_visits', 0) + 1
            salvar_dados(USERS_PATH, usuarios)
        # Inatividade 7 dias
        last_seen = g.user.get('last_seen', 0)
        prev_seen = g.user.get('prev_seen', last_seen)
        g.user['prev_seen'] = last_seen
        if prev_seen and (agora_timestamp() - prev_seen) >= 7*24*3600:
            stats = g.user.setdefault('stats', {})
            stats['inactive_7_days'] = 1
            salvar_dados(USERS_PATH, usuarios)
        from feed import registrar_atividade
        award_if_eligible(usuarios, lambda: salvar_dados(USERS_PATH, usuarios), registrar_atividade, g.user["id"]) 
    except Exception:
        pass
    return jsonify({"status": "ok"})


# --- Execução ---

# Registro do filtro Jinja2 'datetime' no contexto final do app (robusto p/ epoch/ISO)
def datetime_filter(value, format='%d/%m/%Y %H:%M'):
    try:
        from datetime import datetime
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
app.jinja_env.filters['datetime'] = datetime_filter

# --- API: Flags de estudo (favoritos / difíceis) ---
@app.route('/api/card/favorite', methods=['POST'])
@login_required
def api_card_favorite():
    try:
        data = request.get_json(force=True)
        baralho_id = data.get('baralho_id')
        card_id = data.get('card_id')
        active = bool(data.get('active'))
        if not card_id:
            return jsonify({"success": False, "error": "card_id obrigatório"}), 400
        favs = g.user.setdefault('favorites', [])
        if active:
            if card_id not in favs:
                favs.append(card_id)
        else:
            if card_id in favs:
                favs.remove(card_id)
        salvar_dados(USERS_PATH, usuarios)
        try:
            from feed import registrar_atividade
            registrar_atividade('conquista', g.user['id'], f"Atualizou favoritos de estudo")
        except Exception:
            pass
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/card/hard', methods=['POST'])
@login_required
def api_card_hard():
    try:
        data = request.get_json(force=True)
        baralho_id = data.get('baralho_id')
        card_id = data.get('card_id')
        active = bool(data.get('active'))
        if not card_id:
            return jsonify({"success": False, "error": "card_id obrigatório"}), 400
        hards = g.user.setdefault('hard_cards', [])
        if active:
            if card_id not in hards:
                hards.append(card_id)
        else:
            if card_id in hards:
                hards.remove(card_id)
        salvar_dados(USERS_PATH, usuarios)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 FlashStudy iniciando...")
    print("📂 Dados serão salvos em:", DATA_DIR)
    print("🌐 Acesse: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
