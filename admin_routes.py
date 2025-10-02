#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas Administrativas do FlashStudy
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, g, send_file
from functools import wraps
import csv
import io
from datetime import datetime, timedelta

# Estas funções serão importadas pelo app.py
def init_admin_routes(app, usuarios, relatos, admin_logs, plataforma_config, baralhos, shared_decks,
                      agora_timestamp, salvar_dados, registrar_log_admin, usuario_online,
                      RELATOS_PATH, ADMIN_LOGS_PATH, PLATAFORMA_CONFIG_PATH, USERS_PATH,
                      UPLOAD_FOLDER, allowed_file):
    
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            if "user_id" not in session:
                flash("Você precisa fazer login para acessar esta página.", "warning")
                return redirect(url_for("login"))
            
            user_id = session["user_id"]
            if user_id not in usuarios:
                session.clear()
                flash("Sessão inválida. Faça login novamente.", "danger")
                return redirect(url_for("login"))
            
            user = usuarios[user_id]
            if not user.get("is_admin", False):
                flash("Acesso negado. Esta área é restrita a administradores.", "danger")
                return redirect(url_for("home"))
            
            g.user = user
            return f(*args, **kwargs)
        return decorated_function
    
    # ======================
    # ROTAS DE RELATOS
    # ======================
    
    @app.route("/relatar_problema", methods=["GET", "POST"])
    def relatar_problema():
        from flask import session
        if "user_id" not in session:
            flash("Você precisa fazer login.", "warning")
            return redirect(url_for("login"))
        
        user_id = session["user_id"]
        g.user = usuarios[user_id]
        
        if request.method == "POST":
            categoria = request.form.get("categoria", "").strip()
            mensagem = request.form.get("mensagem", "").strip()
            
            if not categoria or not mensagem or len(mensagem) < 20:
                flash("Preencha todos os campos corretamente (mínimo 20 caracteres).", "warning")
                return redirect(url_for("relatar_problema"))
            
            # Processa imagem se houver
            imagem_path = ""
            if 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename and allowed_file(file.filename):
                    import os
                    from uuid import uuid4
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"relato_{uuid4().hex[:8]}.{ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    imagem_path = f"uploads/{filename}"
            
            # Cria o relato
            relato_id = f"REL{int(agora_timestamp())}"
            relatos[relato_id] = {
                "id": relato_id,
                "usuario_id": user_id,
                "usuario_nome": g.user["nome"],
                "usuario_email": g.user["email"],
                "categoria": categoria,
                "mensagem": mensagem,
                "imagem": imagem_path,
                "status": "pendente",
                "data": agora_timestamp(),
                "resposta_admin": ""
            }
            salvar_dados(RELATOS_PATH, relatos)
            
            flash("Relato enviado com sucesso! Nossa equipe irá analisá-lo em breve.", "success")
            return redirect(url_for("relatar_problema"))
        
        # GET - buscar relatos do usuário
        meus_relatos = [r for r in relatos.values() if r.get("usuario_id") == user_id]
        meus_relatos.sort(key=lambda x: x.get("data", 0), reverse=True)
        
        return render_template("relatar_problema.html", meus_relatos=meus_relatos)
    
    # ======================
    # PAINEL ADMINISTRATIVO
    # ======================
    
    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        # Estatísticas gerais
        total_usuarios = len(usuarios)
        total_baralhos = sum(len(b) for b in baralhos.values())
        total_relatos = len([r for r in relatos.values() if r.get("status") == "pendente"])
        usuarios_online = len([u for u in usuarios.values() if usuario_online(u["id"])])
        
        # Atividades recentes (últimos 20 logs)
        atividades_recentes = sorted(admin_logs, key=lambda x: x.get("data", 0), reverse=True)[:20]
        
        return render_template("admin_dashboard.html",
                             total_usuarios=total_usuarios,
                             total_baralhos=total_baralhos,
                             total_relatos=total_relatos,
                             usuarios_online=usuarios_online,
                             atividades_recentes=atividades_recentes)
    
    @app.route("/admin/relatos")
    @admin_required
    def admin_relatos():
        categoria_filtro = request.args.get("categoria", "")
        status_filtro = request.args.get("status", "")
        
        relatos_lista = list(relatos.values())
        
        # Aplica filtros
        if categoria_filtro:
            relatos_lista = [r for r in relatos_lista if r.get("categoria") == categoria_filtro]
        if status_filtro:
            relatos_lista = [r for r in relatos_lista if r.get("status") == status_filtro]
        
        # Ordena por data (mais recentes primeiro)
        relatos_lista.sort(key=lambda x: x.get("data", 0), reverse=True)
        
        return render_template("admin_relatos.html", relatos=relatos_lista)
    
    @app.route("/admin/relatos/<relato_id>/responder", methods=["POST"])
    @admin_required
    def admin_responder_relato(relato_id):
        if relato_id not in relatos:
            flash("Relato não encontrado.", "danger")
            return redirect(url_for("admin_relatos"))
        
        resposta = request.form.get("resposta", "").strip()
        if not resposta:
            flash("A resposta não pode estar vazia.", "warning")
            return redirect(url_for("admin_relatos"))
        
        relatos[relato_id]["resposta_admin"] = resposta
        relatos[relato_id]["status"] = "respondido"
        salvar_dados(RELATOS_PATH, relatos)
        
        registrar_log_admin(g.user["id"], "resposta", 
                          f"Respondeu ao relato {relato_id}",
                          f"Categoria: {relatos[relato_id].get('categoria')}")
        
        flash("Resposta enviada com sucesso!", "success")
        return redirect(url_for("admin_relatos"))
    
    @app.route("/admin/relatos/<relato_id>/status", methods=["POST"])
    @admin_required
    def admin_atualizar_status_relato(relato_id):
        if relato_id not in relatos:
            flash("Relato não encontrado.", "danger")
            return redirect(url_for("admin_relatos"))
        
        novo_status = request.form.get("status", "pendente")
        relatos[relato_id]["status"] = novo_status
        salvar_dados(RELATOS_PATH, relatos)
        
        registrar_log_admin(g.user["id"], "edicao",
                          f"Atualizou status do relato {relato_id} para '{novo_status}'")
        
        flash(f"Status atualizado para '{novo_status}'!", "success")
        return redirect(url_for("admin_relatos"))
    
    # ======================
    # GESTÃO DE USUÁRIOS
    # ======================
    
    @app.route("/admin/usuarios")
    @admin_required
    def admin_usuarios():
        busca = request.args.get("busca", "").lower()
        
        usuarios_lista = list(usuarios.values())
        
        if busca:
            usuarios_lista = [u for u in usuarios_lista 
                            if busca in u.get("nome", "").lower() 
                            or busca in u.get("email", "").lower() 
                            or busca in u.get("id", "").lower()]
        
        usuarios_lista.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
        
        return render_template("admin_usuarios.html", usuarios_lista=usuarios_lista)
    
    @app.route("/admin/usuarios/<user_id>/promover", methods=["POST"])
    @admin_required
    def admin_promover_admin(user_id):
        if user_id not in usuarios:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("admin_usuarios"))
        
        usuarios[user_id]["is_admin"] = True
        salvar_dados(USERS_PATH, usuarios)
        
        registrar_log_admin(g.user["id"], "promover",
                          f"Promoveu {usuarios[user_id]['nome']} para administrador")
        
        flash(f"{usuarios[user_id]['nome']} agora é administrador!", "success")
        return redirect(url_for("admin_usuarios"))
    
    @app.route("/admin/usuarios/<user_id>/remover_admin", methods=["POST"])
    @admin_required
    def admin_remover_admin(user_id):
        if user_id not in usuarios:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("admin_usuarios"))
        
        usuarios[user_id]["is_admin"] = False
        salvar_dados(USERS_PATH, usuarios)
        
        registrar_log_admin(g.user["id"], "remover",
                          f"Removeu privilégios de admin de {usuarios[user_id]['nome']}")
        
        flash(f"Privilégios de admin removidos de {usuarios[user_id]['nome']}.", "success")
        return redirect(url_for("admin_usuarios"))
    
    @app.route("/admin/usuarios/<user_id>/suspender", methods=["POST"])
    @admin_required
    def admin_suspender_usuario(user_id):
        if user_id not in usuarios:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("admin_usuarios"))
        
        usuarios[user_id]["is_suspended"] = True
        salvar_dados(USERS_PATH, usuarios)
        
        registrar_log_admin(g.user["id"], "suspensao",
                          f"Suspendeu a conta de {usuarios[user_id]['nome']}")
        
        flash(f"Conta de {usuarios[user_id]['nome']} suspensa.", "warning")
        return redirect(url_for("admin_usuarios"))
    
    @app.route("/admin/usuarios/<user_id>/reativar", methods=["POST"])
    @admin_required
    def admin_reativar_usuario(user_id):
        if user_id not in usuarios:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("admin_usuarios"))
        
        usuarios[user_id]["is_suspended"] = False
        salvar_dados(USERS_PATH, usuarios)
        
        registrar_log_admin(g.user["id"], "reativacao",
                          f"Reativou a conta de {usuarios[user_id]['nome']}")
        
        flash(f"Conta de {usuarios[user_id]['nome']} reativada.", "success")
        return redirect(url_for("admin_usuarios"))
    
    @app.route("/admin/usuarios/<user_id>/resetar", methods=["POST"])
    @admin_required
    def admin_resetar_usuario():
        user_id = request.view_args['user_id']
        if user_id not in usuarios:
            return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
        
        usuarios[user_id]["points"] = 0
        usuarios[user_id]["conquistas"] = []
        usuarios[user_id]["badges"] = []
        salvar_dados(USERS_PATH, usuarios)
        
        registrar_log_admin(g.user["id"], "reset",
                          f"Resetou o progresso de {usuarios[user_id]['nome']}")
        
        return jsonify({"success": True})
    
    # ======================
    # DESIGN DA PLATAFORMA
    # ======================
    
    @app.route("/admin/design", methods=["GET", "POST"])
    @admin_required
    def admin_design():
        if request.method == "POST":
            # Atualiza cores
            plataforma_config["tema"]["cor_primaria"] = request.form.get("cor_primaria", "#3b82f6")
            plataforma_config["tema"]["cor_secundaria"] = request.form.get("cor_secundaria", "#8b5cf6")
            plataforma_config["tema"]["fonte_principal"] = request.form.get("fonte_principal", "Inter, system-ui, sans-serif")
            
            # Processa banner_home
            if 'banner_home' in request.files:
                file = request.files['banner_home']
                if file and file.filename and allowed_file(file.filename):
                    import os
                    from uuid import uuid4
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"banner_{uuid4().hex[:8]}.{ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    plataforma_config["tema"]["banner_home"] = f"uploads/{filename}"
            
            # Processa logo
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename and allowed_file(file.filename):
                    import os
                    from uuid import uuid4
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"logo_{uuid4().hex[:8]}.{ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    plataforma_config["tema"]["logo"] = f"uploads/{filename}"
            
            salvar_dados(PLATAFORMA_CONFIG_PATH, plataforma_config)
            
            registrar_log_admin(g.user["id"], "design",
                              "Atualizou o design da plataforma")
            
            flash("Design da plataforma atualizado com sucesso!", "success")
            return redirect(url_for("admin_design"))
        
        return render_template("admin_design.html", config=plataforma_config)
    
    # ======================
    # EVENTOS E CAMPANHAS
    # ======================
    
    @app.route("/admin/eventos", methods=["GET", "POST"])
    @admin_required
    def admin_eventos():
        if request.method == "POST":
            from uuid import uuid4
            evento = {
                "id": str(uuid4()),
                "titulo": request.form.get("titulo", ""),
                "descricao": request.form.get("descricao", ""),
                "tipo": request.form.get("tipo", "desafio"),
                "data_inicio": request.form.get("data_inicio", ""),
                "data_fim": request.form.get("data_fim", ""),
                "recompensa": int(request.form.get("recompensa", 100)),
                "ativo": True,
                "criado_em": agora_timestamp()
            }
            
            plataforma_config["eventos"].append(evento)
            salvar_dados(PLATAFORMA_CONFIG_PATH, plataforma_config)
            
            registrar_log_admin(g.user["id"], "criacao",
                              f"Criou evento: {evento['titulo']}")
            
            flash("Evento criado com sucesso!", "success")
            return redirect(url_for("admin_eventos"))
        
        return render_template("admin_eventos.html", eventos=plataforma_config["eventos"])
    
    @app.route("/admin/eventos/<evento_id>/excluir", methods=["POST"])
    @admin_required
    def admin_excluir_evento(evento_id):
        plataforma_config["eventos"] = [e for e in plataforma_config["eventos"] if e.get("id") != evento_id]
        salvar_dados(PLATAFORMA_CONFIG_PATH, plataforma_config)
        
        registrar_log_admin(g.user["id"], "exclusao",
                          f"Excluiu evento {evento_id}")
        
        flash("Evento excluído!", "success")
        return redirect(url_for("admin_eventos"))
    
    # ======================
    # NOTIFICAÇÕES
    # ======================
    
    @app.route("/admin/notificacoes", methods=["GET", "POST"])
    @admin_required
    def admin_notificacoes():
        if request.method == "POST":
            from uuid import uuid4
            notificacao = {
                "id": str(uuid4()),
                "titulo": request.form.get("titulo", ""),
                "mensagem": request.form.get("mensagem", ""),
                "tipo": request.form.get("tipo", "info"),
                "destinatarios": request.form.get("destinatarios", "todos"),
                "destinatarios_texto": {
                    "todos": "Todos os usuários",
                    "admins": "Apenas administradores",
                    "ativos": "Usuários ativos",
                    "inativos": "Usuários inativos"
                }.get(request.form.get("destinatarios", "todos"), "Todos"),
                "link": request.form.get("link", ""),
                "data": agora_timestamp()
            }
            
            plataforma_config["notificacoes_globais"].append(notificacao)
            salvar_dados(PLATAFORMA_CONFIG_PATH, plataforma_config)
            
            registrar_log_admin(g.user["id"], "notificacao",
                              f"Enviou notificação: {notificacao['titulo']}")
            
            flash("Notificação enviada com sucesso!", "success")
            return redirect(url_for("admin_notificacoes"))
        
        # Estatísticas
        total_notificacoes = len(plataforma_config["notificacoes_globais"])
        notificacoes_mes = len([n for n in plataforma_config["notificacoes_globais"] 
                                if n.get("data", 0) > agora_timestamp() - (30 * 24 * 3600)])
        
        return render_template("admin_notificacoes.html",
                             notificacoes=plataforma_config["notificacoes_globais"],
                             total_notificacoes=total_notificacoes,
                             notificacoes_mes=notificacoes_mes)
    
    # ======================
    # LOGS DE AUDITORIA
    # ======================
    
    @app.route("/admin/logs")
    @admin_required
    def admin_logs():
        admin_filtro = request.args.get("admin", "")
        acao_filtro = request.args.get("acao", "")
        
        logs_lista = list(admin_logs)
        
        if admin_filtro:
            logs_lista = [l for l in logs_lista if l.get("admin_id") == admin_filtro]
        if acao_filtro:
            logs_lista = [l for l in logs_lista if acao_filtro in l.get("tipo", "")]
        
        logs_lista.sort(key=lambda x: x.get("data", 0), reverse=True)
        
        # Lista de admins para filtro
        admins = [u for u in usuarios.values() if u.get("is_admin")]
        
        # Estatísticas
        total_logs = len(admin_logs)
        hoje_ts = agora_timestamp() - (agora_timestamp() % 86400)
        logs_hoje = len([l for l in admin_logs if l.get("data", 0) >= hoje_ts])
        logs_semana = len([l for l in admin_logs if l.get("data", 0) >= agora_timestamp() - (7 * 86400)])
        total_admins = len(admins)
        
        return render_template("admin_logs.html",
                             logs=logs_lista,
                             admins=admins,
                             total_logs=total_logs,
                             logs_hoje=logs_hoje,
                             logs_semana=logs_semana,
                             total_admins=total_admins)
    
    @app.route("/admin/logs/exportar", methods=["POST"])
    @admin_required
    def admin_exportar_logs():
        # Cria CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(["ID", "Admin", "Tipo", "Descrição", "Data"])
        
        # Dados
        for log in admin_logs:
            writer.writerow([
                log.get("id", ""),
                log.get("admin_nome", ""),
                log.get("tipo", ""),
                log.get("descricao", ""),
                datetime.fromtimestamp(log.get("data", 0)).strftime("%d/%m/%Y %H:%M:%S")
            ])
        
        # Prepara para download
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'logs_admin_{datetime.now().strftime("%Y%m%d")}.csv'
        )
