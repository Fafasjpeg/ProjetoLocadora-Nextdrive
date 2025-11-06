from flask import Flask, render_template, redirect, url_for, make_response, session, request
import os
from cripto_itens import Seguranca
from BDD_operacao import Operacao

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
criptografia = Seguranca()
operacao = Operacao()

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

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        
        # Dados pessoais
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        data_nascimento = request.form.get('dataNascimento')
        cnh = request.form.get('cnh')
        genero = request.form.get('genero')
        cpf = request.form.get('cpf')
        telefone = request.form.get('telefone')

        # Endereço
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        bairro = request.form.get('bairro')
        cep = request.form.get('cep')
        complemento = request.form.get('complemento')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')  

        # Foto (arquivo)
        foto = request.files.get('foto')
        foto_bytes = None
        if foto and foto.filename != '':
            foto_bytes = foto.read()
            #foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
            #foto.save(foto_path)

        #TESTE
        #operacao.add_Endereco(logradouro,bairro,numero,cep,complemento,cidade,estado)
        #operacao.add_Cliente(nome,telefone,email,foto_bytes,senha,cpf,data_nascimento,cnh,genero)
    
#pritna no console os dados recebidos
        print("\n=== Novo Cadastro Recebido ===")
        print(f"Nome: {nome}")
        print(f"E-mail: {email}")
        print(f"Senha: {senha}")
        print(f"Data de Nascimento: {data_nascimento}")
        print(f"CNH: {cnh}")
        print(f"Gênero: {genero}")
        print(f"CPF: {cpf}")
        print(f"Telefone: {telefone}")
        print(f"Endereço: {logradouro}, {numero} - {bairro}")
        print(f"CEP: {cep}")
        print(f"Complemento: {complemento}")
        print(f"Cidade: {cidade}")
        print(f"Estado: {estado}")
        print(f"Foto salva em: {foto_path}\n")
        
        return redirect(url_for('login'))
            
    return render_template('cadastro.html')

@app.route("/perfil")
def perfil():
    return render_template('perfil.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        print(f"\n=== Tentativa de Login ===\n E-mail: {email}\nSenha: {senha}\n")
        
        return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route("/redefinirsenha")
def redefinirsenha():
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        senha2 = request.form.get('senha2')
        
        if senha != senha2:
            print("\n=== Erro na Redefinição de Senha ===\n As senhas não coincidem.\n")
            return redirect(url_for('redefinirsenha'))
        
        print(f"\n=== Solicitação de Redefinição de Senha ===\n E-mail: {email}\n Nova Senha: {senha}\n")
        return redirect(url_for('login'))
    
    return render_template('redefinir.html')

@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    if request.method == 'POST':
        
        metodo = request.form.get('payment_method') 
        
        numero = request.form.get('numero_cartao')
        nome = request.form.get('nome_cartao')
        validade = request.form.get('validade')
        cvv = request.form.get('cvv')
        parcelas = request.form.get('parcelas')

        chave_pix = request.form.get('pix_chave') # nao entendi. por que vamos receber a chave pix?

        if metodo == 'credito':
            print("Pagamento com cartão de crédito:", numero, parcelas)
        elif metodo == 'debito':
            print("Pagamento no débito:", numero)
        elif metodo == 'pix':
            print("Pagamento via Pix com chave:", chave_pix)
        else:
            print("Método não especificado")

        return redirect(url_for('confirmacaoreserva'))
    
    return render_template('pagamento.html')

@app.route("/reserva", methods=['GET', 'POST'])
def reserva():
    
    if request.method == 'POST':
        
        agenciaretirada = request.form.get('agenciaretirada')
        agenciadevolucao = request.form.get('agenciadevolucao')
        data_retirada = request.form.get('dataretirada')
        data_devolucao = request.form.get('datadevolucao') #a gente que define
        
        
        print(f"\n=== Reserva de Veículo ===\n Data de Retirada: {data_retirada}\n Data de Devolução: {data_devolucao}\n")
        
        return redirect(url_for('pagamento'))
    
    return render_template('reserva.html')

@app.route("/confirmacaoreserva")
def confirmacaoreserva():
    return render_template('confirmacaoreserva.html')

if __name__ == "__main__":
    app.run(debug=True)
