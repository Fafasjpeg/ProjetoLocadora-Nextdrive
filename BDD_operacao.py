from BDD_conexao import _Session, Cargo,Cliente,Empregado,Endereco,Agencia,Aluguel,Servico,Veiculo, Fornecedor,Departamento,Pagamento
from sqlalchemy import text
from flask import flash

class Operacao:
    
    # ----------------------------- CRUD -------------------------------------------
    
    # ----------------------------- Adicionar Itens -------------------------------------------
    
    def add_Cliente(self,nome,telefone,email,foto,senha,cpf,data_de_nasci,cnh,genero):
        with _Session() as session: #uso do session no lugar do db por não ter conflito entre palavras reservadas
            cliente = Cliente(
                nome=nome,
                telefone=telefone,
                email=email,
                foto=foto,
                senha=senha, #senha ja vem hashada pelo main.py
                cpf=cpf,
                data_de_nasci=data_de_nasci,
                cnh=cnh,
                genero=genero
                )
            session.add(cliente)
            session.commit()

    def add_Empregado(self,nome,telefone,email, senha,salario,cpf,data_de_nasci,genero, id_departamento, id_endereco, id_cargo):   
        with _Session() as session:
            empregado = Empregado(
                nome=nome,
                telefone=telefone,
                email=email,
                senha=senha, #senha ja vem hashada pelo main.py
                salario=salario,
                cpf=cpf,
                data_de_nasci=data_de_nasci,
                genero=genero,
                id_departamento = id_departamento,
                id_endereco = id_endereco,
                id_cargo = id_cargo,
                )
            session.add(empregado)
            session.flush() 

    def add_Endereco(self,logradouro,bairro,numero,cep,complemento,cidade,estado):
        with _Session() as session:
            endereco = Endereco(
                logradouro=logradouro,
                bairro=bairro,
                numero=numero,
                cep=cep,
                complemento=complemento,
                cidade=cidade,
                estado=estado
                )
            session.add(endereco)
            session.commit() 
            
    def add_Agencia(self,nome,telefone,email,id_endereco):
        with _Session() as session:
            agencia = Agencia(
                nome=nome,
                telefone=telefone,
                email=email,
                id_endereco = id_endereco,
                )
            session.add(agencia)
            session.commit()                     

    def add_Aluguel(self,id_agencia_retirada, id_agencia_devolucao , data_retirada,hora_retirada,data_aluguel,data_devolutiva,quantidade_dias,plano, id_cliente,id_veiculo):
        with _Session() as session:
            aluguel = Aluguel(
                id_agencia_retirada=id_agencia_retirada,
                id_agencia_devolucao=id_agencia_devolucao,
                data_retirada=data_retirada,
                hora_retirada=hora_retirada,
                data_aluguel=data_aluguel,
                data_devolutiva=data_devolutiva,
                quantidade_dias=quantidade_dias,
                plano=plano,
                id_cliente=id_cliente,
                id_veiculo=id_veiculo
                )
            session.add(aluguel)
            session.commit()                     

    def add_Cargo(self,cargo,funcao):
        with _Session() as session:
            cargo = Cargo(
                cargo=cargo,
                funcao=funcao
                )
            session.add(cargo)
            session.commit()         

    def add_Departamento(self,nome,descricao,funcao,situacao,complemento):
        with _Session() as session:
            departamento = Departamento(
                nome=nome,
                descricao=descricao,
                funcao=funcao,
                situacao=situacao,
                complemento=complemento
                )
            session.add(departamento)
            session.commit()           

    def add_Fornecedor(self,cnpj,razao_social,nome_fantasia,foto):
        with _Session() as session:
            fornecedor = Fornecedor(
                cnpj=cnpj,
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                foto=foto
                )
            session.add(fornecedor)
            session.commit()          

    def add_Pagamento(self,forma_pagamento,valor_multa,valor_aluguel,valor_servicos,valor_total,observacoes,status_pagamento, parcelas):
        with _Session() as session:
            pagamento = Pagamento(
                forma_pagamento=forma_pagamento,
                valor_multa=valor_multa,
                valor_aluguel=valor_aluguel,
                valor_servicos=valor_servicos,
                valor_total=valor_total,
                observacoes=observacoes,
                status_pagamento=status_pagamento,
                parcelas = parcelas
                )
            session.add(pagamento)
            session.commit() 

    def add_Servico(self,tipo_servico,nome,preco):
        with _Session() as session:
            servico = Servico(
                tipo_servico=tipo_servico,
                nome=nome,
                preco=preco
                )
            session.add(servico)
            session.commit() 

    def add_Veiculo(self,marca,modelo,placa,cor,quilometragem,valor_aquisicao,categoria):
        with _Session() as session:
            veiculo = Veiculo(
                marca=marca,
                modelo=modelo,
                placa=placa,
                cor=cor,
                quilometragem=quilometragem,
                valor_aquisicao=valor_aquisicao,
                categoria=categoria
                )
            session.add(veiculo)
            session.commit() 
            
    # ----------------------------- Visualizar os Itens -------------------------------------------

    def visual_Cliente(self,email):
        with _Session() as session:
            cliente = session.query(Cliente).filter(Cliente.email == email).first() 

            #Se nao achar o cliente com a senha inserida
            if  not cliente:
                return flash("E-mail não cadastrado.", "error")  
            
            return cliente
    
        
    def visual_Endereco(self, id_cliente):
        with _Session() as session:
            cliente = session.query(Cliente).filter(Cliente.id_cliente==id_cliente).first()
            
            if not cliente:
                return flash("Cliente não encontrado.", "error")
            
            endereco = session.query(Endereco).filter(Endereco.id_endereco==cliente.id_endereco).first()   
            
            if not endereco:
                return flash("Endereço não encontrado.", "error")
                     
            return endereco
   
            
    def visual_Agencia(self,nome):
        with _Session() as session:
            agencia = session.query(Agencia).filter(Agencia.nome == nome).first()
            
            if not agencia:
                return flash("Agência não encontrada.", "error")
            
            return agencia                     
        
    #Funcoes que apenas o Admin pode utilizar                    

    def visual_Empregado(self,cpf):
        with _Session() as session:
            empregado = session.query(Empregado).filter(Empregado.cpf == cpf).first()
            
            if not empregado:
                return flash("Empregado não encontrado.", "error")
            
            return empregado 

    def visual_Departamento(self,nome):
        with _Session() as session:
            departamento = session.query(Departamento).filter(Departamento.nome == nome).first()
            
            if not departamento:
                return flash("Departamento não encontrado.", "error")
            
            return departamento    

    def visual_Fornecedor(self,cnpj):
        with _Session() as session:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first()
            
            if not fornecedor:
                return flash("Fornecedor não encontrado.", "error")
            
            return fornecedor          

    def visual_Servico(self,nome):
        with _Session() as session:
            servico = session.query(Servico).filter(Servico.nome == nome).first()
             
            if not servico:
                return flash("Serviço não encontrado.", "error")
            
            return servico 

    def visual_Veiculo(self,placa):
        with _Session() as session:     
            veiculos = session.query(Veiculo).filter(Veiculo.placa == placa).first()
            
            if not veiculos:
                return flash("Veículo não encontrado.", "error")
            
            return veiculos
        
    
    # ----------------------------- Deletar Itens -------------------------------------------
    
    def DELETAR_cliente(self, email):
        with _Session() as session:
            cliente = session.query(Cliente).filter(Cliente.email == email).first()    
            if cliente:
                session.delete(cliente)
                session.commit()    
            else:
                return flash("Cliente não foi encontrado para ser deletado", "error")


    def DELETAR_veiculo(self, placa):
        with _Session() as session:
            veiculo = session.query(Veiculo).filter(Veiculo.placa == placa).first()
            if veiculo:
                session.delete(veiculo)
                session.commit()
            else:
                return flash("Veículo não foi encontrado para ser deletado", "error")


    def DELETAR_agencia(self, nome):
        with _Session() as session:
            agencia = session.query(Agencia).filter(Agencia.nome == nome).first()
            if agencia:
                session.delete(agencia)
                session.commit()
            else:
                return flash("Agência não foi encontrada para ser deletada", "error")


    def DELETAR_fornecedor(self, cnpj):
        with _Session() as session:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first()
            if fornecedor:
                session.delete(fornecedor)
                session.commit()
            else:
                return flash("Fornecedor não foi encontrado para ser deletado", "error")

    # ----------------------------- Atualizar Itens -------------------------------------------
    
    def Atualizar_cliente(self,id , coluna, novo_valor):
        with _Session() as session:
           cliente = session.query(Cliente).filter(Cliente.id == id).first() 
           
           if not cliente:
               return flash("Cliente não encontrado para atualização.", "error")

           setattr(cliente, coluna, novo_valor)
           session.commit()

    def Atualizar_endereco_cliente(self, email, coluna, novo_valor):
        with _Session() as session:
            cliente = session.query(Cliente).filter(Cliente.email == email).first()
           
            if not cliente:
                return flash("Cliente não encontrado para atualização do endereço.", "error")
            
            endereco = session.query(Endereco).filter(Endereco.id_endereco == cliente.id_endereco).first() 
           
            if not endereco:
               return flash("Endereço não encontrado para atualização.", "error")

            setattr(endereco, coluna, novo_valor)
            session.commit() 

    def Atualizar_endereco_agencia(self, nome, coluna, novo_valor):
        with _Session() as session:
           agencia = session.query(Agencia).filter(Agencia.nome == nome).first()
           
           if not agencia:
               return flash("Agência não encontrada para atualização do endereço.", "error")
           
           endereco = session.query(Endereco).filter(Endereco.id_endereco == agencia.id_agencia).first() 
           
           if not endereco:
               return flash("Endereço da agencia não encontrado para atualização.", "error")

           setattr(endereco, coluna, novo_valor)
           session.commit()              

    def Atualizar_servico(self, nome, coluna, novo_valor):
        with _Session() as session:
           servico = session.query(Servico).filter(Servico.nome == nome).first()
           
           if not servico:
               return flash("Serviço não encontrado para atualização.", "error")

           setattr(servico, coluna, novo_valor)
           session.commit()  

    def Atualizar_aluguel(self, id_aluguel, coluna, novo_valor):
        with _Session() as session:
           aluguel = session.query(Aluguel).filter(Aluguel.id_aluguel == id_aluguel).first()
           
           if not aluguel:
               return flash("Aluguel nao encontrado", "error")

           setattr(aluguel, coluna, novo_valor)
           session.commit()

    def Atualizar_pagamento(self, id_aluguel, coluna, novo_valor):
        with _Session() as session:
           pagamento = session.query(Pagamento).filter(Pagamento.id_aluguel == id_aluguel).first()
           
           if not pagamento:
               return flash("Pagamento nao encontrado", "error")

           setattr(pagamento, coluna, novo_valor)
           session.commit()
           
           
    # ----------------------------- Listar Itens (filtros) -------------------------------------------
    
    def listar_todos_veiculos(self):
        with _Session() as session:
            veiculos = session.query(Veiculo).all()

            if not veiculos:
                flash("Nenhum veículo encontrado.", "error")
                return []  # <- volta uma lista vazia

            return veiculos
           
    def filtrar_veiculos_por_categoria(self, categoria):
        with _Session() as session:
            veiculos = session.query(Veiculo).filter(Veiculo.categoria == categoria).all()

            if not veiculos:
                flash("Nenhum veículo dessa categoria encontrado.", "error")
                veiculos=[] # <- volta uma lista vazia

            return veiculos

        
    def listar_alugueis_por_cliente(self, id_cliente):
        with _Session() as session:
            alugueis = session.query(Aluguel).filter(Aluguel.id_cliente == id_cliente).all()
            return alugueis
        
    def listar_agencias(self):
        with _Session() as session:
            agencias = session.query(Agencia).all()

            if not agencias:
                flash("Nenhuma agência encontrada.", "error")
                return []  # <-- Retorna lista vazia para evitar erros

            return agencias
        
    def listar_todos_cargos(self):
        with _Session() as session:
            cargos = session.query(Cargo).all()

            if not cargos:
                flash("Nenhum cargo encontrado.", "error")
                return []  # retorna lista vazia se não houver registros

            return cargos

    def formatar_cpf(self, cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

    def formatar_data(self, data):
        return data.strftime("%d/%m/%Y")


       
#fotos_b = b'foto'    
#data_nascimento = '01/05/2008'
#operacao.add_Endereco('logradouro','bairro',31,'cep','complemento','cidade','estado')      
#operacao.add_Cliente('nome','telefone','email',fotos_b,'senha','cpf','2008-05-01','cnh','g',operacao.visual_Endereco())
    