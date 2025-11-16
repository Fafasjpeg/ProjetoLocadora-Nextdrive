from flask import Flask, render_template, redirect, url_for, make_response, session, request, flash
import os
from datetime import datetime
from cripto_itens import Seguranca
from BDD_operacao import Operacao
from BDD_conexao import Cliente, Endereco, Veiculo, Aluguel, Servico, Fornecedor, Agencia, Empregado, Departamento, Cargo, Pagamento, _Session


app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

operacao = Operacao()

@app.route("/")
def base():
    return redirect(url_for('index'))

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    
    #se tiver esses ids na session, tira eles
    aluguel_id = session.get('aluguel_id')
    if aluguel_id:
        session.pop('aluguel_id', None)
    pagamento_id = session.get('pagamento_id')
    if pagamento_id:
        session.pop('pagamento_id', None)
        
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    db = _Session()

    # Pega o cliente logado
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()

    # Filtro de categoria via URL
    categoria = request.args.get('categoria')
    if categoria:
        veiculos = operacao.filtrar_veiculos_por_categoria(categoria)
    else:
        veiculos = operacao.listar_todos_veiculos()

    return render_template('home.html', cliente=cliente, veiculos=veiculos)


@app.route("/listadeveiculos")
def listadeveiculos():
    veiculos = operacao.listar_todos_veiculos()
    return render_template('listadeveiculos.html', veiculos=veiculos)


@app.route("/listadeveiculos/<int:id_veiculo>")
def veiculo(id_veiculo):
    db = _Session()

    veiculo = db.query(Veiculo).filter(Veiculo.id_veiculo == id_veiculo).first()

    #validacao
    if not veiculo:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for('listadeveiculos'))

    return render_template('veiculo.html', veiculo=veiculo)

@app.route("/termos")
def termos():
    return render_template('termos.html')

@app.route("/privacidade")
def privacidade():
    return render_template('privacidade.html')

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':
        db = _Session()

        try:
            # cliente dados
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')
            senha_hash = Seguranca.gerar_hash(senha)
            data_nascimento = request.form.get('dataNascimento')
            cnh = request.form.get('cnh')
            genero = request.form.get('genero')
            cpf = request.form.get('cpf')
            telefone = request.form.get('telefone')

            # verifica email unico
            if db.query(Cliente).filter(Cliente.email == email).first():
                flash("E-mail já cadastrado.", "error")
                return redirect(url_for('cadastro'))

            # endereco dados
            logradouro = request.form.get('logradouro')
            numero = request.form.get('numero')
            bairro = request.form.get('bairro')
            cep = request.form.get('cep')
            complemento = request.form.get('complemento')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')

            # foto
            foto = request.files.get('foto')
            foto_bytes = foto.read() if foto and foto.filename else None

            # novo endereco
            novo_endereco = Endereco(
                logradouro=logradouro,
                numero=numero,
                bairro=bairro,
                cep=cep,
                complemento=complemento,
                cidade=cidade,
                estado=estado
            )
            db.add(novo_endereco)
            db.flush()  # garante id_endereco

            # converte data nascimento
            
            data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()

            # novo cliente
            novo_cliente = Cliente(
                nome=nome,
                email=email,
                senha=senha_hash,
                data_de_nasci=data_nascimento,
                cnh=cnh,
                genero=genero,
                cpf=cpf,
                telefone=telefone,
                foto=foto_bytes,
                id_endereco=novo_endereco.id_endereco # pega o id do endereco criado
            )

            db.add(novo_cliente)
            db.commit()

            flash("Cadastro concluído com sucesso!", "success")
            return redirect(url_for('login'))

        except Exception as e:
            db.rollback()
            print(str(e))
            flash("Erro ao cadastrar. Tente novamente.", "error")
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

@app.route("/perfil")
def perfil():

    # verifica se esta logado
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    db = _Session()

    # busca o cliente 
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    alugueis = db.query(Aluguel).filter(Aluguel.id_cliente == id_cliente).all()

    db.close()

    if not cliente:
        flash("Conta não encontrada. Faça login novamente.", "error")
        session.pop('cliente_id', None)
        return redirect(url_for('login'))

    return render_template('perfil.html', cliente=cliente, alugueis=alugueis)

    

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        db = _Session()

        email = request.form.get('email')
        senha_inserida = request.form.get('senha')

        # busca pelo email
        cliente = db.query(Cliente).filter(Cliente.email == email).first()

        if not cliente:
            flash("E-mail não cadastrado.", "error")
            db.close()
            return redirect(url_for('login'))

        # valida hash
        if not Seguranca.verificar(senha_inserida, cliente.senha):
            flash("Senha incorreta.", "error")
            db.close()
            return redirect(url_for('login'))

        # guarda na session
        session['cliente_id'] = cliente.id_cliente

        db.close()
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route("/logout")
def logout():
    # tira o id do cliente da sessão
    session.pop('cliente_id', None)

    flash("Você saiu da sua conta.", "success")
    
    return redirect(url_for('login'))

@app.route("/redefinirsenha", methods=['GET', 'POST'])
def redefinirsenha():

    if request.method == 'POST':
        db = _Session()

        email = request.form.get('email')
        senha_inserida = request.form.get('senha')
        senha2 = request.form.get('senha2')

        # busca cliente
        cliente = db.query(Cliente).filter(Cliente.email == email).first()

        if not cliente:
            flash("E-mail não cadastrado.", "error")
            return redirect(url_for('redefinirsenha'))

        if senha_inserida != senha2:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('redefinirsenha'))

        # gera o hash 
        senha_nova_hash = Seguranca.gerar_hash(senha_inserida)

        # atualiza a senha 
        cliente.senha = senha_nova_hash
        db.commit()

        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for('login'))

    return render_template('redefinir.html')

from datetime import datetime, date, time

@app.route("/reserva/<int:id_veiculo>", methods=['GET', 'POST'])
def reserva(id_veiculo):

    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    db = _Session()

    agencias = operacao.listar_agencias()
    cliente = db.query(Cliente).get(id_cliente)
    veiculo = db.query(Veiculo).get(id_veiculo)

    if not veiculo:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':

        plano = request.form.get("plano")  
        data_retirada = request.form.get('dataretirada')
        data_devolucao = request.form.get('datadevolucao')
        agencia_retirada = request.form.get('agenciaretirada')
        agencia_devolucao = request.form.get('agenciadevolucao')

        # converter para datas
        dt_r = datetime.strptime(data_retirada, "%Y-%m-%d")
        dt_d = datetime.strptime(data_devolucao, "%Y-%m-%d")

    # calculo de dias
        quantidade_dias = (dt_d - dt_r).days

        if quantidade_dias <= 0:
            flash("A data de devolução deve ser posterior à de retirada.", "error")
            return redirect(request.url)

        aluguel = Aluguel(
            id_agencia_retirada=agencia_retirada,
            id_agencia_devolucao=agencia_devolucao,
            data_retirada=data_retirada,
            hora_retirada="00:00",
            data_aluguel=date.today(),
            data_devolutiva=data_devolucao,
            quantidade_dias=quantidade_dias,
            plano=plano,                   
            id_cliente=id_cliente,
            id_veiculo=id_veiculo
        )

        db.add(aluguel)
        db.commit()
        db.refresh(aluguel)
        
        # salvar id aluguel numa session
        session['aluguel_id'] = aluguel.id_aluguel

        return redirect(url_for('pagamento'))

    return render_template('reserva.html', veiculo=veiculo, cliente=cliente, agencias=agencias)

@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))
    
    id_aluguel = session.get('aluguel_id')
    if not id_aluguel:
        flash("Nenhuma reserva encontrada.", "error")
        return redirect(url_for("home"))

    db = _Session()
    aluguel = db.query(Aluguel).get(id_aluguel)
    veiculo = db.query(Veiculo).get(aluguel.id_veiculo)
    cliente = db.query(Cliente).get(id_cliente)

    if request.method == 'POST':

        metodo = request.form.get('payment_method') 
        parcelas = request.form.get('parcelas') or 1
        valor_aluguel = veiculo.valor_diario * aluguel.quantidade_dias

        pagamento = Pagamento(
            forma_pagamento=metodo,
            valor_multa=0,
            valor_aluguel=valor_aluguel,
            valor_servicos=0,
            valor_total=valor_aluguel,
            observacoes=None,
            status_pagamento=True,
            id_aluguel=id_aluguel,
            parcelas=parcelas
        )

        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)

        # salvar id pagamento numa session
        session['pagamento_id'] = pagamento.id_pagamento

        from utils.email_sender import enviar_email_confirmacao

        # html do email
        html_email = f"""
        <h2>Reserva Confirmada ✓</h2>

        <h3>Cliente</h3>
        <p><strong>{cliente.nome}</strong></p>
        <p>Email: {cliente.email}</p>

        <h3>Veículo</h3>
        <p><strong>{veiculo.modelo}</strong> — {veiculo.marca}</p>
        <p>Placa: {veiculo.placa}</p>
        <p>R$ {veiculo.valor_diario:.2f} por dia</p>

        <h3>Detalhes da Reserva</h3>
        <p><strong>Retirada:</strong> {aluguel.data_retirada} — 
        {aluguel.agencia_retirada.nome} — {aluguel.agencia_retirada.logradouro}, {aluguel.agencia_retirada.numero}</p>

        <p><strong>Devolução:</strong> {aluguel.data_devolutiva} — 
        {aluguel.agencia_devolucao.nome} — {aluguel.agencia_devolucao.logradouro}, {aluguel.agencia_devolucao.numero}</p>

        <h3>Pagamento</h3>
        <p><strong>Método:</strong> {pagamento.forma_pagamento}</p>
        <p><strong>Parcelas:</strong> {pagamento.parcelas}</p>
        <p><strong>Total:</strong> R$ {pagamento.valor_total:.2f}</p>

        <p style="margin-top:20px;">Obrigado por escolher a <strong>NextDrive</strong>!</p>
        """

        # envia o email
        status, resposta = enviar_email_confirmacao(
            api_key="2cwQLyrVjUz8gRG9",
            destino=cliente.email,
            assunto="Confirmação da Reserva - NextDrive",
            html=html_email
        )

        print("STATUS EMAIL:", status, resposta)

        flash("Pagamento realizado e reserva confirmada!", "success")
        return redirect(url_for('confirmacaoreserva'))
    
    return render_template('pagamento.html', id_aluguel=id_aluguel)

@app.route("/confirmacaoreserva")
def confirmacaoreserva():
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    id_aluguel = session.get('aluguel_id')
    if not id_aluguel:
        flash("Nenhuma reserva encontrada.", "error")
        return redirect(url_for("home"))
    
    id_pagamento = session.get('pagamento_id')
    if not id_pagamento:
        flash("Nenhum pagamento encontrado.", "error")  
        return redirect(url_for("home"))
    
    db = _Session()
    
    aluguel = db.query(Aluguel).get(id_aluguel)
    veiculo = db.query(Veiculo).get(aluguel.id_veiculo)
    pagamento = db.query(Pagamento).get(id_pagamento)
    cliente = db.query(Cliente).get(id_cliente)
        
    return render_template('confirmacaoreserva.html', aluguel=aluguel, veiculo=veiculo, pagamento=pagamento, cliente=cliente)

if __name__ == "__main__":
    app.run(debug=True)
