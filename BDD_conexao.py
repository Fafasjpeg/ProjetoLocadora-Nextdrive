from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, Date, Time, ForeignKey, text
from sqlalchemy.orm import declarative_base,sessionmaker, relationship

Engine = create_engine("mysql+pymysql://root:gbs1@localhost:3306/locacaocarro")
Base = declarative_base()
_Session = sessionmaker(Engine)
class Agencia(Base):
    __tablename__ = 'Agencia'

    id_agencia = Column(Integer, primary_key=True)
    nome = Column(String(255),unique=True )
    telefone = Column(String(15),unique=True )
    email = Column(String(255), unique=True )
    id_endereco = Column(Integer, ForeignKey('Endereco.id_endereco'))
        


    enderecoAG = relationship('Endereco', back_populates='agenciaEN')
    departamento = relationship('AgenciaDepartamento', back_populates='agencias')
    aluguel = relationship('AgenciaAluguel', back_populates='alugueis')

class Aluguel(Base):
    __tablename__ = 'Aluguel'    

    id_aluguel = Column(Integer, primary_key=True )
    data_retirada = Column(Date )
    hora_retirada = Column(Time)
    data_aluguel = Column(Date)
    data_devolutiva = Column(Date)
    quantidade_dias = Column(Integer)
    plano = Column(String(255))
    id_cliente = Column(Integer, ForeignKey('Cliente.id_cliente'), primary_key=True)
    id_veiculo = Column(Integer, ForeignKey('Veiculo.id_veiculo'), primary_key=True)

    agencia = relationship('AgenciaAluguel', back_populates='agencias')
    clienteAL = relationship('ClienteAluguel', back_populates='aluguelCL')
    veiculoAL = relationship('Veiculo', back_populates='aluguelVE')
    pagamentoAL = relationship('Pagamento', back_populates='aluguelPA')

 


class AgenciaAluguel(Base):
    __tablename__ = 'AgenciaAluguel'    

    id_aluguel = Column(Integer, ForeignKey('Aluguel.id_aluguel'), primary_key=True)
    id_agencia = Column(Integer, ForeignKey('Agencia.id_agencia'), primary_key=True)

    alugueis = relationship('Agencia', back_populates='aluguel')
    agencias = relationship('Aluguel', back_populates='agencia') 

class Cargo(Base):
    __tablename__ = 'Cargo'    

    id_cargo = Column(Integer, primary_key=True)
    nome = Column(String(255))
    funcao = Column(String(255))

    empregadoCA = relationship('Empregado', back_populates = 'cargoEM')

class Cliente(Base):
    __tablename__ = 'Cliente'

    id_cliente = Column(Integer, primary_key=True)
    nome = Column(String(255),unique=True )
    telefone = Column(String(15),unique=True )
    email = Column(String(255), unique=True )  
    foto = Column(LargeBinary(255))  
    senha = Column(String(255),unique=True)
    cpf = Column(String(11),unique=True)
    data_de_nasci = Column(Date)
    cnh = Column(String(11), unique=True)
    genero = Column(String(1))
    id_endereco = Column(Integer,ForeignKey('Endereco.id_endereco'))

    enderecoCL = relationship('Endereco', back_populates='clienteEN')
    aluguelL =  relationship('ClienteAluguel', back_populates='clienteL')

class ClienteAluguel(Base):
    __tablename__ = 'ClienteAluguel'

    id_cliente =  Column(Integer, ForeignKey('Cliente.id_cliente'), primary_key=True) 
    id_aluguel = Column(Integer,ForeignKey('Aluguel.id_aluguel'), primary_key=True )


    aluguelCL = relationship('Aluguel', back_populates='clienteAL')
    clienteL  = relationship('Cliente', back_populates='aluguelL' )
    

class Departamento(Base):
    __tablename__ = 'Departamento'

    id_departamento = Column(Integer, primary_key=True)
    nome = Column(String(255),unique=True )
    descricao = Column(String(255))
    funcao = Column(String(255))
    situacao = Column(String(10))
    complemento = Column(String(255))

    agencia = relationship('AgenciaDepartamento', back_populates='departamentos')
    empregadoDE= relationship('Empregado', back_populates='departamentoEM')

   

class AgenciaDepartamento(Base):
    __tablename__ = 'AgenciaDepartamento' 

    id_agencia = Column(Integer, ForeignKey('Agencia.id_agencia'), primary_key= True)   
    id_departamento = Column(Integer,ForeignKey('Departamento.id_departamento'), primary_key=True)

    agencias = relationship('Agencia', back_populates='departamento')
    departamentos = relationship('Departamento', back_populates='agencia')


class  Empregado(Base):
    __tablename__ = 'Empregado'

    id_empregado = Column(Integer, primary_key=True)  
    nome  = Column(String(255), unique=True)
    cpf = Column(String(11), unique=True)
    data_de_nasci = Column(Date)
    telefone = Column(String(15), unique=True)
    salario = Column(Float)
    email =  Column(String(255), unique=True)
    genero = Column(String(1))
    id_endereco = Column(Integer,ForeignKey('Endereco.id_endereco'))
    id_departamento = Column(Integer,ForeignKey('Departamento.id_departamento'))
    id_cargo = Column(Integer,ForeignKey('Cargo.id_cargo'))

    enderecoEM = relationship('Endereco', back_populates='empregadoEN')
    departamentoEM = relationship('Departamento', back_populates='empregadoDE')
    cargoEM = relationship('Cargo', back_populates='empregadoCA')


class Endereco(Base):
    __tablename__ = 'Endereco'

    id_endereco = Column(Integer, primary_key=True)
    logradouro = Column(String(255))
    bairro = Column(String(255))
    numero = Column(Integer)
    cep = Column(String(255))
    complemento = Column(String(255))
    cidade = Column(String(255))
    estado = Column(String(255))
    

    agenciaEN = relationship('Agencia', back_populates='enderecoAG')
    clienteEN = relationship('Cliente', back_populates='enderecoCL')
    empregadoEN = relationship('Empregado', back_populates='enderecoEM')
    fornecedorEN = relationship('Fornecedor', back_populates='enderecoFO')


class Fornecedor(Base):
    __tablename__ = 'Fornecedor'

    id_fornecedor = Column(Integer, primary_key=True)
    cnpj =  Column(String(18), unique=True)  
    razao_social = Column(String(255))
    nome_fantasia = Column(String(255), unique=True)
    foto = Column(LargeBinary(255))
    id_endereco =  Column(Integer, ForeignKey('Endereco.id_endereco'))

    enderecoFO = relationship('Endereco', back_populates='fornecedorEN')
    servicoFO = relationship('Servico', back_populates='fornecedorSE')
    
class Pagamento(Base):
    __tablename__ = 'Pagamento'

    id_pagamento = Column(Integer, primary_key=True)
    forma_pagamento =  Column(String(255))  
    valor_multa = Column(Float)
    valor_aluguel = Column(Float)
    valor_servicos = Column(Float)   
    valor_total = Column(Float)  
    observacoes = Column(String(255)) 
    status_pagamento = Column(String(1))
    id_aluguel =  Column(Integer, ForeignKey('Aluguel.id_aluguel'))

    aluguelPA = relationship('Aluguel', back_populates='pagamentoAL')

class Servico(Base):
    __tablename__ = 'Servico'

    id_servico = Column(Integer, primary_key=True)
    tipo_servico =  Column(String(255))  
    nome = Column(String(255))
    preco = Column(Float)
    id_fornecedor =  Column(Integer, ForeignKey('Fornecedor.id_fornecedor'))


    fornecedorSE =  relationship('Fornecedor', back_populates='servicoFO')
    veiculo = relationship('VeiculoServico', back_populates='servicos') 
    
class Veiculo(Base):
    __tablename__ = 'Veiculo'

    id_veiculo = Column(Integer, primary_key=True)
    marca =  Column(String(255))  
    modelo = Column(String(255))
    placa = Column(String(7))
    cor = Column(String(255))
    quilometragem = Column(Float)
    valor_diario = Column(Float)
    data_aquisicao = Column(Date)
    categoria = Column(String(255))

    aluguelVE = relationship('Aluguel', back_populates='veiculoAL')
    servico = relationship('VeiculoServico', back_populates='veiculos')

class VeiculoServico(Base):
    __tablename__ = 'VeiculoServico'

    id_veiculo = Column(Integer, ForeignKey('Veiculo.id_veiculo'), primary_key=True)
    id_servico = Column(Integer, ForeignKey('Servico.id_servico'), primary_key=True)

    veiculos = relationship('Veiculo', back_populates='servico')
    servicos = relationship('Servico', back_populates='veiculo')

#with _Session() as session:
#    agencia = Agencia(nome='funcionou', telefone="119856566543456",email='gdfgadfdgszfhshg')
#    session.add(agencia)
#    session.commit()
Base.metadata.create_all(Engine)    