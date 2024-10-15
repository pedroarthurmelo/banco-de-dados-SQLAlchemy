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

#Função para criar o banco de dados, caso não exista
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

#apagar o banco de dados
def delete_database():
    connection = pymysql.connect(host=host, user=usuario, password=senha)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {nome_do_banco};")
            print(f"Banco de dados '{nome_do_banco}' deletado, se existia.")
    finally:
        connection.close()

#apagar o banco de dados
delete_database()

# Fazendo uma URL para criar a conexão no engine
url = f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_do_banco}'

# Conectando ao banco de dados
engine = sqlalchemy.create_engine(url, echo=True)

# Definindo a base para as tabelas
base = declarative_base()

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
    apartamento = relationship("Apartamento", back_populates="apolice", uselist=False)  # Alterado para um relacionamento one-to-one
    
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

# Criando uma sessão
Sessao = sessionmaker(bind=engine)
sessao = Sessao()


# Função para adicionar um cliente
def adicionar_cliente(sessao, cpf, nome, endereco, telefone, email):
    cliente = Cliente(cpf=cpf, nome=nome, endereco=endereco, telefone=telefone, email=email)
    try:
        sessao.add(cliente)
        sessao.commit()
        print(f"Cliente {nome} adicionado com sucesso.")
    except Exception as e:
        sessao.rollback()
        print(f"Erro ao adicionar cliente: {e}")

# Exemplo: Adicionar um cliente
adicionar_cliente(sessao, '12345678901', 'Carlos Silva', 'Rua A, 123', '99999-1234', 'carlos@email.com')

# Função para adicionar uma Apólice
def adicionar_apolice(sessao, fk_cliente, data_contrato, contato, assinatura):
    apolice = Apolice(fk_cliente=fk_cliente, data_contrato=data_contrato, contato=contato, assinatura=assinatura)
    try:
        sessao.add(apolice)
        sessao.commit()
        print(f"Apolice adicionada com sucesso.")
    except Exception as e:
        sessao.rollback()
        print(f"Erro ao adicionar apolice: {e}")

cliente1 = sessao.query(Cliente).filter_by(cpf='12345678901').first()  
if cliente1:
    adicionar_apolice(sessao, cliente1.id, '2024-01-15', 'Contato Apólice 1', 'Carlos Silva')

# Função para adicionar um Apartamento
def adicionar_apartamento(sessao, endereco, andar, tipo_ap, numero_ap, apolice_id):
    apartamento = Apartamento(endereco=endereco, andar=andar, tipo_ap=tipo_ap, numero_ap=numero_ap, apolice_id=apolice_id)
    try:
        sessao.add(apartamento)
        sessao.commit()
        print(f"Apartamento adicionado com sucesso.")
    except Exception as e:
        sessao.rollback()
        print(f"Erro ao adicionar apartamento: {e}")

# Adicionando um Apartamento para a Apólice criada
apolice1 = sessao.query(Apolice).filter(Apolice.fk_cliente == cliente1.id).first()
if apolice1:
    adicionar_apartamento(sessao, 'Rua B, 456', 3, 'Residencial', 101, apolice1.id)

# Função para adicionar um Acidente
def adicionar_acidente(sessao, descricao, data_ocorrencia, valor_acidente, tipo_acidente, apartamento_id):
    acidente = Acidente(descricao=descricao, data_ocorrencia=data_ocorrencia, valor_acidente=valor_acidente, tipo_acidente=tipo_acidente, fk_apartamento=apartamento_id)
    try:
        sessao.add(acidente)
        sessao.commit()
        print(f"Acidente adicionado com sucesso.")
    except Exception as e:
        sessao.rollback()
        print(f"Erro ao adicionar acidente: {e}")

apartamento1 = sessao.query(Apartamento).filter(Apartamento.apolice_id == apolice1.id).first()
if apartamento1:
    adicionar_acidente(sessao, 'Incêndio no apartamento', '2024-02-15', 15000.00, 'Incêndio', apartamento1.id)


# Função para ler todos os clientes
def ler_clientes(sessao):
    clientes = sessao.query(Cliente).all()
    for cliente in clientes:
        print(cliente)

# Função para ler um cliente pelo ID
def ler_cliente_por_id(sessao, cliente_id):
    cliente = sessao.query(Cliente).filter(Cliente.id == cliente_id).one_or_none()
    if cliente:
        print(cliente)
    else:
        print(f"Cliente com ID {cliente_id} não encontrado.")

# Função para ler todas as apólices
def ler_apolices(sessao):
    apolices = sessao.query(Apolice).all()
    for apolice in apolices:
        print(apolice)

# Função para ler uma apólice pelo ID
def ler_apolice_por_id(sessao, apolice_id):
    apolice = sessao.query(Apolice).filter(Apolice.id == apolice_id).one_or_none()
    if apolice:
        print(apolice)
    else:
        print(f"Apolice com ID {apolice_id} não encontrada.")

# Função para ler todos os apartamentos
def ler_apartamentos(sessao):
    apartamentos = sessao.query(Apartamento).all()
    for apartamento in apartamentos:
        print(apartamento)

# Função para ler um apartamento pelo ID
def ler_apartamento_por_id(sessao, apartamento_id):
    apartamento = sessao.query(Apartamento).filter(Apartamento.id == apartamento_id).one_or_none()
    if apartamento:
        print(apartamento)
    else:
        print(f"Apartamento com ID {apartamento_id} não encontrado.")

# Função para ler todos os acidentes
def ler_acidentes(sessao):
    acidentes = sessao.query(Acidente).all()
    for acidente in acidentes:
        print(acidente)

# Função para ler um acidente pelo ID
def ler_acidente_por_id(sessao, acidente_id):
    acidente = sessao.query(Acidente).filter(Acidente.id == acidente_id).one_or_none()
    if acidente:
        print(acidente)
    else:
        print(f"Acidente com ID {acidente_id} não encontrado.")

# Exemplo de uso das funções de leitura
print("\nLista de Clientes:")
ler_clientes(sessao)

print("\nCliente pelo ID 1:")
ler_cliente_por_id(sessao, 1)

print("\nLista de Apólices:")
ler_apolices(sessao)

print("\nApolice pelo ID 1:")
ler_apolice_por_id(sessao, 1)

print("\nLista de Apartamentos:")
ler_apartamentos(sessao)

print("\nApartamento pelo ID 1:")
ler_apartamento_por_id(sessao, 1)

print("\nLista de Acidentes:")
ler_acidentes(sessao)

print("\nAcidente pelo ID 1:")
ler_acidente_por_id(sessao, 1)


# Função para atualizar um cliente
def atualizar_cliente(sessao, cliente_id, novos_dados):
    cliente = sessao.query(Cliente).filter(Cliente.id == cliente_id).one_or_none()
    if cliente:
        for key, value in novos_dados.items():
            setattr(cliente, key, value)
        sessao.commit()
        print(f"Cliente {cliente_id} atualizado com sucesso.")
    else:
        print(f"Cliente {cliente_id} não encontrado.")

# Atualizando cliente
cliente1 = sessao.query(Cliente).filter_by(cpf='12345678901').first()
if cliente1:
    novos_dados_cliente = {
        'nome': 'Carlos Silva Atualizado',
        'endereco': 'Rua A, 456',
        'telefone': '98888-8888',
        'email': 'carlos_atualizado@email.com'
    }
    atualizar_cliente(sessao, cliente1.id, novos_dados_cliente)


# Função para atualizar uma Apólice
def atualizar_apolice(sessao, apolice_id, novos_dados):
    apolice = sessao.query(Apolice).filter(Apolice.id == apolice_id).one_or_none()
    if apolice:
        for key, value in novos_dados.items():
            setattr(apolice, key, value)
        sessao.commit()
        print(f"Apolice {apolice_id} atualizada com sucesso.")
    else:
        print(f"Apolice {apolice_id} não encontrada.")


# Atualizando Apólice
apolice1 = sessao.query(Apolice).filter(Apolice.fk_cliente == cliente1.id).first()
if apolice1:
    novos_dados_apolice = {
        'contato': 'Contato Atualizado',
        'assinatura': 'Carlos Silva Atualizado'
    }
    atualizar_apolice(sessao, apolice1.id, novos_dados_apolice)


# Função para atualizar um Apartamento
def atualizar_apartamento(sessao, apartamento_id, novos_dados):
    apartamento = sessao.query(Apartamento).filter(Apartamento.id == apartamento_id).one_or_none()
    if apartamento:
        for key, value in novos_dados.items():
            setattr(apartamento, key, value)
        sessao.commit()
        print(f"Apartamento {apartamento_id} atualizado com sucesso.")
    else:
        print(f"Apartamento {apartamento_id} não encontrado.")

# Atualizando Apartamento
apartamento1 = sessao.query(Apartamento).filter(Apartamento.apolice_id == apolice1.id).first()
if apartamento1:
    novos_dados_apartamento = {
        'endereco': 'Rua B, 789',
        'andar': 4,
        'tipo_ap': 'Comercial',
        'numero_ap': 102
    }
    atualizar_apartamento(sessao, apartamento1.id, novos_dados_apartamento)


# Função para atualizar um Acidente
def atualizar_acidente(sessao, acidente_id, novos_dados):
    acidente = sessao.query(Acidente).filter(Acidente.id == acidente_id).one_or_none()
    if acidente:
        for key, value in novos_dados.items():
            setattr(acidente, key, value)
        sessao.commit()
        print(f"Acidente {acidente_id} atualizado com sucesso.")
    else:
        print(f"Acidente {acidente_id} não encontrado.")


# Atualizando Acidente
acidente1 = sessao.query(Acidente).filter(Acidente.fk_apartamento == apartamento1.id).first()
if acidente1:
    novos_dados_acidente = {
        'descricao': 'Incêndio no apartamento - Atualizado',
        'valor_acidente': 20000.00,
        'tipo_acidente': 'Incêndio - Atualizado'
    }
    atualizar_acidente(sessao, acidente1.id, novos_dados_acidente)


#Função para deletar um cliente
def deletar_cliente(sessao, cliente_id):
    cliente = sessao.query(Cliente).filter(Cliente.id == cliente_id).one_or_none()
    if cliente:
        sessao.delete(cliente)
        sessao.commit()
        print(f"Cliente {cliente_id} deletado com sucesso.")
    else:
        print(f"Cliente {cliente_id} não encontrado.")

# Deletar cliente
deletar_cliente(sessao, cliente1.id)

# Função para deletar uma Apólice
def deletar_apolice(sessao, apolice_id):
    apolice = sessao.query(Apolice).filter(Apolice.id == apolice_id).one_or_none()
    if apolice:
        sessao.delete(apolice)
        sessao.commit()
        print(f"Apolice {apolice_id} deletada com sucesso.")
    else:
        print(f"Apolice {apolice_id} não encontrada.")

# Função para deletar um Apartamento
def deletar_apartamento(sessao, apartamento_id):
    apartamento = sessao.query(Apartamento).filter(Apartamento.id == apartamento_id).one_or_none()
    if apartamento:
        sessao.delete(apartamento)
        sessao.commit()
        print(f"Apartamento {apartamento_id} deletado com sucesso.")
    else:
        print(f"Apartamento {apartamento_id} não encontrado.")

# Deletar Apartamento
deletar_apartamento(sessao, apartamento1.id)

# Função para deletar um Acidente
def deletar_acidente(sessao, acidente_id):
    acidente = sessao.query(Acidente).filter(Acidente.id == acidente_id).one_or_none()
    if acidente:
        sessao.delete(acidente)
        sessao.commit()
        print(f"Acidente {acidente_id} deletado com sucesso.")
    else:
        print(f"Acidente {acidente_id} não encontrado.")

# Deletar Acidente
deletar_acidente(sessao, acidente1.id)


# Fechando a sessão
sessao.close()

