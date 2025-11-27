from flask import Flask, render_template, redirect, url_for, make_response, session, request, flash, send_file, Response
import os
import re
import base64
import io
from utils.email_sender import enviar_email_confirmacao, montar_email_contato
from utils.validacao_idade import calcular_idade
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime
from decimal import Decimal
from cripto_itens import Seguranca
from BDD_operacao import Operacao
from BDD_conexao import Cliente, Endereco, Veiculo, Aluguel, Servico, Fornecedor, Agencia, Empregado, Departamento, Cargo, Pagamento, _Session
from dotenv import load_dotenv

app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'
load_dotenv()
operacao = Operacao()

@app.route("/")
def base():
    return redirect(url_for('nextdrive'))

@app.route("/index")
def index():
    return render_template('index.html')

from flask import Response, redirect, url_for

#rota pra buscar a foto do veiculo no banco e devolver como imagem
@app.route("/foto_veiculo/<int:id_veiculo>")
def foto_veiculo(id_veiculo):
    db = _Session()
    veiculo = db.query(Veiculo).filter_by(id_veiculo=id_veiculo).first()
    db.close()

    if not veiculo or not veiculo.foto:
        # devolve a imagem padrao do veículo
        return redirect(url_for('static', filename='img/cars/carromisterio.jpg'))

    # retorna a imagem 
    return Response(veiculo.foto, mimetype="image/jpeg")

@app.route("/nextdrive")
def nextdrive():
    return render_template('landingpage.html')

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

    # pega o cliente logado
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()

    # filtro de categoria via url pelo args
    categoria = request.args.get('categoria')
    if categoria:
        veiculos = operacao.filtrar_veiculos_por_categoria(categoria)
    else:
        veiculos = operacao.listar_todos_veiculos()
    
    db.close()

    return render_template('home.html', cliente=cliente, veiculos=veiculos)


@app.route("/listadeveiculos")
def listadeveiculos():
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    db = _Session()

    categoria = request.args.get('categoria')
    if categoria:
        veiculos = operacao.filtrar_veiculos_por_categoria(categoria)
    else:
        veiculos = operacao.listar_todos_veiculos()

    db.close()

    return render_template('listadeveiculos.html', veiculos=veiculos, categoria=categoria)

@app.route("/listadeveiculos/<int:id_veiculo>")
def veiculo(id_veiculo):
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))
    
    db = _Session()

    veiculo = db.query(Veiculo).filter(Veiculo.id_veiculo == id_veiculo).first()
    
    db.close()
    
    #validacao
    
    if not veiculo:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for('listadeveiculos'))

    return render_template('veiculo.html', veiculo=veiculo)

@app.route("/termos")
def termos():
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))
    
    return render_template('termos.html')

@app.route("/privacidade")
def privacidade():
    
    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))
    
    return render_template('privacidade.html')

@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        assunto = request.form.get("assunto")
        mensagem = request.form.get("mensagem")

        # monta o html do email
        html_email = montar_email_contato(nome, email, telefone, assunto, mensagem)

        # email da empresa (destino)
        destino = "contatonextdrive@gmail.com"

        # envia usando sua função
        status, retorno = enviar_email_confirmacao(
            api_key='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', # a chave devera ser alterada toda vez que for feito um commit
            destino=destino,
            assunto=f"Novo contato do site - {nome}",
            html=html_email
        )

        if status == 201:
            flash("Mensagem enviada com sucesso! Em breve retornaremos o contato.", "success")
        else:
            flash("Erro ao enviar a mensagem. Tente novamente mais tarde.", "error")
            print("ERRO EMAIL:", status, retorno)

        return redirect(url_for("contato"))

    return render_template("contato.html")


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

            data_nascimento_str = request.form.get('data_nascimento')
            data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()

            cnh = request.form.get('cnh')
            genero = request.form.get('genero')
            
            # valida idade
            if calcular_idade(data_nascimento) < 18:
                flash("Você deve ter pelo menos 18 anos para se cadastrar.", "error")
                return redirect(url_for('cadastro'))

            # remove mascara CPF e telefone
            cpf = re.sub(r'\D', '', request.form.get('cpf'))
            telefone = re.sub(r'\D', '', request.form.get('telefone'))

            # verifica email único
            if db.query(Cliente).filter(Cliente.email == email).first():
                flash("E-mail já cadastrado.", "error")
                return redirect(url_for('cadastro'))

            # endereco dados
            logradouro = request.form.get('logradouro')
            numero = int(request.form.get('numero'))
            bairro = request.form.get('bairro')
            cep = re.sub(r'\D', '', request.form.get('cep'))
            complemento = request.form.get('complemento')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')

            # foto
            foto = request.files.get('foto')
            foto_bytes = foto.read() if foto and foto.filename else None

            # novo endereço
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
            db.flush()

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
                id_endereco=novo_endereco.id_endereco
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

        finally:
            db.close()

    return render_template('cadastro.html')

# rtoa pra pegar a foto do cliente no banoc em bytes e devolver como imagem
@app.route("/foto_cliente/<int:id_cliente>")
def foto_cliente(id_cliente):
    db = _Session()
    cliente = db.query(Cliente).filter_by(id_cliente=id_cliente).first()
    db.close()

    if not cliente or not cliente.foto:
        # devolve a imagem padrao
        return redirect(url_for('static', filename='img/default-user.jpg'))

    # retorna imagem diretamente
    return Response(cliente.foto, mimetype="image/jpeg")

@app.route("/perfil")
def perfil():

    id_cliente = session.get('cliente_id')
    if not id_cliente:
        return redirect(url_for('login'))

    db = _Session()
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    alugueis = db.query(Aluguel).filter(Aluguel.id_cliente == id_cliente).all()

    if not cliente:
        flash("Conta não encontrada.", "error")
        session.pop('cliente_id', None)
        return redirect(url_for('login'))

    # aplicar mascara
    cliente.cpf_formatado = operacao.formatar_cpf(cliente.cpf)
    cliente.data_formatada = operacao.formatar_data(cliente.data_de_nasci)

    return render_template('perfil.html', cliente=cliente, alugueis=alugueis)

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        db = _Session()

        email = request.form.get('email')
        senha_inserida = request.form.get('senha')

        # busca pelo email
        cliente = db.query(Cliente).filter(Cliente.email == email).first()

        db.close()
        
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
        db.close()

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
        agencia_retirada = int(request.form.get('agenciaretirada'))
        agencia_devolucao = int(request.form.get('agenciadevolucao'))

        # converte para datas
        dt_r = datetime.strptime(data_retirada, "%Y-%m-%d").date()
        dt_d = datetime.strptime(data_devolucao, "%Y-%m-%d").date()

        # validacao de datas
        if dt_d <= dt_r:
            flash("A data de devolução deve ser posterior à de retirada.", "error")
            return redirect(url_for('reserva', id_veiculo=id_veiculo))

        # checa disponibilidade do veiculo
        alugueis_conflitantes = db.query(Aluguel).filter(
            Aluguel.id_veiculo == id_veiculo,
            Aluguel.data_retirada <= dt_d,
            Aluguel.data_devolucao >= dt_r
        ).all()

        if alugueis_conflitantes:
            # pega o primeiro conflito para informar ao usuario
            conflito = alugueis_conflitantes[0]
            flash(f"Veículo indisponível para o período selecionado. "
                  f"Já está alugado de {conflito.data_retirada} até {conflito.data_devolucao}.", "error")
            return redirect(request.url)

        # calculo de dias
        quantidade_dias = (dt_d - dt_r).days

        # novo aluguel
        aluguel = Aluguel(
            id_agencia_retirada=agencia_retirada,
            id_agencia_devolucao=agencia_devolucao,
            data_retirada=dt_r,
            hora_retirada=time(0,0),
            data_aluguel=date.today(),
            data_devolucao=dt_d,
            quantidade_dias=quantidade_dias,
            plano=plano,
            id_cliente=id_cliente,
            id_veiculo=id_veiculo
        )

        db.add(aluguel)
        db.commit()
        db.refresh(aluguel)
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
        parcelas = int(request.form.get('parcelas') or 1)
        valor_aluguel = Decimal(veiculo.valor_diario) * Decimal(aluguel.quantidade_dias)

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

        session['pagamento_id'] = pagamento.id_pagamento
        
        # formata datas
        data_retirada_fmt = aluguel.data_retirada.strftime("%d/%m/%Y")
        data_devolucao_fmt = aluguel.data_devolucao.strftime("%d/%m/%Y")

        # formata valores
        valor_diario_fmt = f"{veiculo.valor_diario:.2f}".replace(".", ",")
        valor_total_fmt = f"{pagamento.valor_total:.2f}".replace(".", ",")

        # Monta o html do email na rota pagamento
        html_email = f"""
        <h2>Reserva Confirmada ✓</h2>

        <h3>Cliente</h3>
        <p><strong>{cliente.nome}</strong></p>
        <p>Email: {cliente.email}</p>

        <h3>Veículo</h3>
        <p><strong>{veiculo.modelo}</strong> — {veiculo.marca}</p>
        <p>Placa: {veiculo.placa}</p>
        <p>R$ {valor_diario_fmt} por dia</p>

        <h3>Detalhes da Reserva</h3>
        <p><strong>Retirada:</strong> {data_retirada_fmt} —
        {aluguel.agencia_retirada.nome} — {aluguel.agencia_retirada.endereco.logradouro}, {aluguel.agencia_retirada.endereco.numero}</p>

        <p><strong>Devolução:</strong> {data_devolucao_fmt} —
        {aluguel.agencia_devolucao.nome} — {aluguel.agencia_devolucao.endereco.logradouro}, {aluguel.agencia_devolucao.endereco.numero}</p>

        <h3>Pagamento</h3>
        <p><strong>Método:</strong> {pagamento.forma_pagamento}</p>
        <p><strong>Parcelas:</strong> {pagamento.parcelas}</p>
        <p><strong>Total:</strong> R$ {valor_total_fmt}</p>

        <p style="margin-top:20px;">Obrigado por escolher a <strong>NextDrive</strong>!</p>
        """

        # envia o email usando Brevo
        status, resposta = enviar_email_confirmacao(
            api_key='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', # a chave devera ser alterada toda vez que for feito um commit
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
    
    # db.close()
        
    return render_template('confirmacaoreserva.html', aluguel=aluguel, veiculo=veiculo, pagamento=pagamento, cliente=cliente)

@app.route("/limpa_sessoes")
def limpa_sessoes():
    
    # limpa todas as sessoes de aluguel e pagamento e joga pra home
    session.pop('aluguel_id', None)
    session.pop('pagamento_id', None)
    
    return redirect(url_for('home'))

@app.route("/limpa_sessoes_perfil")
def limpa_sessoes_perfil():
    
    # limpa todas as sessoes de aluguel e pagamento e joga pra perfil
    session.pop('aluguel_id', None)
    session.pop('pagamento_id', None)
    
    flash("Sessões de aluguel e pagamento limpas.", "success")
    
    return redirect(url_for('perfil'))

@app.route("/loginadm", methods=['GET', 'POST'])
def loginadm():
    
    id_empregado = session.get('empregado_id')
    if id_empregado:
        return redirect(url_for('homeadm'))

    if request.method == 'POST':
        db = _Session()

        email = request.form.get('email')
        senha_inserida = request.form.get('senha')

        # busca empregado pelo email
        empregado = db.query(Empregado).filter(Empregado.email == email).first()

        db.close()

        if not empregado:
            flash("E-mail não cadastrado.", "error")
            return redirect(url_for('loginadm'))

        # valida hash da senha
        if not Seguranca.verificar(senha_inserida, empregado.senha):
            flash("Senha incorreta.", "error")
            return redirect(url_for('loginadm'))

        # guarda id do empregado na sessão
        session['empregado_id'] = empregado.id_empregado

        return redirect(url_for('homeadm'))  # coloque o painel que você quiser

    return render_template('adm/loginadm.html')

@app.route('/redefinirsenhaempregado', methods=['GET', 'POST'])
def redefinirsenhaempregado():
    if request.method == 'POST':
        db = _Session()

        email = request.form.get('email')
        senha_inserida = request.form.get('senha')
        senha2 = request.form.get('senha2')

        # busca empregado
        empregado = db.query(Empregado).filter(Empregado.email == email).first()

        if not empregado:
            flash("E-mail não cadastrado.", "error")
            return redirect(url_for('redefinirsenhaempregado'))

        if senha_inserida != senha2:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('redefinirsenhaempregado'))

        # gera o hash 
        senha_nova_hash = Seguranca.gerar_hash(senha_inserida)

        # atualiza a senha 
        empregado.senha = senha_nova_hash
        db.commit()
        db.close()

        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for('loginadm'))

    return render_template('adm/redefinirempregado.html')

@app.route("/logoutadm")
def logoutadm():
    session.pop('empregado_id', None)  # remove o id do administrador da sessão
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for('loginadm'))


@app.route("/cadastroadm", methods=['GET', 'POST'])
def cadastroadm():

    db = _Session()
    departamentos = []
    cargos = []

    try:
        # carregar dados para selects
        departamentos = db.query(Departamento).all()
        cargos = operacao.listar_todos_cargos()

        if request.method == 'POST':
            # dados do empregado
            nome = request.form.get('nome').strip()
            email = request.form.get('email').strip()
            senha = request.form.get('senha').strip()
            senha_hash = Seguranca.gerar_hash(senha)
            cpf = re.sub(r'\D', '', request.form.get('cpf'))  # remove a mascara
            data_nascimento = datetime.strptime(request.form.get('data_de_nasci'), "%Y-%m-%d").date()
            genero = request.form.get('genero')
            telefone = re.sub(r'\D', '', request.form.get('telefone'))  # remove a mascara
            salario = request.form.get('salario')
            
            # ids do cargo e departamento 
            id_departamento = request.form.get('id_departamento')
            id_cargo = request.form.get('id_cargo')

            # verifica se email e cpf sao unicos e retornam a resposta ja pelo front end sem tentar inserir no banco
            if db.query(Empregado).filter(Empregado.email == email).first():
                flash("E-mail já cadastrado.", "error")
                return redirect(url_for('cadastroadm'))

            if db.query(Empregado).filter(Empregado.cpf == cpf).first():
                flash("CPF já cadastrado.", "error")
                return redirect(url_for('cadastroadm'))

            # dados do endereco
            logradouro = request.form.get('logradouro').strip()
            numero = int(request.form.get('numero'))
            bairro = request.form.get('bairro').strip()
            cep = re.sub(r'\D', '', request.form.get('cep'))  # remove mascara
            complemento = request.form.get('complemento').strip()
            cidade = request.form.get('cidade').strip()
            estado = request.form.get('estado').strip()

            # novo endereco
            novo_endereco = Endereco(
                logradouro=logradouro,
                numero=numero,
                bairro=bairro,
                cep=cep,
                complemento=complemento if complemento else None,
                cidade=cidade,
                estado=estado
            )
            db.add(novo_endereco)
            db.flush()  # garante id_endereco

            # novo empregado
            novo_empregado = Empregado(
                nome=nome,
                email=email,
                senha=senha_hash,
                cpf=cpf,
                data_de_nasci=data_nascimento,
                genero=genero,
                telefone=telefone,
                salario=salario,
                id_departamento=id_departamento,
                id_cargo=id_cargo,
                id_endereco=novo_endereco.id_endereco # pega o id_endereco do endereco criado
            )

            db.add(novo_empregado)
            db.commit()

            flash("Empregado cadastrado com sucesso!", "success")
            return redirect(url_for('homeadm'))

    except Exception as e: #caso de rollback
        db.rollback()
        print("Erro ao cadastrar empregado:", e)
        flash("Erro ao cadastrar empregado. Tente novamente.", "error")

    finally:
        db.close()

    return render_template("adm/cadastroadm.html", departamentos=departamentos, cargos=cargos)

@app.route("/homeadm")
def homeadm():
    
    # verifica se empregado esta logado
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    db = _Session()

    # busca o empregado logado
    empregado = db.query(Empregado).filter(Empregado.id_empregado == id_empregado).first()

    db.close()

    if not empregado:
        flash("Conta não encontrada. Faça login novamente.", "error")
        session.pop('empregado_id', None)
        return redirect(url_for('loginadm'))

    return render_template('adm/homeadm.html', empregado=empregado)

@app.route("/cadastrofornecedor", methods=['GET', 'POST'])
def cadastrofornecedor():
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    if request.method == 'POST':
        db = _Session()
        try:
            # dados fornecedor
            cnpj = re.sub(r'\D', '', request.form.get('cnpj'))
            razaosocial = request.form.get('razaosocial')
            nome_fantasia = request.form.get('nome_fantasia')

            # verifica se existe cnpj cadastrado
            if db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first():
                flash("CNPJ já cadastrado.", "error")
                return redirect(url_for('cadastrofornecedor'))

            # foto fornecedor
            foto = request.files.get('foto')
            foto_bytes = foto.read() if foto and foto.filename else None

            # dados do endereco do fornecedor
            logradouro = request.form.get('logradouro')
            numero = int(request.form.get('numero'))
            bairro = request.form.get('bairro')
            cep = re.sub(r'\D', '', request.form.get('cep'))
            complemento = request.form.get('complemento')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')

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
            db.flush()  # garante novo_endereco.id_endereco

            # novo fornecedor
            novo_fornecedor = Fornecedor(
                cnpj=cnpj,
                razao_social=razaosocial,
                nome_fantasia=nome_fantasia,
                foto=foto_bytes,
                id_endereco=novo_endereco.id_endereco
            )
            db.add(novo_fornecedor)
            db.commit()

            flash("Fornecedor cadastrado com sucesso!", "success")
            return redirect(url_for('homeadm'))

        except Exception as e:
            db.rollback()
            print(str(e))
            flash("Erro ao cadastrar fornecedor. Tente novamente.", "error")
            return redirect(url_for('cadastrofornecedor'))

        finally:
            db.close()

    return render_template("adm/cadastrofornecedor.html")

@app.route("/cadastroagencia", methods=['GET', 'POST'])
def cadastroagencia():
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    if request.method == 'POST':
        db = _Session()
        try:
            # dados da agencia
            nome = request.form.get('nome')
            telefone = re.sub(r'\D', '', request.form.get('telefone'))
            email = request.form.get('email')

            # dados endereco
            logradouro = request.form.get('logradouro')
            numero = int(request.form.get('numero'))
            bairro = request.form.get('bairro')
            cep = re.sub(r'\D', '', request.form.get('cep'))
            complemento = request.form.get('complemento')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')

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
            db.flush()  # garante novo_endereco.id_endereco

            # nova agencia
            nova_agencia = Agencia(
                nome=nome,
                telefone=telefone,
                email=email,
                id_endereco=novo_endereco.id_endereco
            )
            db.add(nova_agencia)
            db.commit()

            flash("Agência cadastrada com sucesso!", "success")
            return redirect(url_for('homeadm'))

        except Exception as e:
            db.rollback()
            print(str(e))
            flash("Erro ao cadastrar agência. Tente novamente.", "error")
            return redirect(url_for('cadastroagencia'))

        finally:
            db.close()

    return render_template("adm/cadastroagencia.html")


@app.route("/cadastroservico", methods=['GET', 'POST'])
def cadastroservico():
    db = _Session()
    
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    if request.method == 'POST':
        try:
            tipo_servico = request.form.get('tipo_servico')
            nome = request.form.get('nome')
            preco = request.form.get('preco')
            id_fornecedor = request.form.get('id_fornecedor')

            # remove mascara e transforma em float
            preco = float(preco.replace(".", "").replace(",", "."))

            # valida fornecedor
            fornecedor = db.query(Fornecedor).filter_by(id_fornecedor=id_fornecedor).first()
            if not fornecedor:
                flash("Fornecedor inválido.", "error")
                return redirect(url_for('cadastroservico'))

            # novo serviço
            novo_servico = Servico(
                tipo_servico=tipo_servico,
                nome=nome,
                preco=preco,
                id_fornecedor=id_fornecedor
            )

            db.add(novo_servico)
            db.commit()

            flash("Serviço cadastrado com sucesso!", "success")
            return redirect(url_for('homeadm'))

        except Exception as e:
            print(e)
            db.rollback()
            flash("Erro ao cadastrar serviço.", "error")
            return redirect(url_for('cadastroservico'))

        finally:
            db.close()

    # pega os fornecedores para o select
    fornecedores = db.query(Fornecedor).all()
    db.close()

    return render_template("adm/cadastroservico.html", fornecedores=fornecedores)


@app.route("/cadastroveiculo", methods=["GET", "POST"])
def cadastroveiculo():
    # define categorias validas
    categorias_validas = ["Sedan", "Hatch", "SUV", "Luxo"]
    
    # verifica se empregado esta logado
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))
    
    db = _Session()

    if request.method == "POST":
        try:
            # dados do veiculo
            valor_diario = request.form.get("valor_diario")
            data_aquisicao = request.form.get("data_aquisicao")
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            placa = request.form.get("placa")
            cor = request.form.get("cor")
            quilometragem = request.form.get("quilometragem")
            categoria = request.form.get("categoria")

            # valida categoria
            if categoria not in categorias_validas:
                flash("Categoria inválida! Selecione Sedan, Hatch, SUV ou Luxo.")
                return redirect(url_for("cadastroveiculo"))

            # foto do veiculo
            foto = request.files.get("foto")
            foto_bytes = foto.read() if foto and foto.filename else None

            # novo veiculo
            novo_veiculo = Veiculo(
                valor_diario=valor_diario,
                data_aquisicao=data_aquisicao if data_aquisicao else None,
                marca=marca,
                modelo=modelo,
                placa=placa,
                cor=cor,
                quilometragem=quilometragem,
                categoria=categoria,
                foto=foto_bytes # salva foto em bytes no banco
            )

            db.add(novo_veiculo)
            db.commit()
            flash("Veículo cadastrado com sucesso!")
            return redirect(url_for("homeadm"))

        except Exception as e:
            db.rollback()
            print(str(e))
            flash("Erro ao cadastrar veículo. Tente novamente.", "error")
            return redirect(url_for("cadastroveiculo"))

        finally:
            db.close()

    return render_template("adm/cadastroveiculo.html")

@app.route("/cadastrodepartamento", methods=['GET', 'POST'])
def cadastrodepartamento():
    db = _Session()
    
    # verifica se empregado esta logado
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    if request.method == 'POST':
        try:
            # dados depto
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            funcao = request.form.get('funcao', '').strip()
            complemento = request.form.get('complemento', '').strip()
            situacao = request.form.get('situacao', '').strip()

            # validacao nome e situacao obrigatorios
            if not nome or not situacao:
                flash("Preencha todos os campos obrigatórios.", "error")
                return redirect(url_for('cadastrodepartamento'))

            # novo departamento
            novo_dep = Departamento(
                nome=nome,
                descricao=descricao if descricao else None,
                funcao=funcao if funcao else None,
                complemento=complemento if complemento else None,
                situacao=situacao if situacao else None
            )

            db.add(novo_dep)
            db.commit()

            flash("Departamento cadastrado com sucesso!", "success")
            return redirect(url_for('homeadm'))

        except Exception as e:
            print("Erro ao cadastrar departamento:", e)
            db.rollback()
            flash("Erro ao cadastrar departamento. Tente novamente.", "error")
            return redirect(url_for('cadastrodepartamento'))

        finally:
            db.close()

    db.close()
    return render_template("adm/cadastrodepartamento.html")

@app.route("/cadastrocargo", methods=['GET', 'POST'])
def cadastrocargo():
    
    # verifica se empregado esta logado
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))

    if request.method == 'POST':
        db = _Session()

        try:
            # dados cargo
            nome = request.form.get('nome')
            funcao = request.form.get('funcao')

            # trim de espacos
            nome = nome.strip()
            funcao = funcao.strip() if funcao else None

            # nome obrigatorio
            if not nome:
                flash("O nome do cargo é obrigatório.", "error")
                return redirect(url_for('cadastrocargo'))

            # impede cargos duplicados pelo mesmo nome
            if db.query(Cargo).filter(Cargo.nome == nome).first():
                flash("Já existe um cargo cadastrado com esse nome.", "error")
                return redirect(url_for('cadastrocargo'))

            # novo cargo
            novo_cargo = Cargo(
                nome=nome,
                funcao=funcao if funcao else None
            )

            db.add(novo_cargo)
            db.commit()

            flash("Cargo cadastrado com sucesso!", "success")
            return redirect(url_for('homeadm'))

        except Exception as e:
            db.rollback()
            print("Erro ao cadastrar cargo:", str(e))
            flash("Erro ao cadastrar cargo.", "error")
            return redirect(url_for('cadastrocargo'))

        finally:
            db.close()

    return render_template("adm/cadastrocargo.html")

@app.route('/dashboard')
def dashboard():
    
    id_empregado = session.get('empregado_id')
    if not id_empregado:
        return redirect(url_for('loginadm'))
    
    db = _Session()

    # total de alugueis
    total_alugueis = db.query(Aluguel).count()
    # soma do faturamento total
    faturamento_total = db.query(func.sum(Pagamento.valor_total)).scalar() or 0

    # listagens
    veiculos = db.query(Veiculo).all()
    fornecedores = db.query(Fornecedor).all()
    servicos = db.query(Servico).all()
    empregados = db.query(Empregado).all()
    agencias = db.query(Agencia).all()
    
    

    return render_template(
        'adm/dashboard.html',
        total_alugueis=total_alugueis,
        faturamento_total=faturamento_total,
        veiculos=veiculos,
        fornecedores=fornecedores,
        servicos=servicos,
        empregados=empregados,
        agencias=agencias
    )

# rotas para deletar registros no dashboard
@app.route("/deletar_veiculo/<int:id_veiculo>")
def deletar_veiculo(id_veiculo):
    db = _Session()
    veiculo = db.query(Veiculo).get(id_veiculo)
    if veiculo:
        db.delete(veiculo)
        db.commit()
        flash("Veículo deletado com sucesso!", "success")
    else:
        flash("Veículo não encontrado.", "error")
    db.close()
    return redirect(url_for("dashboard"))  # ou a página que lista os veículos

@app.route("/deletar_fornecedor/<int:id_fornecedor>")
def deletar_fornecedor(id_fornecedor):
    db = _Session()
    fornecedor = db.query(Fornecedor).get(id_fornecedor)
    if fornecedor:
        db.delete(fornecedor)
        db.commit()
        flash("Fornecedor deletado com sucesso!", "success")
    else:
        flash("Fornecedor não encontrado.", "error")
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/deletar_servico/<int:id_servico>")
def deletar_servico(id_servico):
    db = _Session()
    servico = db.query(Servico).get(id_servico)
    if servico:
        db.delete(servico)
        db.commit()
        flash("Serviço deletado com sucesso!", "success")
    else:
        flash("Serviço não encontrado.", "error")
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/deletar_empregado/<int:id_empregado>")
def deletar_empregado(id_empregado):
    db = _Session()
    empregado = db.query(Empregado).get(id_empregado)
    if empregado:
        db.delete(empregado)
        db.commit()
        flash("Empregado deletado com sucesso!", "success")
    else:
        flash("Empregado não encontrado.", "error")
    db.close()
    return redirect(url_for("dashboard"))

@app.route("/deletar_agencia/<int:id_agencia>")
def deletar_agencia(id_agencia):
    db = _Session()
    agencia = db.query(Agencia).get(id_agencia)
    if agencia:
        db.delete(agencia)
        db.commit()
        flash("Agência deletada com sucesso!", "success")
    else:
        flash("Agência não encontrada.", "error")
    db.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    
    app.run(debug=True)
