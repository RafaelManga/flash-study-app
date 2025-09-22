#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração do banco de dados PostgreSQL
"""

import os
import subprocess
import sys
from database import db, init_db, Badge, User, Baralho, Card, Amizade, Competicao, SessaoEstudo, Atividade, Notificacao, ConviteBaralho, BaralhoMembro, UserBadge

def verificar_postgresql():
    """Verifica se o PostgreSQL está instalado e rodando"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL não encontrado")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL não está instalado ou não está no PATH")
        return False

def criar_usuario_e_banco():
    """Cria usuário e banco de dados para a aplicação"""
    print("🔄 Configurando banco de dados...")
    
    # Configurações do banco
    db_name = "flashstudy_db"
    db_user = "flashstudy"
    db_password = "flashstudy123"
    
    try:
        # Conecta como superusuário para criar usuário e banco
        conn_string = "postgresql://postgres@localhost:5432/postgres"
        
        # Cria usuário
        cmd_create_user = f"psql {conn_string} -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\""
        result = subprocess.run(cmd_create_user, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Usuário '{db_user}' criado com sucesso")
        else:
            if "already exists" in result.stderr:
                print(f"⚠️  Usuário '{db_user}' já existe")
            else:
                print(f"❌ Erro ao criar usuário: {result.stderr}")
                return False
        
        # Cria banco de dados
        cmd_create_db = f"psql {conn_string} -c \"CREATE DATABASE {db_name} OWNER {db_user};\""
        result = subprocess.run(cmd_create_db, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Banco de dados '{db_name}' criado com sucesso")
        else:
            if "already exists" in result.stderr:
                print(f"⚠️  Banco de dados '{db_name}' já existe")
            else:
                print(f"❌ Erro ao criar banco de dados: {result.stderr}")
                return False
        
        # Concede privilégios
        cmd_grant = f"psql {conn_string} -c \"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};\""
        result = subprocess.run(cmd_grant, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Privilégios concedidos ao usuário '{db_user}'")
        else:
            print(f"⚠️  Aviso ao conceder privilégios: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante configuração do banco: {e}")
        return False

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    print("🔄 Testando conexão com o banco de dados...")
    
    try:
        from app_db import app
        from sqlalchemy import text
        with app.app_context():
            # Tenta executar uma query simples
            result = db.session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ Conexão com banco de dados estabelecida com sucesso!")
                return True
            else:
                print("❌ Erro na conexão com banco de dados")
                return False
    except Exception as e:
        print(f"❌ Erro ao conectar com banco de dados: {e}")
        return False

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    print("🔄 Criando tabelas no banco de dados...")
    
    try:
        from app_db import app
        with app.app_context():
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("🔄 Instalando dependências...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_db.txt'], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def main():
    """Função principal de configuração"""
    print("🚀 Configurando FlashStudy com PostgreSQL...")
    print("=" * 60)
    
    # Verifica se PostgreSQL está instalado
    if not verificar_postgresql():
        print("\n📋 Para instalar o PostgreSQL:")
        print("   Windows: https://www.postgresql.org/download/windows/")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False
    
    # Instala dependências
    if not instalar_dependencias():
        return False
    
    # Cria usuário e banco
    if not criar_usuario_e_banco():
        return False
    
    # Testa conexão
    if not testar_conexao():
        return False
    
    # Cria tabelas
    if not criar_tabelas():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python migrate_data.py (para migrar dados existentes)")
    print("2. Execute: python app_db.py (para iniciar a aplicação)")
    print("\n🔧 Configurações do banco:")
    print("   Host: localhost")
    print("   Porta: 5432")
    print("   Banco: flashstudy_db")
    print("   Usuário: flashstudy")
    print("   Senha: flashstudy123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


