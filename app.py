from cs50 import SQL
from flask import Flask,render_template, request, session
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///dicionario.db")

@app.route("/", methods=["GET", "POST"])

def inicial():

    if not "user_id" in session:
        return render_template("login.html")


    id = session["user_id"]
    if id:
        id = id[0]['id']

    nome_usuario = db.execute("SELECT usuario from usuarios where id = ?", id)
    if nome_usuario:
        nome_usuario = nome_usuario[0]['usuario']



    if request.method == "GET":
        termos_e_descricoes = db.execute("SELECT termo, descricao_de_termo FROM usuarios WHERE usuario = ? AND termo IS NOT NULL AND descricao_de_termo IS NOT NULL ORDER BY termo ASC", nome_usuario)
        termos_e_descricoes_ordenados = sorted(termos_e_descricoes, key=lambda x: x['termo'])
        return render_template("inicial.html", termos_e_descricoes_ordenados=termos_e_descricoes_ordenados)

    else:
        novo_termo = request.form.get("novo_termo")
        nova_descricao = request.form.get("nova_descricao")

        db.execute("INSERT INTO usuarios (usuario, termo, descricao_de_termo) VALUES(?,?, ?)", nome_usuario, novo_termo, nova_descricao)

    ## termos = db.execute("SELECT termo FROM usuarios WHERE usuario = ?", nome_usuario)
    ## descricao_de_termos = db.execute("SELECT descricao_de_Termo FROM usuarios WHERE usuario = ?", nome_usuario)

        termos_e_descricoes = db.execute("SELECT termo, descricao_de_termo FROM usuarios WHERE usuario = ? AND termo IS NOT NULL AND descricao_de_termo IS NOT NULL ORDER BY termo ASC", nome_usuario)
        termos_e_descricoes_ordenados = sorted(termos_e_descricoes, key=lambda x: x['termo'])
        return render_template("inicial.html", termos_e_descricoes_ordenados=termos_e_descricoes_ordenados)

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "GET":
        return render_template("registro.html")
    else:
        usuario = request.form.get("username_registro")
        senha = request.form.get("password_registro")
        confirmar = request.form.get("confirmation")

        if not usuario or not senha or not confirmar:
            return render_template("registro.html", error="Todos os campos devem ser preenchidos.")
        if senha != confirmar:
            return render_template("registro.html", error="As senhas não coincidem.")

        db.execute("INSERT INTO usuarios (usuario, senha) VALUES(?,?)", usuario, senha)

        return render_template("login.html", success="Cadastro efetuado com sucesso. Faça o login.")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        usuario = request.form.get("username_login")
        senha = request.form.get("password_login")

        if not usuario or not senha:
            return render_template("login.html", error="Por favor, preencha todos os campos.")

        senha_verdadeira = db.execute("SELECT senha from usuarios where usuario = ?", usuario)
        if senha_verdadeira:
            senha_verdadeira = senha_verdadeira[0]['senha']

        id = db.execute("SELECT id from usuarios where usuario = ?", usuario)

        if senha_verdadeira == senha:
            session["user_id"] = id

            termos_e_descricoes = db.execute("SELECT termo, descricao_de_termo FROM usuarios WHERE usuario = ? AND termo IS NOT NULL AND descricao_de_termo IS NOT NULL ORDER BY termo ASC", usuario)
            termos_e_descricoes_ordenados = sorted(termos_e_descricoes, key=lambda x: x['termo'])
            return render_template("inicial.html", termos_e_descricoes_ordenados=termos_e_descricoes_ordenados)

        return render_template("login.html", error="Usuário ou senha incorretos.")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")



