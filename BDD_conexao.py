from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey,
    Date, Float, LargeBinary, Table, Numeric, Boolean, Time
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Conexão e base (mantive exatamente como você pediu)
Engine = create_engine("mysql+pymysql://root:2008fsfc@localhost:3306/locacaocarro")
Base = declarative_base()
_Session = sessionmaker(bind=Engine)

# --- Tabelas de associação ---
AgenciaDepartamento = Table(
    'AgenciaDepartamento',
    Base.metadata,
    Column('id_agencia', Integer, ForeignKey('agencia.id_agencia'), primary_key=True),
    Column('id_departamento', Integer, ForeignKey('departamento.id_departamento'), primary_key=True)
)

VeiculoServico = Table(
    'VeiculoServico',
    Base.metadata,
    Column('id_veiculo', Integer, ForeignKey('veiculo.id_veiculo'), primary_key=True),
    Column('id_servico', Integer, ForeignKey('servico.id_servico'), primary_key=True)
)

# --- Classes principais ---

class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    data_de_nasci = Column(Date, nullable=False)   # seu nome existente
    cnh = Column(String(11), nullable=False)
    genero = Column(String(1), nullable=False)
    foto = Column(LargeBinary, nullable=True)
    cpf = Column(String(11), unique=True, nullable=False)
    telefone = Column(String(15), nullable=False)
    id_endereco = Column(Integer, ForeignKey('endereco.id_endereco'), nullable=False)

    # relacionamentos (Cliente -> Endereco, Aluguel, Pagamento via Aluguel)
    endereco = relationship("Endereco", back_populates="clientes")
    alugueis = relationship("Aluguel", back_populates="cliente")
    # pagamentos acessíveis via aluguel.pagamentos

class Endereco(Base):
    __tablename__ = 'endereco'

    id_endereco = Column(Integer, primary_key=True)
    logradouro = Column(String(255), nullable=False)
    numero = Column(Integer, nullable=False)
    bairro = Column(String(255), nullable=False)
    cep = Column(String(8), nullable=False)
    complemento = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)

    clientes = relationship("Cliente", back_populates="endereco")
    fornecedores = relationship("Fornecedor", back_populates="endereco")
    agencias = relationship("Agencia", back_populates="endereco")
    empregados = relationship("Empregado", back_populates="endereco")


class Fornecedor(Base):
    __tablename__ = 'fornecedor'

    id_fornecedor = Column(Integer, primary_key=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    razaosocial = Column(String(100), nullable=False)   
    nome_fantasia = Column(String(100), nullable=True)   
    foto = Column(LargeBinary, nullable=True)
    id_endereco = Column(Integer, ForeignKey('endereco.id_endereco'), nullable=False)

    endereco = relationship("Endereco", back_populates="fornecedores")
    servicos = relationship("Servico", back_populates="fornecedor")


class Cargo(Base):
    __tablename__ = 'cargo'

    id_cargo = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    funcao = Column(String(255), nullable=True)

    empregados = relationship("Empregado", back_populates="cargo")


class Departamento(Base):
    __tablename__ = 'departamento'

    id_departamento = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=True)
    funcao = Column(String(255), nullable=True)
    complemento = Column(String(255), nullable=True)
    situacao = Column(String(255), nullable=True)

    empregados = relationship("Empregado", back_populates="departamento")
    agencias = relationship("Agencia", secondary=AgenciaDepartamento, back_populates="departamentos")


class Empregado(Base):
    __tablename__ = 'empregado'

    id_empregado = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(255), nullable=False)
    data_de_nasci = Column(Date, nullable=False)  
    genero = Column(String(1), nullable=False)
    telefone = Column(String(15), nullable=False)
    salario = Column(Numeric(9, 2), nullable=False)
    
    id_departamento = Column(Integer, ForeignKey('departamento.id_departamento'), nullable=False)
    id_endereco = Column(Integer, ForeignKey('endereco.id_endereco'), nullable=False)
    id_cargo = Column(Integer, ForeignKey('cargo.id_cargo'), nullable=False)
    
    # criar email e senha pra admin acess

    endereco = relationship("Endereco", back_populates="empregados")
    departamento = relationship("Departamento", back_populates="empregados")
    cargo = relationship("Cargo", back_populates="empregados")


class Agencia(Base):
    __tablename__ = 'agencia'

    id_agencia = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(15), nullable=False)
    email = Column(String(255), nullable=False)           
    id_endereco = Column(Integer, ForeignKey('endereco.id_endereco'), nullable=False)

    endereco = relationship("Endereco", back_populates="agencias")
    departamentos = relationship("Departamento", secondary=AgenciaDepartamento, back_populates="agencias")

    # relacoes com aluguel: retirada e devolucao 
    alugueis_retirada = relationship(
        "Aluguel",
        back_populates="agencia_retirada",
        foreign_keys="Aluguel.id_agencia_retirada"
    )
    alugueis_devolucao = relationship(
        "Aluguel",
        back_populates="agencia_devolucao",
        foreign_keys="Aluguel.id_agencia_devolucao"
    )


class Veiculo(Base):
    __tablename__ = 'veiculo'

    id_veiculo = Column(Integer, primary_key=True)
    valor_diario = Column(Numeric(9, 2), nullable=False) 
    data_aquisicao = Column(Date, nullable=True)
    marca = Column(String(255), nullable=False)
    modelo = Column(String(255), nullable=False)
    placa = Column(String(7), unique=True, nullable=False)
    cor = Column(String(100), nullable=False)
    quilometragem = Column(Integer, nullable=False) 
    categoria = Column(String(255), nullable=False)

    foto = Column(LargeBinary, nullable=True)

    alugueis = relationship("Aluguel", back_populates="veiculo")
    servicos = relationship("Servico", secondary=VeiculoServico, back_populates="veiculos")


class Servico(Base):
    __tablename__ = 'servico'

    id_servico = Column(Integer, primary_key=True)
    tipo_servico = Column(String(100), nullable=True)  
    nome = Column(String(100), nullable=False)
    preco = Column(Numeric(9, 2), nullable=False)
    id_fornecedor = Column(Integer, ForeignKey('fornecedor.id_fornecedor'), nullable=False)

    fornecedor = relationship("Fornecedor", back_populates="servicos")
    veiculos = relationship("Veiculo", secondary=VeiculoServico, back_populates="servicos")


class Aluguel(Base):
    __tablename__ = 'aluguel'

    id_aluguel = Column(Integer, primary_key=True)

    # FKs para agência de retirada e devolução (conforme dicionário)
    id_agencia_retirada = Column(Integer, ForeignKey('agencia.id_agencia'), nullable=False)
    id_agencia_devolucao = Column(Integer, ForeignKey('agencia.id_agencia'), nullable=False)

    data_retirada = Column(Date, nullable=False)
    hora_retirada = Column(Time, nullable=True)
    data_aluguel = Column(Date, nullable=False)
    data_devolutiva = Column(Date, nullable=False)
    quantidade_dias = Column(Integer, nullable=False)
    plano = Column(String(255), nullable=True)

    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    id_veiculo = Column(Integer, ForeignKey('veiculo.id_veiculo'), nullable=False)

    # relacionamentos
    cliente = relationship("Cliente", back_populates="alugueis")
    veiculo = relationship("Veiculo", back_populates="alugueis")

#relacionamentos com agencia pra retirada e devolucao
    agencia_retirada = relationship(
        "Agencia",
        back_populates="alugueis_retirada",
        foreign_keys=[id_agencia_retirada]
    )
    agencia_devolucao = relationship(
        "Agencia",
        back_populates="alugueis_devolucao",
        foreign_keys=[id_agencia_devolucao]
    )

    pagamentos = relationship("Pagamento", back_populates="aluguel")


class Pagamento(Base):
    __tablename__ = 'pagamento'

    id_pagamento = Column(Integer, primary_key=True)
    forma_pagamento = Column(String(100), nullable=False)
    valor_multa = Column(Numeric(9, 2), nullable=True)
    valor_aluguel = Column(Numeric(9, 2), nullable=False)
    valor_servicos = Column(Numeric(9, 2), nullable=True)
    valor_total = Column(Numeric(9, 2), nullable=False)
    observacoes = Column(String(255), nullable=True)
    status_pagamento = Column(Boolean, nullable=False, default=False)
    parcelas = Column(Integer, nullable=False, default=1)

    id_aluguel = Column(Integer, ForeignKey('aluguel.id_aluguel'), nullable=False)

    aluguel = relationship("Aluguel", back_populates="pagamentos")


# cria as tabelas 
# Base.metadata.create_all(Engine)
