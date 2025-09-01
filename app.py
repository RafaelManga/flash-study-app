from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import carregar_dados, salvar_dados

app = Flask(__name__)
app.secret_key = "segredo123"  # troque por algo mais seguro

# Carregando dados
usuarios = carregar_dados("data/users.json", default={})
flashcards = carregar_dados("data/flashcards.json", default=[])


# ---------------------- ROTAS DE LOGIN ----------------------

@app.route("/")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", cards=flashcards, usuario=session["usuario"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        if email in usuarios and usuarios[email]["senha"] == senha:
            session["usuario"] = {
                "nome": usuarios[email]["nome"],
                "email": email
            }
            return redirect(url_for("home"))
        else:
            return render_template("login.html", erro="Email ou senha inválidos.")

    mensagem = request.args.get("mensagem")
    return render_template("login.html", mensagem=mensagem)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        if email in usuarios:
            return render_template("register.html", erro="Esse email já está cadastrado.")

        usuarios[email] = {"nome": nome, "senha": senha}
        salvar_dados("data/users.json", usuarios)
        return redirect(url_for("login", mensagem="Cadastro concluído com sucesso!"))

    return render_template("register.html")


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        if email in usuarios and usuarios[email]["nome"] == nome:
            usuarios[email]["senha"] = senha
            salvar_dados("data/users.json", usuarios)
            return redirect(url_for("login", mensagem="Senha alterada com sucesso!"))
        else:
            return render_template("reset_password.html", erro="Email ou nome inválido.")

    return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# ---------------------- ROTAS DE FLASHCARDS ----------------------

@app.route("/criar", methods=["GET", "POST"])
def criar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        frente = request.form["frente"]
        verso = request.form["verso"]
        flashcards.append({"frente": frente, "verso": verso})
        salvar_dados("data/flashcards.json", flashcards)
        return redirect(url_for("home"))

    return render_template("criar.html")


@app.route("/estudar")
def estudar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("estudar.html", cards=flashcards)


if __name__ == "__main__":
    app.run(debug=True)
