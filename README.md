# FlashStudy

Plataforma de estudos com flashcards, desafios e colaboração entre usuários. Desenvolvida em Flask (Python), com interface moderna e recursos de IA para geração de cards.

## Funcionalidades
- Criação e gerenciamento de baralhos de flashcards
- Compartilhamento de baralhos com outros usuários
- Sistema de amigos e convites
- Modo desafio (quiz)
- Geração de cards com IA (Google Gemini)
- Interface responsiva e moderna

## Como rodar o projeto

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repo>
   cd teste
   ```
2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure as variáveis de ambiente:**
   - Crie um arquivo `.env` (opcional) ou defina as variáveis no sistema:
     - `SECRET_KEY` (chave secreta Flask)
     - `GEMINI_API_KEY` (chave da API Google Gemini)

5. **Execute o projeto:**
   ```bash
   python app.py
   ```
6. **Acesse no navegador:**
   - http://localhost:5000

## Estrutura principal
- `app.py` — Backend Flask e rotas principais
- `templates/` — Templates HTML (Jinja2)
- `static/` — Arquivos estáticos (CSS, JS, imagens)
- `data/` — Dados persistentes em JSON

## Observações
- O projeto não utiliza banco de dados relacional, todos os dados são salvos em arquivos JSON.
- Para usar a IA, é necessário configurar a chave da API Gemini.
- O sistema é voltado para fins educacionais e pode ser expandido facilmente.

---

Dúvidas ou sugestões? Abra uma issue ou entre em contato!
