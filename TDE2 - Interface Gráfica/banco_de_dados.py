import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship, sessionmaker
import pymysql

# Versão do SQLAlchemy
versao = sqlalchemy.__version__
print(f"Versão do SQLAlchemy: {versao}")

# Dados de conexão
usuario = 'root'
senha = ''
host = 'localhost'
porta = '3306'
nome_do_banco = 'familia'

# Função para criar o banco de dados, caso não exista
def create_database():
    connection = pymysql.connect(host=host, user=usuario, password=senha)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nome_do_banco};")
            print(f"Banco de dados '{nome_do_banco}' criado ou já existe.")
    finally:
        connection.close()

# Criando o banco de dados, se não existir
create_database()

# Fazendo uma URL para criar a conexão no engine
url = f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_do_banco}'

# Conectando ao banco de dados
engine = sqlalchemy.create_engine(url, echo=True)

# Definindo a base para as tabelas
base = declarative_base()

# Mapeando as tabelas

# Tabela Cliente
class Cliente(base):
    __tablename__ = 'cliente'
    
    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    nome = Column(String(50))
    endereco = Column(String(100))
    telefone = Column(String(15))
    email = Column(String(50))
    
    # Relacionamento com Apólice
    apolices = relationship("Apolice", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(nome={self.nome}, cpf={self.cpf})>"

# Tabela Apólice
class Apolice(base):
    __tablename__ = 'apolice'
    
    id = Column(Integer, primary_key=True)
    fk_cliente = Column(Integer, ForeignKey('cliente.id'))
    data_contrato = Column(Date)
    contato = Column(String(50))
    assinatura = Column(String(50))
    
    # Relacionamento com Cliente e Apartamento
    cliente = relationship("Cliente", back_populates="apolices")
    apartamento = relationship("Apartamento", back_populates="apolice")
    
    def __repr__(self):
        return f"<Apolice(id={self.id}, data_contrato={self.data_contrato})>"

# Tabela Acidente
class Acidente(base):
    __tablename__ = 'acidente'
    
    id = Column(Integer, primary_key=True)
    descricao = Column(String(200))
    data_ocorrencia = Column(Date)
    valor_acidente = Column(Float)
    tipo_acidente = Column(String(50))
    
    # Relacionamento com Apartamento
    fk_apartamento = Column(Integer, ForeignKey('apartamento.id'))
    apartamento = relationship("Apartamento", back_populates="acidentes")
    
    def __repr__(self):
        return f"<Acidente(descricao={self.descricao}, data_ocorrencia={self.data_ocorrencia})>"

# Tabela Apartamento
class Apartamento(base):
    __tablename__ = 'apartamento'
    
    id = Column(Integer, primary_key=True)
    endereco = Column(String(100))
    andar = Column(Integer)
    tipo_ap = Column(String(50))
    numero_ap = Column(Integer)
    
    # Relacionamento com Apólice e Acidente
    apolice_id = Column(Integer, ForeignKey('apolice.id'))
    apolice = relationship("Apolice", back_populates="apartamento")
    acidentes = relationship("Acidente", back_populates="apartamento")
    
    def __repr__(self):
        return f"<Apartamento(endereco={self.endereco}, numero_ap={self.numero_ap})>"

# Criando as tabelas no banco de dados
base.metadata.create_all(engine)

# Criando instâncias de exemplo
cliente1 = Cliente(cpf='12345678901', nome='Carlos Silva', endereco='Rua A, 123', telefone='99999-1234', email='carlos@email.com')
apolice1 = Apolice(data_contrato='2024-01-15', contato='Contato Apólice 1', assinatura='Carlos Silva')
apartamento1 = Apartamento(endereco='Rua B, 456', andar=3, tipo_ap='Residencial', numero_ap=101)
acidente1 = Acidente(descricao='Incêndio no apartamento', data_ocorrencia='2024-05-10', valor_acidente=50000.00, tipo_acidente='Incêndio')

# Associando o relacionamento
apolice1.cliente = cliente1
apartamento1.apolice = apolice1
acidente1.apartamento = apartamento1

# Criando uma sessão
Sessao = sessionmaker(bind=engine)
sessao = Sessao()

# Adicionando e commitando as instâncias
sessao.add_all([cliente1, apolice1, apartamento1, acidente1])
sessao.commit()

# Consultando os dados
for cliente in sessao.query(Cliente).order_by(Cliente.id):
    print(cliente)

for apolice in sessao.query(Apolice).order_by(Apolice.id):
    print(apolice)

for apartamento in sessao.query(Apartamento).order_by(Apartamento.id):
    print(apartamento)

for acidente in sessao.query(Acidente).order_by(Acidente.id):
    print(acidente)
