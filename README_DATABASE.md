# FlashStudy - Migração para PostgreSQL

## 🚀 Instalação e Configuração

### Pré-requisitos

1. **Python 3.8+**
2. **PostgreSQL 12+**
3. **pip** (gerenciador de pacotes Python)

### Passo 1: Instalar PostgreSQL

#### Windows
1. Baixe o instalador em: https://www.postgresql.org/download/windows/
2. Execute o instalador e siga as instruções
3. Anote a senha do usuário `postgres` que você definiu

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Passo 2: Configurar o Banco de Dados

Execute o script de configuração automática:

```bash
python setup_database.py
```

Este script irá:
- Verificar se o PostgreSQL está instalado
- Instalar as dependências Python necessárias
- Criar o usuário e banco de dados
- Criar todas as tabelas necessárias

### Passo 3: Migrar Dados Existentes (Opcional)

Se você já tem dados nos arquivos JSON, migre-os para o banco:

```bash
python migrate_data.py
```

### Passo 4: Executar a Aplicação

```bash
python app_db.py
```

A aplicação estará disponível em: http://localhost:5000

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### `users`
- Armazena informações dos usuários
- Campos: id, nome, email, senha, avatar, points, etc.

#### `baralhos`
- Armazena baralhos de flashcards
- Campos: id, nome, cor, user_id, is_shared, etc.

#### `cards`
- Armazena cards individuais
- Campos: id, frente, verso, baralho_id, etc.

#### `amizades`
- Gerencia relacionamentos de amizade
- Campos: user1_id, user2_id, status, data_solicitacao, etc.

#### `competicoes`
- Gerencia competições entre amigos
- Campos: user1_id, user2_id, baralho_id, status, pontuacao1, pontuacao2, etc.

#### `sessoes_estudo`
- Registra sessões de estudo
- Campos: user_id, baralho_id, acertos, erros, pontos_ganhos, etc.

#### `badges`
- Define badges disponíveis
- Campos: id, nome, descricao, icone, categoria, raridade, requisitos

#### `user_badges`
- Relaciona usuários com badges conquistados
- Campos: user_id, badge_id, data_conquista

#### `atividades`
- Feed de atividades dos usuários
- Campos: user_id, tipo, descricao, data, dados_extras

#### `notificacoes`
- Sistema de notificações
- Campos: user_id, tipo, titulo, mensagem, lida, data

## 🔧 Configurações

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=postgresql://flashstudy:flashstudy123@localhost:5432/flashstudy_db
GEMINI_API_KEY=sua_chave_do_gemini_aqui
```

### Configurações do Banco

- **Host**: localhost
- **Porta**: 5432
- **Banco**: flashstudy_db
- **Usuário**: flashstudy
- **Senha**: flashstudy123

## 🆚 Diferenças entre Versões

### Versão JSON (app.py)
- Dados armazenados em arquivos JSON
- Mais simples para desenvolvimento
- Limitado para produção

### Versão PostgreSQL (app_db.py)
- Dados armazenados em banco relacional
- Melhor performance e escalabilidade
- Suporte a transações e integridade referencial
- Backup e recuperação mais robustos

## 🐛 Solução de Problemas

### Erro de Conexão com PostgreSQL

1. Verifique se o PostgreSQL está rodando:
   ```bash
   # Windows
   services.msc
   
   # macOS/Linux
   brew services list | grep postgresql
   sudo systemctl status postgresql
   ```

2. Verifique se as credenciais estão corretas no arquivo `.env`

3. Teste a conexão manualmente:
   ```bash
   psql -h localhost -U flashstudy -d flashstudy_db
   ```

### Erro de Dependências

1. Instale as dependências:
   ```bash
   pip install -r requirements_db.txt
   ```

2. Se houver conflitos, use um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   pip install -r requirements_db.txt
   ```

### Erro de Migração

1. Verifique se os arquivos JSON existem na pasta `data/`
2. Verifique se o banco de dados está acessível
3. Execute a migração novamente:
   ```bash
   python migrate_data.py
   ```

## 📈 Melhorias Implementadas

### Sistema de Competições
- ✅ Correção do problema de aceitar/recusar desafios
- ✅ Ranking funcional com dados reais
- ✅ Notificações de badges ao aceitar competições

### Banco de Dados
- ✅ Migração completa de JSON para PostgreSQL
- ✅ Modelos SQLAlchemy bem estruturados
- ✅ Relacionamentos e integridade referencial
- ✅ Sistema de migração de dados

### Performance
- ✅ Consultas otimizadas com índices
- ✅ Lazy loading para relacionamentos
- ✅ Transações para operações críticas

### Escalabilidade
- ✅ Suporte a múltiplos usuários simultâneos
- ✅ Backup e recuperação de dados
- ✅ Monitoramento de performance

## 🚀 Próximos Passos

1. **Configurar backup automático** do banco de dados
2. **Implementar cache** com Redis para melhor performance
3. **Adicionar logs** de auditoria
4. **Configurar monitoramento** de performance
5. **Implementar testes automatizados**

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs da aplicação
2. Consulte a documentação do PostgreSQL
3. Verifique se todas as dependências estão instaladas
4. Execute os scripts de configuração novamente

---

**Nota**: Esta versão com PostgreSQL é recomendada para uso em produção, oferecendo melhor performance, segurança e escalabilidade comparada à versão com arquivos JSON.



