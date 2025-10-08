from flask import Flask, render_template, redirect, url_for, make_response, session, request

app = Flask(__name__)

@app.route("/")
def base():
    return redirect(url_for('index'))

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/listadeveiculos")
def listadeveiculos():
    return render_template('listadeveiculos.html')

@app.route("/listadeveiculos/veiculo")
def veiculo():
    return render_template('veiculo.html')

@app.route("/termos")
def termos():
    return render_template('termos.html')

@app.route("/privacidade")
def privacidade():
    return render_template('privacidade.html')

@app.route("/cadastro")
def cadastro():
    return render_template('cadastro.html')

@app.route("/perfil")
def perfil():
    return render_template('perfil.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/redefinirsenha")
def redefinirsenha():
    return render_template('redefinir.html')

@app.route("/pagamento")
def pagamento():
    return render_template('pagamento.html')

@app.route("/reserva")
def reserva():
    return render_template('reserva.html')

@app.route("/confirmacaoreserva")
def confirmacaoreserva():
    return render_template('confirmacaoreserva.html') #teste para ver html

if __name__ == "__main__":
    app.run(debug=True)
