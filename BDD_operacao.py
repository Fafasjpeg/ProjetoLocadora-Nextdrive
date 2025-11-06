from BDD_conexao import _Session, Cargo,Cliente,Empregado,Endereco,Agencia,Aluguel,Servico,Veiculo, Fornecedor,Departamento,Pagamento,ClienteAluguel
from sqlalchemy import  text
import bcrypt


salt = bcrypt.gensalt(rounds=14)

class Operacao:
    
    def add_Cliente(self,nome,telefone,email,foto,senha,cpf,data_de_nasci,cnh,genero):
        with _Session() as session:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'),salt)
            self.cliente = Cliente(nome=nome,telefone=telefone,email=email,foto=foto,senha=senha_hash,cpf=cpf,data_de_nasci=data_de_nasci,cnh=cnh,genero=genero)
            session.add(self.cliente)
            session.commit()

    def add_Empregado(self,nome,telefone,email,foto,salario,cpf,data_de_nasci,genero):
        with _Session() as session:
            self.empregado = Empregado(nome=nome,telefone=telefone,email=email,foto=foto,salario=salario,cpf=cpf,data_de_nasci=data_de_nasci,genero=genero)
            session.add(self.empregado)
            session.commit() 

    def add_Endereco(self,logradouro,bairro,numero,cep,complemento,cidade,estado):
        with _Session() as session:
            self.endereco = Endereco(logradouro=logradouro,bairro=bairro,numero=numero,cep=cep,complemento=complemento,cidade=cidade,estado=estado)
            session.add(self.endereco)
            session.commit() 
            
    def add_Agencia(self,nome,telefone,email):
        with _Session() as session:
            self.agencia = Agencia(nome=nome,telefone=telefone,email=email)
            session.add(self.agencia)
            session.commit()                     

    def add_Aluguel(self,data_retirada,hora_retirada,data_aluguel,data_devolutiva,quantidade_dias,plano):
        with _Session() as session:
            self.aluguel = Aluguel(data_retirada=data_retirada,hora_retirada=hora_retirada,data_aluguel=data_aluguel,data_devolutiva=data_devolutiva,quantidade_dias=quantidade_dias,plano=plano)
            session.add(self.aluguel)
            session.commit()                     

    def add_Cargo(self,cargo,funcao):
        with _Session() as session:
            self.cargo = Cargo(cargo=cargo,funcao=funcao)
            session.add(self.cargo)
            session.commit()         

    def add_Departamento(self,nome,descricao,funcao,situacao,complemento):
        with _Session() as session:
            self.departamento = Departamento(nome=nome,descricao=descricao,funcao=funcao,situacao=situacao,complemento=complemento)
            session.add(self.departamento)
            session.commit()           

    def add_Fornecedor(self,cnpj,razao_social,nome_fantasia,foto):
        with _Session() as session:
            self.fornecedor = Fornecedor(cnpj=cnpj,razao_social=razao_social,nome_fantasia=nome_fantasia, foto=foto)
            session.add(self.fornecedor)
            session.commit()          

    def add_Pagamento(self,forma_pagamento,valor_multa,valor_aluguel,valor_servicos,valor_total,observacoes,status_pagamento):
        with _Session() as session:
            self.pagamento = Pagamento(forma_pagamento=forma_pagamento,valor_multa=valor_multa,valor_aluguel=valor_aluguel,valor_servicos=valor_servicos,valor_total=valor_total,observacoes=observacoes,status_pagamento=status_pagamento)
            session.add(self.pagamento)
            session.commit() 

    def add_Servico(self,tipo_servico,nome,preco):
        with _Session() as session:
            self.servico = Servico(tipo_servico=tipo_servico,nome=nome,preco=preco)
            session.add(self.servico)
            session.commit() 

    def add_Veiculo(self,marca,modelo,placa,cor,quilometragem,valor_aquisicao,categoria):
        with _Session() as session:
            self.veiculo = Veiculo(marca=marca,modelo=modelo,placa=placa,cor=cor,quilometragem=quilometragem,valor_aquisicao=valor_aquisicao,categoria=categoria)
            session.add(self.veiculo)
            session.commit() 
            
    # Visualizar os Itens

    def visual_Cliente(self,senha):
        with _Session() as session:
            self.cliente = session.query(Cliente).filter(Cliente.senha == senha).first() 

            #Se nao achar o cliente com a senha inserida
            if  not self.cliente:
                return None  
            
            #chama uma procedure 
            self.aluguel = session.execute(text('CALL visualizar_aluguel(:id)'),  {"id":self.cliente.id_cliente }).fetchall() 
            self.pagamento = session.execute(text('CALL visualizar_pagamento(:id)'),  {"id":self.pagamento.id_pagamento }).fetchall() 

            for p in self.pagamento:
                return p     
            for valor in self.aluguel:
                return valor        
            for endereco in self.cliente.enderecoCL:
                return endereco 
            
            return self.cliente

    
        
    def visual_Endereco(self):
        with _Session() as session:
            self.endereco = session.query(Endereco).first()            
            return self.endereco.id_endereco  
   
            
    def visual_Agencia(self,nome):
        with _Session() as session:
            self.agencia = session.query(Agencia).filter(Agencia.nome == nome).first()
            return self.agencia                     

     

    #Funcoes que apenas o Admin pode utilizar                    

    def visual_Empregado(self,cpf):
        with _Session() as session:
            self.empregado = session.query(Empregado).filter(Empregado.cpf == cpf).first()
            return self.empregado   

    def visual_Departamento(self,nome):
        with _Session() as session:
            self.departamento = session.query(Departamento).filter(Departamento.nome == nome).first()
            return self.departamento    

    def visual_Fornecedor(self,cnpj):
        with _Session() as session:
            self.fornecedor = session.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first()
            return self.fornecedor          

    def visual_Servico(self,nome):
        with _Session() as session:
            self.servico = session.query(Servico).filter(Servico.nome == nome).first()
             
            return self.servico 

    def visual_Veiculo(self,placa):
        with _Session() as session:     
            self.veiculos = session.query(Veiculo).filter(Servico.placa == placa).first()
            self.aluguel = session.execute(text('CALL visualizar_aluguel(:id)'),  {"id":self.veiculos.id_veiculos }).fetchall() 

            #linha de codigo que pode ser adicionada --> self.alugueis = session.execute(text('CALL visualizar_veiculoaluguel()')).fetchall() 
            

            return self.veiculos,self.aluguel


    
    # DELETAR
    def DELETAR_cliente(self,senha):
        with _Session() as session:
            self.cliente = session.query(Cliente).filter(Cliente.senha == senha).firsh()    
            if self.cliente:
                session.delete(self.cliente)
                session.commit()    
            else:
                return 'Cliente nao foi encontrado'

    def DELETAR_veiculo(self,placa):
        with _Session() as session:
            self.veiculo =  session.get(Veiculo, placa)
            if self.veiculo:
                session.delete(self.veiculo)
                session.commit()
            else:
                return 'Veiculo nao foi encontrado' 

    def DELETAR_agencia(self,nome):
        with _Session() as session:
            self.agencia = session.get(Agencia,nome)          
            if self.agencia: 
                session.delete(self.agencia)
                session.commit()

    def DELETAR_fornecedor(self,cnpj):
        with _Session() as session:
            self.fornecedor =  session.get(Fornecedor, cnpj)  
            if self.fornecedor:
                session.delete(self.fornecedor)
                session.commit()

    #Atualizacao  
    def Atualizar_cliente(self,senha, coluna, novo_valor):
        with _Session() as session:
           self.cliente = session.query(Cliente).filter(Cliente.senha == senha).first() 
           
           if not self.cliente:
               return 'Cliente nao encontrado '

           setattr(self.cliente, coluna, novo_valor)
           session.commit()

    def Atualizar_endereco_cliente(self,senha, coluna, novo_valor):
        with _Session() as session:
           self.cliente = session.query(Cliente).filter(Cliente.senha == senha).first()
           self.endereco = session.query(Endereco).filter(Endereco.id_endereco == self.cliente.id_endereco).first() 
           
           if not self.endereco:
               return 'endereco nao encontrado '

           setattr(self.endereco, coluna, novo_valor)
           session.commit() 

    def Atualizar_endereco_agencia(self,nome, coluna, novo_valor):
        with _Session() as session:
           self.agencia = session.query(Agencia).filter(Agencia.nome == nome).first()
           if not self.agencia:
               return 'Agencia nao encontrada' 
           self.endereco = session.query(Endereco).filter(Endereco.id_endereco == self.agencia.id_agencia).first() 
           
           if not self.endereco:
               return 'endereco nao encontrado'

           setattr(self.endereco, coluna, novo_valor)
           session.commit()              

    def Atualizar_servico(self,nome, coluna, novo_valor):
        with _Session() as session:
           self.servico = session.query(Servico).filter(Servico.nome == nome).first()
           if not self.servico:
               return 'servico nao encontrada' 

           setattr(self.servico, coluna, novo_valor)
           session.commit()  

    def Atualizar_aluguel(self,senha, coluna, novo_valor):
        with _Session() as session:
           self.cliente = session.query(Cliente).filter(Cliente.senha == senha).first()
           if not self.agencia:
               return 'Agencia nao encontrada' 
           self.aluguel = session.query(Aluguel).filter(Aluguel.id_aluguel == self.cliente.id_cliente).first()
           if not self.aluguel:
               return 'servico nao encontrada' 

           setattr(self.aluguel, coluna, novo_valor)
           session.commit()

    def Atualizar_pagamento(self,senha, coluna, novo_valor):
        with _Session() as session:
           self.cliente = session.query(Cliente).filter(Cliente.senha == senha).first()
           if not self.agencia:
               return 'Agencia nao encontrada' 
           self.aluguel = session.query(Aluguel).filter(Aluguel.id_aluguel == self.cliente.id_cliente).first()
           if not self.aluguel:
               return 'servico nao encontrada' 

           setattr(self.aluguel, coluna, novo_valor)
           session.commit()
           
       
#fotos_b = b'foto'    
#data_nascimento = '01/05/2008'
#operacao.add_Endereco('logradouro','bairro',31,'cep','complemento','cidade','estado')      
#operacao.add_Cliente('nome','telefone','email',fotos_b,'senha','cpf','2008-05-01','cnh','g',operacao.visual_Endereco())
    
