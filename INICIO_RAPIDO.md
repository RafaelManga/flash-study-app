# 🚀 Guia de Início Rápido - FlashStudy Admin

## 📦 Instalação

### 1. Certifique-se de que todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

### 2. Estrutura de arquivos verificada:
```
flash-study-app/
├── app.py                          # Aplicação principal
├── admin_routes.py                 # Rotas administrativas (NOVO)
├── feed.py                         # Sistema de feed social
├── utils.py                        # Utilitários
├── requirements.txt
├── data/
│   ├── users.json
│   ├── baralhos.json
│   ├── relatos.json               # NOVO
│   ├── admin_logs.json            # NOVO
│   └── plataforma_config.json     # NOVO
├── templates/
│   ├── admin_dashboard.html       # NOVO
│   ├── admin_relatos.html         # NOVO
│   ├── admin_usuarios.html        # NOVO
│   ├── admin_design.html          # NOVO
│   ├── admin_eventos.html         # NOVO
│   ├── admin_notificacoes.html    # NOVO
│   ├── admin_logs.html            # NOVO
│   ├── relatar_problema.html      # NOVO
│   └── ... (outros templates existentes)
└── static/
    └── uploads/                    # Para imagens de relatos e banners
```

---

## 🎬 Iniciando o Sistema

### 1. Execute o servidor:
```bash
python app.py
```

### 2. Acesse no navegador:
```
http://localhost:5000
```

---

## 👤 Criando o Primeiro Administrador

### Método Manual (Recomendado para o primeiro admin):

1. **Registre uma conta normalmente** através da interface web
2. **Anote o ID do usuário** (aparece no perfil)
3. **Edite o arquivo** `data/users.json`:

```json
{
  "USRXYZ1234": {
    "id": "USRXYZ1234",
    "nome": "Admin Principal",
    "email": "admin@flashstudy.com",
    "is_admin": true,    // ← ADICIONE ESTA LINHA
    "senha": "...",
    "avatar": "",
    "points": 0,
    ...
  }
}
```

4. **Salve o arquivo** e faça login novamente
5. **Pronto!** O card "Painel Admin" aparecerá na Home

### Método Alternativo (Via Python):
```python
# No terminal Python ou no app.py
usuarios["USRXYZ1234"]["is_admin"] = True
salvar_dados(USERS_PATH, usuarios)
```

---

## 🎯 Fluxo de Uso

### Para Usuários Comuns:

#### Relatar um Problema:
```
Home → "Relatar Problema" → 
  1. Escolha a categoria (Bug/Sugestão/Dúvida/Feedback)
  2. Descreva (mín. 20 caracteres)
  3. Anexe imagem (opcional)
  4. Enviar
  
→ Acompanhe status e respostas no histórico
```

---

### Para Administradores:

#### Acesso ao Painel:
```
Login (conta admin) → Home → "Painel Admin" 🛡️
```

#### Estrutura do Painel:
```
Dashboard Principal
├── 📋 Gerenciar Relatos
│   ├── Ver todos os relatos
│   ├── Filtrar por categoria/status
│   ├── Responder relatos
│   └── Atualizar status
│
├── 👥 Gerenciar Usuários
│   ├── Buscar usuários
│   ├── Promover/Remover admin
│   ├── Suspender/Reativar contas
│   └── Resetar progresso
│
├── 🎨 Design da Plataforma
│   ├── Alterar cores (primária/secundária)
│   ├── Mudar fonte principal
│   ├── Upload de banner da home
│   └── Upload de logo
│
├── 🎉 Eventos e Campanhas
│   ├── Criar novos eventos
│   ├── Definir recompensas
│   └── Gerenciar eventos ativos
│
├── 📢 Notificações
│   ├── Enviar para todos/admins/ativos/inativos
│   ├── Escolher tipo (info/aviso/sucesso/urgente)
│   └── Adicionar link opcional
│
└── 📝 Logs de Auditoria
    ├── Ver todas as ações admin
    ├── Filtrar por admin/tipo
    └── Exportar para CSV
```

---

## 🔍 Exemplos Práticos

### Exemplo 1: Respondendo um Bug Report

```
1. Admin → Gerenciar Relatos
2. Filtrar: Categoria = "Bug", Status = "Pendente"
3. Encontrar o relato
4. Clicar "Responder"
5. Escrever: "Obrigado pelo relato! Identificamos o problema e já está sendo corrigido. Estará disponível na próxima atualização."
6. Enviar
7. Marcar como "Resolvido" ✅
```

### Exemplo 2: Promovendo um Usuário a Admin

```
1. Admin → Gerenciar Usuários
2. Buscar por nome/email: "João Silva"
3. Clicar "🛡️ Promover para Admin"
4. Confirmar
✅ João Silva agora tem acesso ao painel admin
```

### Exemplo 3: Personalizando o Design

```
1. Admin → Design da Plataforma
2. Cor Primária: #10b981 (verde)
3. Cor Secundária: #f59e0b (laranja)
4. Fonte: "Poppins"
5. Upload banner: "banner_natal_2024.png"
6. Salvar Alterações
✅ Plataforma atualizada com o novo visual
```

### Exemplo 4: Criando um Evento

```
1. Admin → Eventos e Campanhas
2. Preencher:
   - Título: "Desafio de Matemática de Dezembro"
   - Descrição: "Resolva 50 cards de matemática e ganhe pontos extras!"
   - Tipo: "Desafio Temático"
   - Data Início: 01/12/2024
   - Data Fim: 31/12/2024
   - Recompensa: 500 pontos
3. Criar Evento
✅ Evento ativo e visível para todos os usuários
```

### Exemplo 5: Enviando Notificação Global

```
1. Admin → Notificações
2. Destinatários: "Todos os usuários"
3. Tipo: "Sucesso ✅"
4. Título: "Nova Funcionalidade: Modo Escuro!"
5. Mensagem: "Agora você pode alternar entre modo claro e escuro. Experimente no seu perfil!"
6. Link: "/perfil"
7. Enviar Notificação
✅ Todos os usuários receberão a notificação
```

---

## 📊 Monitoramento

### Ver Estatísticas:
```
Dashboard → Cards com números em tempo real:
- Total de usuários: XX
- Baralhos criados: YY
- Relatos pendentes: ZZ
- Usuários online: WW
```

### Acompanhar Atividades:
```
Dashboard → Seção "Atividade Recente":
- Ver últimas 20 ações na plataforma
- Nome do usuário + ação realizada + data/hora
```

### Exportar Logs:
```
Admin → Logs de Auditoria → Botão "📥 Exportar CSV"
→ Baixa arquivo com todas as ações administrativas
```

---

## ⚠️ Avisos Importantes

### Segurança:
- ⚠️ Nunca compartilhe credenciais de admin
- ⚠️ Use senhas fortes
- ⚠️ Revise logs regularmente
- ⚠️ Suspenda contas suspeitas imediatamente

### Backup:
```bash
# Faça backup regular da pasta data/
cp -r data/ backup_$(date +%Y%m%d)/
```

### Ações Irreversíveis:
- ❌ Excluir eventos
- ❌ Resetar progresso de usuários
- ✅ Suspensão de contas (reversível)

---

## 🐛 Solução de Problemas

### Problema: "Acesso Negado" no Painel Admin
**Solução**: Verifique se `is_admin: true` está no seu usuário em `users.json`

### Problema: Relatos não aparecem
**Solução**: Verifique se o arquivo `data/relatos.json` existe e está formatado corretamente

### Problema: Erro ao salvar design
**Solução**: Verifique permissões da pasta `static/uploads/`

### Problema: Logs não registram
**Solução**: Verifique se `data/admin_logs.json` existe e é uma lista `[]`

---

## 📞 Suporte

### Logs de Erro:
- Verifique o console onde o servidor está rodando
- Erros aparecem com `❌` no terminal

### Testando Funcionalidades:
1. Use o ambiente de desenvolvimento (debug=True)
2. Teste cada funcionalidade individualmente
3. Verifique os arquivos JSON após cada ação

---

## ✅ Checklist de Verificação

Antes de usar em produção:

- [ ] Primeiro admin criado e testado
- [ ] Sistema de relatos funcionando
- [ ] Upload de imagens configurado
- [ ] Logs de auditoria registrando ações
- [ ] Backup automático configurado
- [ ] Senhas fortes em todas as contas admin
- [ ] Permissões de arquivos corretas
- [ ] HTTPS configurado (produção)

---

## 🎓 Próximos Passos

1. **Familiarize-se** com todas as áreas do painel admin
2. **Promova** outros administradores de confiança
3. **Configure** o design da plataforma
4. **Crie** eventos e campanhas para engajamento
5. **Monitore** relatos e responda rapidamente
6. **Revise** logs regularmente para segurança

---

**Dúvidas?** Verifique `MELHORIAS_IMPLEMENTADAS.md` para documentação completa!

🚀 **Bom uso do FlashStudy Admin!**
