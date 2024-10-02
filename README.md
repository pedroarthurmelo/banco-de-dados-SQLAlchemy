# Sistema de Gerenciamento de Músicas com SQLAlchemy

Este código Python define um sistema simples para gerenciar uma coleção de músicas, artistas, álbuns, gêneros, clientes e playlists, utilizando a biblioteca SQLAlchemy para interagir com um banco de dados MySQL.

## Estrutura do Código

O código está dividido em várias partes:

### 1. Configurações do Banco de Dados

- **Importações:** Importa as bibliotecas necessárias do SQLAlchemy para conexão com o banco de dados, mapeamento de objetos (ORM), e manipulação de datas.
  
- **Credenciais:** Define as credenciais de acesso ao banco de dados MySQL (usuário, senha, host, porta e nome do banco).

- **Verificação do Banco de Dados:** Verifica se o banco de dados especificado já existe, criando-o caso contrário.

- **Criação da Engine:** Cria uma engine do SQLAlchemy para conexão com o banco de dados.

- **Base Declarativa:** Define uma classe base `Base` para mapeamento dos objetos Python para tabelas do banco de dados.

### 2. Definição das Classes e Mapeamentos

Classes que representam as tabelas do banco de dados, com suas respectivas colunas e relacionamentos:

- **Cliente:** Armazena informações dos clientes (nome, email, data de nascimento, playlists).

- **Playlist:** Representa uma playlist (nome, data de criação, quantidade de músicas, cliente).

- **Musica:** Contém dados da música (nome, duração, gênero, álbum, single).

- **Album:** Representa um álbum musical (nome, data de lançamento, artista, músicas).

- **Artista:** Armazena informações sobre o artista (nome, país de origem, álbuns).

- **Genero:** Representa um gênero musical (nome, músicas).

- **PlaylistMusica:** Define a relação entre playlists e músicas (playlist, música).

- **Single:** Representa um single (nome, data de lançamento, músicas).

#### Mapeamentos

- Mapeia as classes para tabelas no banco de dados usando decorators `__tablename__` e `Column`.

- **Relacionamentos:** Define relacionamentos entre as tabelas usando `relationship`.

- **Criação das Tabelas:** Cria as tabelas no banco de dados usando `Base.metadata.create_all(engine)`.

### 3. Sessão do Banco de Dados

- **Criação da Sessão:** Cria uma sessão do SQLAlchemy para interagir com o banco de dados.

### 4. Funcionalidades CRUD

#### CREATE (Criação)

Implementa funções para criar novos registros:

- `criar_cliente()`: Cria um novo cliente.

- `criar_playlist()`: Cria uma nova playlist.

- `adicionar_musica()`: Cria uma nova música, permitindo que o usuário escolha o artista, gênero e se a música é um single ou faz parte de um álbum.

- `adicionar_musica_a_playlist()`: Adiciona uma música a uma playlist.

#### READ (Leitura)

Implementa funções para consultar os dados do banco de dados:

- `ler_clientes()`: Lista os clientes cadastrados.

- `ler_playlists()`: Lista as playlists cadastradas.

- `ler_musicas()`: Lista as músicas cadastradas.

- `ler_albuns()`: Lista os álbuns cadastrados.

- `ler_artistas()`: Lista os artistas cadastrados.

- `ler_singles()`: Lista os singles cadastrados.

- `ler_generos()`: Lista os gêneros musicais cadastrados.

- `ler_playlists_e_musicas()`: Lista as playlists e as músicas que elas contêm.

#### UPDATE (Atualização)

Implementa funções para atualizar registros:

- `atualizar_musica()`: Atualiza os dados de uma música.

- `atualizar_playlist()`: Atualiza os dados de uma playlist.

- `atualizar_album()`: Atualiza os dados de um álbum.

- `atualizar_artista()`: Atualiza os dados de um artista.

- `atualizar_cliente_detalhes()`: Atualiza os detalhes de um cliente.

- `atualizar_genero()`: Atualiza os dados de um gênero musical.

#### DELETE (Deleção)

Implementa funções para deletar registros:

- `apagar_cliente()`: Apaga um cliente.

- `apagar_playlist()`: Apaga uma playlist.

- `apagar_musica()`: Apaga uma música.

- `apagar_album()`: Apaga um álbum.

- `apagar_artista()`: Apaga um artista.

- `apagar_genero()`: Apaga um gênero musical.

- `apagar_single()`: Apaga um single.

- `deletar_banco_de_dados()`: Exclui o banco de dados inteiro.

### 5. Menus

- **Menu de Criação:** Menu para criar novos registros.

- **Menu de Leitura:** Menu para consultar os dados.

- **Menu de Atualização:** Menu para atualizar os dados.

- **Menu de Deleção:** Menu para excluir os dados.

- **Menu Principal:** Menu principal que permite navegar entre as demais opções.

### 6. Execução do Código

O código executa o menu principal e mantém o programa rodando até que o usuário escolha sair. A sessão do banco de dados é fechada ao final.

## Código:

```python
import sqlalchemy
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from datetime import date, datetime

# PARTE 1: Configurações do Banco de Dados
usuario = 'root'
senha = ''
host = 'localhost'
porta = '3306'
nome_do_banco = 'colecao_musicas'

versao = sqlalchemy.__version__
print("Versão do SQLAlchemy:",versao)

url_sem_banco = f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}'

engine_sem_banco = create_engine(url_sem_banco, echo=False)

def banco_existe(nome_do_banco):
    """Verifica se o banco de dados já existe."""
    query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{nome_do_banco}'"
    with engine_sem_banco.connect() as conexao:
        resultado = conexao.execute(text(query)).fetchone()
    return resultado is not None

def criar_banco_de_dados(nome_do_banco):
    """Cria o banco de dados se não existir."""
    with engine_sem_banco.connect() as conexao:
        conexao.execute(text(f"CREATE DATABASE {nome_do_banco}"))
        print(f"Banco de dados '{nome_do_banco}' criado.")

while True:
    if banco_existe(nome_do_banco):
        print(f"O banco de dados '{nome_do_banco}' já existe.")
        break

    print(f"O banco de dados '{nome_do_banco}' será criado se não existir.")
    opcao = input("Deseja continuar? {1} Sim / {2} Não: ")

    if opcao == '1':
        criar_banco_de_dados(nome_do_banco)
        break
    elif opcao == '2':
        print("ADEUS")
        exit()
    else:
        print("Opção inválida. Por favor, escolha {1} ou {2}.")

url_com_banco = f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_do_banco}'
engine = create_engine(url_com_banco, echo=False)

# Base declarativa para mapeamento
Base = declarative_base()

# PARTE 2: Definição das Classes e Mapeamentos
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    nome = Column(String(50))
    email = Column(String(50))
    data_nasc = Column(Date)
    playlists = relationship("Playlist", back_populates="cliente")

class Playlist(Base):
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    data_criacao = Column(Date)
    quantidade_musicas = Column(Integer)
    fk_id_cliente = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Cliente", back_populates="playlists")
    musicas = relationship("PlaylistMusica", back_populates="playlist")

class Musica(Base):
    __tablename__ = 'musicas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    duracao = Column(Integer)
    fk_id_genero = Column(Integer, ForeignKey('generos.id'))
    fk_id_album = Column(Integer, ForeignKey('albuns.id'))
    fk_id_single = Column(Integer, ForeignKey('singles.id'), nullable=True)
    album = relationship("Album", back_populates="musicas")
    genero = relationship("Genero", back_populates="musicas")
    single = relationship("Single", back_populates="musicas")

class Album(Base):
    __tablename__ = 'albuns'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    data_lancamento = Column(Date)
    fk_id_artista = Column(Integer, ForeignKey('artistas.id'))
    artista = relationship("Artista", back_populates="albuns")
    musicas = relationship("Musica", back_populates="album")

class Artista(Base):
    __tablename__ = 'artistas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    pais_origem = Column(String(50))
    albuns = relationship("Album", back_populates="artista")

class Genero(Base):
    __tablename__ = 'generos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    musicas = relationship("Musica", back_populates="genero")

class PlaylistMusica(Base):
    __tablename__ = 'playlist_musicas'
    id = Column(Integer, primary_key=True)
    fk_id_playlist = Column(Integer, ForeignKey('playlists.id'))
    fk_id_musica = Column(Integer, ForeignKey('musicas.id', ondelete='CASCADE'))
    playlist = relationship("Playlist", back_populates="musicas")
    musica = relationship("Musica", backref='playlists', passive_deletes=True)

class Single(Base):
    __tablename__ = 'singles'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    data_lancamento = Column(Date)
    musicas = relationship("Musica", back_populates="single")

# Criando as tabelas no banco de dados
Base.metadata.create_all(engine)

# Criando a sessão para interagir com o banco
Sessao = sessionmaker(bind=engine)
sessao = Sessao()

#CRUD(CREATE)
def criar_cliente():
    nome = input("Digite o nome do cliente: ")
    email = input("Digite o email do cliente: ")
    
    while True:
        data_nasc_input = input("Digite a data de nascimento do cliente (DD-MM-AAAA): ")
        try:
            data_nasc = datetime.strptime(data_nasc_input, "%d-%m-%Y").date()
            break 
        except ValueError:
            print("Formato inválido. Por favor, insira a data no formato DD-MM-AAAA.")
    
    novo_cliente = Cliente(nome=nome, email=email, data_nasc=data_nasc)
    sessao.add(novo_cliente)
    sessao.commit()
    print(f"Cliente '{nome}' criado com sucesso!")

def criar_playlist():
    nome = input("Digite o nome da playlist: ")
    data_criacao = date.today()
    quantidade_musicas = 0
    clientes = sessao.query(Cliente).all()
    
    if not clientes:
        print("Não há clientes cadastrados.")
        return
    
    print("Selecione um cliente pelo ID:")
    for cliente in clientes:
        print(f"- ID: {cliente.id}, Nome: {cliente.nome}")

    try:
        cliente_id = int(input("Digite o ID do cliente: "))
        cliente = sessao.query(Cliente).filter_by(id=cliente_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if not cliente:
        print("Cliente não encontrado.")
        return

    nova_playlist = Playlist(nome=nome, data_criacao=data_criacao, quantidade_musicas=quantidade_musicas, fk_id_cliente=cliente.id)
    sessao.add(nova_playlist)
    sessao.commit()
    print(f"Playlist '{nome}' criada com sucesso!")


def adicionar_musica():
    nome = input("Digite o nome da música: ")

    while True:
        try:
            duracao = int(input("Digite a duração da música em segundos: "))
            if duracao < 0:
                print("A duração não pode ser negativa. Por favor, insira um valor válido.")
                continue
            break
        except ValueError:
            print("Formato inválido. Por favor, insira um número inteiro para a duração.")

    # Selecionar ou criar artista
    try:
        artista_id = int(input("Digite o ID do artista: "))
        artista = sessao.query(Artista).filter_by(id=artista_id).first()
        
        if not artista:
            artista_nome = input("Artista não encontrado. Digite o nome do artista: ")
            pais_origem = input("Digite o país de origem do artista: ")
            artista = Artista(nome=artista_nome, pais_origem=pais_origem)
            sessao.add(artista)
            sessao.commit()
            print(f"Artista '{artista.nome}' criado com sucesso!")
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return

    # Selecionar ou criar gênero
    try:
        genero_id = int(input("Digite o ID do gênero: "))
        genero = sessao.query(Genero).filter_by(id=genero_id).first()
        
        if not genero:
            genero_nome = input("Gênero não encontrado. Digite o nome do gênero: ")
            genero = Genero(nome=genero_nome)
            sessao.add(genero)
            sessao.commit()
            print(f"Gênero '{genero.nome}' criado com sucesso!")
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return

    tipo = input("A música é uma single ou faz parte de um álbum? (1 para Single, 2 para Álbum): ")
    
    if tipo == '1':
        while True:
            data_lancamento_input = input("Digite a data de lançamento da single (DD-MM-AAAA): ")
            try:
                data_lancamento = datetime.strptime(data_lancamento_input, "%d-%m-%Y").date()
                break
            except ValueError:
                print("Formato inválido. Por favor, insira a data no formato DD-MM-AAAA.")
        
        nova_single = Single(nome=nome, data_lancamento=data_lancamento)
        sessao.add(nova_single)
        sessao.commit()
        
        nova_musica = Musica(nome=nome, duracao=duracao, fk_id_single=nova_single.id, fk_id_genero=genero.id)
        sessao.add(nova_musica)
        sessao.commit()
        print(f"Música '{nome}' adicionada como single com sucesso!")
    
    elif tipo == '2':
        try:
            album_id = int(input("Digite o ID do álbum: "))
            album = sessao.query(Album).filter_by(id=album_id).first()
            
            if not album:
                album_nome = input("Álbum não encontrado. Digite o nome do álbum: ")
                while True:
                    data_lancamento_album_input = input("Digite a data de lançamento do álbum (DD-MM-AAAA): ")
                    try:
                        data_lancamento_album = datetime.strptime(data_lancamento_album_input, "%d-%m-%Y").date()
                        break
                    except ValueError:
                        print("Formato inválido. Por favor, insira a data no formato DD-MM-AAAA.")
                
                album = Album(nome=album_nome, data_lancamento=data_lancamento_album, fk_id_artista=artista.id)
                sessao.add(album)
                sessao.commit()
                print(f"Álbum '{album.nome}' criado com sucesso!")
        except ValueError:
            print("ID inválido. Por favor, insira um número inteiro.")
            return

        nova_musica = Musica(nome=nome, duracao=duracao, fk_id_album=album.id, fk_id_genero=genero.id)
        sessao.add(nova_musica)
        sessao.commit()
        print(f"Música '{nome}' adicionada ao álbum '{album.nome}' com sucesso!")



def adicionar_musica_a_playlist():
    playlists = sessao.query(Playlist).all()
    
    if not playlists:
        print("Não há playlists cadastradas. Por favor, crie uma nova playlist.")
        criar_playlist()
        return

    print("Selecione uma playlist pelo ID:")
    for playlist in playlists:
        print(f"- ID: {playlist.id}, Nome: {playlist.nome}")

    try:
        playlist_id = int(input("Digite o ID da playlist: "))
        playlist = sessao.query(Playlist).filter_by(id=playlist_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return

    if not playlist:
        print("Playlist não encontrada.")
        return

    # Mostrar as músicas cadastradas
    ler_musicas()

    try:
        musica_id = int(input("Digite o ID da música a ser adicionada: "))
        musica = sessao.query(Musica).filter_by(id=musica_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return

    if not musica:
        print("Música não encontrada. Você pode criar uma nova música.")
        adicionar_musica()
    else:
        nova_playlist_musica = PlaylistMusica(fk_id_playlist=playlist.id, fk_id_musica=musica.id)
        sessao.add(nova_playlist_musica)
        playlist.quantidade_musicas += 1
        sessao.commit()
        print(f"Música '{musica.nome}' adicionada à playlist '{playlist.nome}' com sucesso!")


#CRUD(READ)
def ler_clientes():
    clientes = sessao.query(Cliente).all()
    if not clientes:
        print("Não há clientes cadastrados.")
        return
    print("Clientes cadastrados:")
    for cliente in clientes:
        print(f"{cliente.id}: {cliente.nome}")

def ler_playlists():
    playlists = sessao.query(Playlist).all()
    if not playlists:
        print("Não há playlists cadastradas.")
        return
    print("Playlists cadastradas:")
    for playlist in playlists:
        print(f"{playlist.id}: {playlist.nome}")

def ler_musicas():
    musicas = sessao.query(Musica).all()
    if not musicas:
        print("Não há músicas cadastradas.")
        return
    print("Músicas cadastradas:")
    for musica in musicas:
        print(f"{musica.id}: {musica.nome}")

def ler_albuns():
    albuns = sessao.query(Album).all()
    if not albuns:
        print("Não há álbuns cadastrados.")
        return
    print("Álbuns cadastrados:")
    for album in albuns:
        print(f"{album.id}: {album.nome} (Lançado em: {album.data_lancamento})")

def ler_artistas():
    artistas = sessao.query(Artista).all()
    if not artistas:
        print("Não há artistas cadastrados.")
        return
    print("Artistas cadastrados:")
    for artista in artistas:
        print(f"{artista.id}: {artista.nome}")

def ler_singles():
    singles = sessao.query(Single).all()
    if not singles:
        print("Não há singles cadastradas.")
        return
    print("Singles cadastradas:")
    for single in singles:
        print(f"{single.id}: {single.nome} (Lançada em: {single.data_lancamento})")

def ler_generos():
    generos = sessao.query(Genero).all()
    if not generos:
        print("Não há gêneros cadastrados.")
        return
    print("Gêneros cadastrados:")
    for genero in generos:
        print(f"{genero.id}: {genero.nome}")

def ler_playlists_e_musicas():
    playlists = sessao.query(Playlist).all()
    if not playlists:
        print("Não há playlists cadastradas.")
        return
    print("Playlists cadastradas:")
    for playlist in playlists:
        print(f"\nPlaylist ID: {playlist.id}, Nome: {playlist.nome}, Data de Criação: {playlist.data_criacao}")
        print("Músicas nesta playlist:")
        if not playlist.musicas:
            print("Nenhuma música cadastrada nesta playlist.")
        else:
            for playlist_musica in playlist.musicas:
                musica = sessao.query(Musica).filter_by(id=playlist_musica.fk_id_musica).first()
                print(f" - {musica.nome} (ID: {musica.id})")

#CRUD(UPDATE)
def atualizar_musica():
    ler_musicas()  # Mostra as músicas cadastradas
    try:
        musica_id = int(input("Digite o ID da música que deseja atualizar: "))
        musica = sessao.query(Musica).filter_by(id=musica_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if musica:
        novo_nome = input("Digite o novo nome da música (deixe em branco para não alterar): ")
        if novo_nome:
            musica.nome = novo_nome
        
        while True:
            nova_duracao_input = input("Digite a nova duração da música em segundos (deixe em branco para não alterar): ")
            if nova_duracao_input:
                try:
                    nova_duracao = int(nova_duracao_input)
                    if nova_duracao < 0:
                        print("A duração não pode ser negativa. Por favor, insira um valor válido.")
                        continue
                    musica.duracao = nova_duracao
                except ValueError:
                    print("Formato inválido. Por favor, insira um número inteiro para a duração.")
                    continue
                break
            else:
                break

        sessao.commit()
        print(f"Música atualizada com sucesso!")
    else:
        print("Música não encontrada.")



def atualizar_playlist():
    ler_playlists()  # Mostra as playlists cadastradas
    try:
        playlist_id = int(input("Digite o ID da playlist que deseja atualizar: "))
        playlist = sessao.query(Playlist).filter_by(id=playlist_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if playlist:
        novo_nome = input("Digite o novo nome da playlist (deixe em branco para não alterar): ")
        if novo_nome:
            playlist.nome = novo_nome

        sessao.commit()
        print(f"Playlist atualizada com sucesso!")
    else:
        print("Playlist não encontrada.")


def atualizar_album():
    ler_albuns()  # Mostra os álbuns cadastrados
    try:
        album_id = int(input("Digite o ID do álbum que deseja atualizar: "))
        album = sessao.query(Album).filter_by(id=album_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if album:
        novo_nome = input("Digite o novo nome do álbum (deixe em branco para não alterar): ")
        if novo_nome:
            album.nome = novo_nome
        
        while True:
            data_lancamento_input = input("Digite a nova data de lançamento do álbum (DD-MM-AAAA) ou deixe em branco para não alterar: ")
            if data_lancamento_input:
                try:
                    album.data_lancamento = datetime.strptime(data_lancamento_input, "%d-%m-%Y").date()
                    break
                except ValueError:
                    print("Formato inválido. Por favor, insira a data no formato DD-MM-AAAA.")
            else:
                break

        sessao.commit()
        print(f"Álbum atualizado com sucesso!")
    else:
        print("Álbum não encontrado.")


def atualizar_artista():
    ler_artistas()  # Mostra os artistas cadastrados
    try:
        artista_id = int(input("Digite o ID do artista que deseja atualizar: "))
        artista = sessao.query(Artista).filter_by(id=artista_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if artista:
        novo_nome = input("Digite o novo nome do artista (deixe em branco para não alterar): ")
        if novo_nome:
            artista.nome = novo_nome
        
        novo_pais = input("Digite o novo país de origem do artista (deixe em branco para não alterar): ")
        if novo_pais:
            artista.pais_origem = novo_pais

        sessao.commit()
        print(f"Artista atualizado com sucesso!")
    else:
        print("Artista não encontrado.")


def atualizar_cliente_detalhes():
    ler_clientes()  # Mostra os clientes cadastrados
    try:
        cliente_id = int(input("Digite o ID do cliente que deseja atualizar: "))
        cliente = sessao.query(Cliente).filter_by(id=cliente_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if cliente:
        print("O que você deseja atualizar?")
        print("1. Nome")
        print("2. Email")
        print("3. Data de Nascimento")
        print("4. Voltar")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            novo_nome = input("Digite o novo nome do cliente: ")
            cliente.nome = novo_nome
            
        elif opcao == '2':
            novo_email = input("Digite o novo email do cliente: ")
            cliente.email = novo_email
            
        elif opcao == '3':
            while True:
                data_nasc_input = input("Digite a nova data de nascimento do cliente (DD-MM-AAAA): ")
                try:
                    data_nasc = datetime.strptime(data_nasc_input, "%d-%m-%Y").date()
                    cliente.data_nasc = data_nasc
                    break
                except ValueError:
                    print("Formato inválido. Por favor, insira a data no formato DD-MM-AAAA.")
        
        sessao.commit()
        print(f"Detalhes do cliente '{cliente.nome}' atualizados com sucesso!")
    else:
        print("Cliente não encontrado.")


def atualizar_genero():
    ler_generos()  # Mostra os gêneros cadastrados
    try:
        genero_id = int(input("Digite o ID do gênero que deseja atualizar: "))
        genero = sessao.query(Genero).filter_by(id=genero_id).first()
    except ValueError:
        print("ID inválido. Por favor, insira um número inteiro.")
        return
    
    if genero:
        novo_nome = input("Digite o novo nome do gênero (deixe em branco para não alterar): ")
        if novo_nome:
            genero.nome = novo_nome

        sessao.commit()
        print(f"Gênero atualizado com sucesso!")
    else:
        print("Gênero não encontrado.")

# CRUD(DELETE)
def apagar_cliente():
    while True:
        ler_clientes()  # Mostra os clientes cadastrados
        try:
            cliente_id = int(input("Digite o ID do cliente que deseja apagar (ou deixe vazio para cancelar): ").strip())
            cliente = sessao.query(Cliente).filter_by(id=cliente_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if cliente:
            sessao.delete(cliente)
            sessao.commit()
            print(f"Cliente '{cliente.nome}' apagado com sucesso!")
            break
        else:
            print("Cliente não encontrado. Tente novamente.")


def apagar_playlist():
    while True:
        ler_playlists()  # Mostra as playlists cadastradas
        try:
            playlist_id = int(input("Digite o ID da playlist que deseja apagar (ou deixe vazio para cancelar): ").strip())
            playlist = sessao.query(Playlist).filter_by(id=playlist_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if playlist:
            sessao.delete(playlist)
            sessao.commit()
            print(f"Playlist '{playlist.nome}' apagada com sucesso!")
            break
        else:
            print("Playlist não encontrada. Tente novamente.")


def apagar_musica():
    while True:
        ler_musicas()  # Mostra as músicas cadastradas
        try:
            musica_id = int(input("Digite o ID da música que deseja apagar (ou deixe vazio para cancelar): ").strip())
            musica = sessao.query(Musica).filter_by(id=musica_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if musica:
            sessao.delete(musica)
            sessao.commit()
            print(f"Música '{musica.nome}' apagada com sucesso!")
            break
        else:
            print("Música não encontrada. Tente novamente.")


def apagar_album():
    while True:
        ler_albuns()  # Mostra os álbuns cadastrados
        try:
            album_id = int(input("Digite o ID do álbum que deseja apagar (ou deixe vazio para cancelar): ").strip())
            album = sessao.query(Album).filter_by(id=album_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if album:
            sessao.delete(album)
            sessao.commit()
            print(f"Álbum '{album.nome}' apagado com sucesso!")
            break
        else:
            print("Álbum não encontrado. Tente novamente.")



def apagar_artista():
    while True:
        ler_artistas()  # Mostra os artistas cadastrados
        try:
            artista_id = int(input("Digite o ID do artista que deseja apagar (ou deixe vazio para cancelar): ").strip())
            artista = sessao.query(Artista).filter_by(id=artista_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if artista:
            sessao.delete(artista)
            sessao.commit()
            print(f"Artista '{artista.nome}' apagado com sucesso!")
            break
        else:
            print("Artista não encontrado. Tente novamente.")


def apagar_genero():
    while True:
        ler_generos()  # Mostra os gêneros cadastrados
        try:
            genero_id = int(input("Digite o ID do gênero que deseja apagar (ou deixe vazio para cancelar): ").strip())
            genero = sessao.query(Genero).filter_by(id=genero_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if genero:
            sessao.delete(genero)
            sessao.commit()
            print(f"Gênero '{genero.nome}' apagado com sucesso!")
            break
        else:
            print("Gênero não encontrado. Tente novamente.")


def apagar_single():
    while True:
        ler_singles()  # Mostra os singles cadastrados
        try:
            single_id = int(input("Digite o ID da single que deseja apagar (ou deixe vazio para cancelar): ").strip())
            single = sessao.query(Single).filter_by(id=single_id).first()
        except ValueError:
            print("Operação cancelada.")
            break
        
        if single:
            sessao.delete(single)
            sessao.commit()
            print(f"Single '{single.nome}' apagada com sucesso!")
            break
        else:
            print("Single não encontrada. Tente novamente.")


def deletar_banco_de_dados():
    while True:
        print(f"Você tem certeza que deseja deletar o banco de dados '{nome_do_banco}'?")
        print("1. Sim")
        print("2. Não")
        
        confirmar = input("Escolha uma opção (1 ou 2): ")
        
        if confirmar == '1':
            sessao.close()
            # Criar uma nova sessão para executar o comando
            with sessao.begin():  # Use uma nova sessão
                sessao.execute(text(f"DROP DATABASE {nome_do_banco}"))
            print(f"Banco de dados '{nome_do_banco}' deletado com sucesso!")
            break
        elif confirmar == '2':
            print("Operação cancelada.")
            break
        else:
            print("Opção inválida. Por favor, escolha '1' para sim ou '2' para não.")

def menu_criacao():
    while True:
        print("\nMenu de Criação: ", end="")
        print("1. Criar Cliente | 2. Criar Playlist | 3. Criar Música | 4. Adicionar Música a Playlist | 5. Voltar")
        
        opcao = input(" Escolha uma opção: ")

        if opcao == '1':
            criar_cliente()
        elif opcao == '2':
            criar_playlist()
        elif opcao == '3':
            adicionar_musica()
        elif opcao == '4':
            adicionar_musica_a_playlist()
        elif opcao == '5':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

def menu_leitura():
    while True:
        print("\nMenu de Leitura: ", end="")
        print("1. Ler Clientes | 2. Ler Playlists | 3. Ler Músicas | 4. Ler Álbuns | 5. Ler Artistas | 6. Ler Singles | 7. Ler Gêneros Musicais | 8. Ler Playlists e suas Músicas | 9. Voltar")
        
        opcao = input(" Escolha uma opção: ")

        if opcao == '1':
            ler_clientes()
        elif opcao == '2':
            ler_playlists()
        elif opcao == '3':
            ler_musicas()
        elif opcao == '4':
            ler_albuns()
        elif opcao == '5':
            ler_artistas()
        elif opcao == '6':
            ler_singles()
        elif opcao == '7':
            ler_generos()
        elif opcao == '8':
            ler_playlists_e_musicas()
        elif opcao == '9':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

def menu_atualizacao():
    while True:
        print("\nMenu de Atualização: ", end="")
        print("1. Atualizar Dados do Álbum | 2. Atualizar Dados do Artista | 3. Atualizar Cliente | 4. Atualizar Gênero Musical | 5. Atualizar Dados da Música | 6. Voltar")
        
        opcao = input(" Escolha uma opção: ")

        if opcao == '1':
            atualizar_album()
        elif opcao == '2':
            atualizar_artista()
        elif opcao == '3':
            atualizar_cliente_detalhes()
        elif opcao == '4':
            atualizar_genero()
        elif opcao == '5':
            atualizar_musica()
        elif opcao == '6':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

def menu_delecao():
    while True:
        print("\nMenu de Deleção: ", end="")
        print("1. Deletar Cliente | 2. Deletar Artista | 3. Deletar Álbum | 4. Deletar Gênero | 5. Deletar Playlist | 6. Deletar Música | 7. Deletar Single | 8. Deletar Banco de Dados | 9. Voltar")
        
        opcao = input(" Escolha uma opção: ")

        if opcao == '1':
            apagar_cliente()
        elif opcao == '2':
            apagar_artista()
        elif opcao == '3':
            apagar_album()
        elif opcao == '4':
            apagar_genero()
        elif opcao == '5':
            apagar_playlist()
        elif opcao == '6':
            apagar_musica()
        elif opcao == '7':
            apagar_single()
        elif opcao == '8':
            deletar_banco_de_dados()
            exit()
        elif opcao == '9':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

def menu_principal():
    while True:
        print("\nMenu Principal: ", end="")
        print("1. Menu de Criação | 2. Menu de Leitura | 3. Menu de Atualização | 4. Menu de Deleção | 5. Sair")
        
        opcao = input(" Escolha uma opção: ")

        if opcao == '1':
            menu_criacao()
        elif opcao == '2':
            menu_leitura()  
        elif opcao == '3':
            menu_atualizacao()
        elif opcao == '4':
            menu_delecao()
        elif opcao == '5':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

# Executando o menu principal
menu_principal()

# Fechando a sessão ao final
sessao.close()
