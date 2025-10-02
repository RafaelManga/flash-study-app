#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar permissões de admin
"""

import json

# Carregar users.json
with open('data/users.json', 'r', encoding='utf-8') as f:
    usuarios = json.load(f)

print("=" * 60)
print("TESTE DE PERMISSÕES DE ADMINISTRADOR")
print("=" * 60)
print()

for user_id, user_data in usuarios.items():
    nome = user_data.get('nome', 'Sem nome')
    email = user_data.get('email', 'Sem email')
    is_admin = user_data.get('is_admin', False)
    
    status = "[ADMIN]" if is_admin else "[USER]"
    
    print(f"{status}")
    print(f"  ID: {user_id}")
    print(f"  Nome: {nome}")
    print(f"  Email: {email}")
    print(f"  is_admin: {is_admin}")
    print()

print("=" * 60)
print("VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)
