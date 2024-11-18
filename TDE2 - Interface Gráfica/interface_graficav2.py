import sys
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QWidget, QLabel, QDialog, QGridLayout, QLineEdit, 
    QMessageBox, QTabWidget, QListWidget,
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Dados de conexão com o banco de dados
USUARIO = 'root'
SENHA = ''
HOST = 'localhost'
PORTA = '3306'
BANCO_DE_DADOS = 'seguradora'

# Criar engine do SQLAlchemy
engine = sqlalchemy.create_engine(f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{BANCO_DE_DADOS}')

# Definindo a base para as tabelas
Base = declarative_base()

# Criando uma sessão
Sessao = sessionmaker(bind=engine)
sessao = Sessao()

# Tabela Cliente
class Cliente(Base):
    __tablename__ = 'cliente'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    cpf = Column(String(11), unique=True)
    nome = Column(String(50))
    endereco = Column(String(100))
    telefone = Column(String(15))
    email = Column(String(50))
    apolices = relationship("Apolice", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome={self.nome}, cpf={self.cpf}, telefone={self.telefone}, email={self.email})>"

# Tabela Apólice
class Apolice(Base):
    __tablename__ = 'apolice'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    fk_cliente = Column(Integer, ForeignKey('cliente.id'))
    data_contrato = Column(Date)
    contato = Column(String(50))
    assinatura = Column(String(50))
    cliente = relationship("Cliente", back_populates="apolices")
    apartamento = relationship("Apartamento", back_populates="apolice", uselist=False)

    def __repr__(self):
        return f"<Apolice(id={self.id}, data_contrato={self.data_contrato}, cliente_id={self.fk_cliente})>"

# Tabela Apartamento
class Apartamento(Base):
    __tablename__ = 'apartamento'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    endereco = Column(String(100))
    andar = Column(Integer)
    tipo_ap = Column(String(50))
    numero_ap = Column(Integer)
    apolice_id = Column(Integer, ForeignKey('apolice.id'))
    apolice = relationship("Apolice", back_populates="apartamento")
    acidentes = relationship("Acidente", back_populates="apartamento")

    def __repr__(self):
        return f"<Apartamento(id={self.id}, endereco={self.endereco}, numero_ap={self.numero_ap}, apolice_id={self.apolice_id})>"

# Tabela Acidente
class Acidente(Base):
    __tablename__ = 'acidente'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    descricao = Column(String(200))
    data_ocorrencia = Column(Date)
    valor_acidente = Column(Float)
    tipo_acidente = Column(String(50))
    fk_apartamento = Column(Integer, ForeignKey('apartamento.id'))
    apartamento = relationship("Apartamento", back_populates="acidentes")

    def __repr__(self):
        return f"<Acidente(id={self.id}, descricao={self.descricao}, data_ocorrencia={self.data_ocorrencia}, apartamento_id={self.fk_apartamento})>"
    
class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False) # Store the hash, not the plain text password
    role = Column(String(20), nullable=False) #e.g., 'root', 'client', 'admin'

    def __repr__(self):
        return f"<Usuario(id={self.id}, username={self.username}, role={self.role})>"

# Criando as tabelas no banco de dados (se já não existirem)
Base.metadata.create_all(engine)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        layout = QGridLayout()
        self.register_dialog = None

        layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input, 0, 1)

        layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input, 1, 1)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button, 2, 0, 1, 2)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_registration)
        layout.addWidget(self.register_button, 3, 0, 1, 2)


        self.setLayout(layout)
        self.registration_dialog = None

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = sessao.query(Usuario).filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            self.role = user.role
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")

    def show_registration(self):
        if self.registration_dialog is None:
            self.registration_dialog = RegistrationDialog(self)
        self.registration_dialog.show()

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New User")
        layout = QGridLayout()

        layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input, 0, 1)

        layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input, 1, 1)

        layout.addWidget(QLabel("Confirm Password:"), 2, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input, 2, 1)

        layout.addWidget(QLabel("Role (root, client, admin):"), 3, 0)
        self.role_input = QLineEdit()
        layout.addWidget(self.role_input, 3, 1)


        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button, 4, 0, 1, 2)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_input.text()
        self.close()
        if self.parent():
            self.parent().show()

        if password != confirm_password:
            QMessageBox.warning(self, "Registration Error", "Passwords do not match.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            new_user = Usuario(username=username, password_hash=hashed_password.decode('utf-8'), role=role)
            sessao.add(new_user)
            sessao.commit()
            QMessageBox.information(self, "Registration Successful", "User registered successfully!")
            self.accept()
        except IntegrityError:
            sessao.rollback()
            QMessageBox.warning(self, "Registration Error", "Username already exists. Please choose a different username.")
        except Exception as e:
            sessao.rollback()
            QMessageBox.warning(self, "Registration Error", f"An error occurred: {e}")

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SGBD - Seguradora')
        self.setGeometry(720, 250, 500, 500)

        # Estilo da janela
        self.setStyleSheet(""" 
            QMainWindow { 
                background-color: #E6E6E6; 
            } 
            QPushButton { 
                background-color: #0056b3; 
                color: white; 
                font-size: 16px; 
                border-radius: 5px; 
                padding: 10px; 
            } 
            QPushButton:hover { 
                background-color: #0074e1; 
            } 
            QDialog { 
                background-color: #fdfeff; 
            } 
            QLabel { 
                font-size: 14px;
                color:#333333
            } 
            QLineEdit { 
                padding: 5px; 
                border: 1px solid #ccc; 
                border-radius: 3px; 
            } 
        """)

        # Estilo personalizado para as abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #0ff;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                font-weight: alternate;
            }
            QTabWidget::pane {
                border: 1px solid #000000;
                padding: 10px
            }
            QTabBar::tab:hover {
              background-color: #f0f0f0;    
            }
        """)

        # Criar um QLabel para o título da seguradora
        title_label = QLabel('Seguradora')
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        title_label.setAlignment(Qt.AlignCenter)

        # Criar um layout vertical e adicionar o QLabel ao layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(title_label)  # Adiciona o título ao layout
        layout.addWidget(self.tabs)  # Adiciona as abas ao layout
        self.setCentralWidget(central_widget)

        # Adicionar as abas na ordem desejada: Cliente, Apólice, Apartamento, Acidente
        self.add_tab('Cliente', 'Cliente')
        self.add_tab('Apólice', 'Apólice')
        self.add_tab('Apartamento', 'Apartamento')
        self.add_tab('Acidente', 'Acidente')

    def add_tab(self, title, tipo):
        tab = QWidget()
        layout = QVBoxLayout()

        # Adicionando botões diretamente na aba
        add_btn = QPushButton(f'Adicionar {tipo}')
        read_btn = QPushButton(f'Ler {tipo}')
        update_btn = QPushButton(f'Atualizar {tipo}')
        delete_btn = QPushButton(f'Deletar {tipo}')

        layout.addWidget(add_btn)
        layout.addWidget(read_btn)
        layout.addWidget(update_btn)
        layout.addWidget(delete_btn)

        # Funções para cada botão
        add_btn.clicked.connect(lambda: self.form_dialog(tipo, 'Adicionar'))
        read_btn.clicked.connect(lambda: self.form_dialog(tipo, 'Ler'))
        update_btn.clicked.connect(lambda: self.form_dialog(tipo, 'Atualizar'))
        delete_btn.clicked.connect(lambda: self.form_dialog(tipo, 'Deletar'))

        tab.setLayout(layout)
        self.tabs.addTab(tab, title)

    def form_dialog(self, tipo, operacao):
        dialog = QDialog(self)
        dialog.setWindowTitle(f'{operacao} {tipo}')
        dialog.resize(600, 600)
        layout = QGridLayout()
        campos = [] # Declare campos here

        if self.role == "client" and operacao in ['Adicionar', 'Atualizar', 'Deletar']:
            if tipo not in ['Cliente', 'Apólice']:
                QMessageBox.warning(dialog, 'Acesso Negado', 'Você não tem permissão para realizar esta operação.')
                return

        if operacao == 'Ler':
            layout.addWidget(QLabel(f'Lista de {tipo}s:'), 0, 0)
            list_widget = QListWidget()
            layout.addWidget(list_widget, 1, 0, 1, 2)

            registros = self.get_registros(tipo)
            if tipo == 'Cliente':
                for registro in registros:
                    client_str = f"ID: {registro.id}, Nome: {registro.nome}, CPF: {registro.cpf}, Telefone: {registro.telefone}, Email: {registro.email}"
                    list_widget.addItem(client_str)
            elif tipo == 'Apólice':
                for registro in registros:
                    cliente_id = registro.cliente.id
                    apolice_str = f"ID Apólice: {registro.id}, ID Cliente: {cliente_id}, Data Contrato: {registro.data_contrato}, Contato: {registro.contato}, Assinatura: {registro.assinatura}"
                    list_widget.addItem(apolice_str)
            elif tipo == 'Apartamento':
                for registro in registros:
                    acidente_ids = [str(acidente.id) for acidente in registro.acidentes]
                    apartamento_str = f"ID Apartamento: {registro.id}, Endereço: {registro.endereco}, Número: {registro.numero_ap}, Andar: {registro.andar}, Tipo: {registro.tipo_ap}, IDs Acidentes: {', '.join(acidente_ids) if acidente_ids else 'Nenhum'}"
                    list_widget.addItem(apartamento_str)
            elif tipo == 'Acidente':
                for registro in registros:
                    acidente_str = f"ID Acidente: {registro.id}, Descrição: {registro.descricao}, Data Ocorrência: {registro.data_ocorrencia}, Valor: {registro.valor_acidente}, Tipo: {registro.tipo_acidente}"
                    list_widget.addItem(acidente_str)

            submit_btn = QPushButton(f'Fechar')
            submit_btn.clicked.connect(dialog.accept)
            layout.addWidget(submit_btn, 2, 0, 1, 2)


        elif operacao == 'Adicionar':
            campos, inputs = self.criar_campos(tipo, layout)

            if tipo == 'Apartamento':
                layout.addWidget(QLabel('Apólices já cadastradas:'), len(campos), 0, 1, 2)
                apolice_list = QListWidget()
                apolices = self.get_registros('Apólice')
                for apolice in apolices:
                    apolice_str = f"ID Apólice: {apolice.id}, Data Contrato: {apolice.data_contrato}, Contato: {apolice.contato}, Assinatura: {apolice.assinatura}"
                    apolice_list.addItem(apolice_str)
                layout.addWidget(apolice_list, len(campos) + 1, 0, 1, 2)

            elif tipo == 'Apólice':
                layout.addWidget(QLabel('Clientes já cadastrados:'), len(campos), 0, 1, 2)
                cliente_list = QListWidget()
                clientes = self.get_registros('Cliente')
                for cliente in clientes:
                    cliente_str = f"ID: {cliente.id}, Nome: {cliente.nome}, CPF: {cliente.cpf}, Endereço: {cliente.endereco}, Telefone: {cliente.telefone}, Email: {cliente.email}"
                    cliente_list.addItem(cliente_str)
                layout.addWidget(cliente_list, len(campos) + 1, 0, 1, 2)

            elif tipo == 'Acidente':
                layout.addWidget(QLabel('Apartamentos já cadastrados:'), len(campos), 0, 1, 2)
                apartamento_list = QListWidget()
                apartamentos = self.get_registros('Apartamento')
                for apartamento in apartamentos:
                    apartamento_str = f"ID Apartamento: {apartamento.id}, Endereço: {apartamento.endereco}, Número: {apartamento.numero_ap}, Andar: {apartamento.andar}, Tipo: {apartamento.tipo_ap}"
                    apartamento_list.addItem(apartamento_str)
                layout.addWidget(apartamento_list, len(campos) + 1, 0, 1, 2)

            submit_btn = QPushButton(f'Adicionar {tipo}')
            submit_btn.clicked.connect(lambda: self.adicionar_registro(
                tipo, inputs, dialog,
                apolice_list if tipo == 'Apartamento' else None,
                cliente_list if tipo == 'Apólice' else None,
                apartamento_list if tipo == 'Acidente' else None
            ))
            layout.addWidget(submit_btn, len(campos) + 2, 0, 1, 2)

        elif operacao == 'Atualizar' or operacao == 'Deletar':
            layout.addWidget(QLabel(f'Selecione o ID do {tipo} para {operacao.lower()}:'))
            id_list = QListWidget()
            layout.addWidget(id_list, 1, 0, 1, 2)
            registros = self.get_registros(tipo)
            campos = [] # Define campos here
            for registro in registros:
                id_list.addItem(f"ID {registro.id} - {str(registro)}")

            if operacao == 'Atualizar':
                campos, inputs = self.criar_campos(tipo, layout, start_row=2)
                submit_btn = QPushButton(f'Atualizar {tipo}')
                submit_btn.clicked.connect(lambda: self.atualizar_registro(tipo, inputs, id_list, dialog))
            else:  # Deletar
                submit_btn = QPushButton(f'Deletar {tipo}')
                submit_btn.clicked.connect(lambda: self.deletar_registro(tipo, id_list, dialog))

            layout.addWidget(submit_btn, 4 if operacao == 'Deletar' else len(campos) + 3, 0, 1, 2)

        dialog.setLayout(layout)
        dialog.exec_()

    def criar_campos(self, tipo, layout, start_row=0):
        campos = []
        inputs = []

        if tipo == 'Cliente':
            campos = ['CPF', 'Nome', 'Endereço', 'Telefone', 'Email']
        elif tipo == 'Apólice':
            campos = ['Data do Contrato (DD-MM-YYYY)', 'Contato', 'Assinatura']
        elif tipo == 'Apartamento':
            campos = ['Endereço', 'Andar', 'Tipo de Apartamento (Padrão,Kitnet,Cobertura,Duplex,Triplex,Flat)', 'Número do Apartamento']
        elif tipo == 'Acidente':
            campos = ['Descrição', 'Data da Ocorrência (DD-MM-YYYY)', 'Valor do Acidente', 'Tipo de Acidente']

        for i, campo in enumerate(campos):
            layout.addWidget(QLabel(campo), start_row + i, 0)
            input_field = QLineEdit()
            layout.addWidget(input_field, start_row + i, 1)
            inputs.append(input_field)

        return campos, inputs

    def adicionar_registro(self, tipo, inputs, dialog, apolice_list=None, cliente_list=None, apartamento_list=None):
            if self.role == "client" and tipo != 'Cliente':
                QMessageBox.warning(dialog, 'Acesso Negado', 'Você não tem permissão para adicionar este tipo de registro.')
                return

            try:
                if tipo == 'Cliente':
                    cpf_input = inputs[0].text()
                    # Check for duplicate CPF before adding to the database
                    existing_client = sessao.query(Cliente).filter(Cliente.cpf == cpf_input).first()
                    if existing_client:
                        QMessageBox.warning(dialog, 'Erro', 'CPF já cadastrado. Insira um CPF diferente.')
                        return

                    cliente = Cliente(
                        cpf=cpf_input,
                        nome=inputs[1].text(),
                        endereco=inputs[2].text(),
                        telefone=inputs[3].text(),
                        email=inputs[4].text()
                    )
                    sessao.add(cliente)
                    sessao.commit()
                    QMessageBox.information(dialog, 'Sucesso', f'{tipo} adicionado com sucesso!')
                    dialog.accept()
                elif tipo == 'Apólice':
                    data_contrato = datetime.strptime(inputs[0].text(), '%d-%m-%Y').date()
                    selected_cliente = cliente_list.currentItem()
                    if selected_cliente:
                        try:
                            # Get the full text of the QListWidgetItem
                            cliente_text = selected_cliente.text()
                            
                            # Use a more robust method to extract the ID
                            # Assuming the format is "ID: X, Nome: Name, CPF: ..."
                            id_part = [part for part in cliente_text.split(',') if 'ID:' in part][0]
                            fk_cliente = int(id_part.split('ID:')[1].strip())
                            apolice = Apolice(
                                data_contrato=data_contrato,
                                contato=inputs[1].text(),
                                assinatura=inputs[2].text(),
                                fk_cliente=fk_cliente
                            )
                            sessao.add(apolice)
                            sessao.commit()
                            QMessageBox.information(dialog, 'Sucesso', 'Apólice adicionada com sucesso!')
                            dialog.accept()
                        except (ValueError, IndexError) as e:
                            QMessageBox.warning(dialog, 'Erro', f'Erro ao adicionar Apólice: {e}. Certifique-se de ter selecionado um cliente válido.')
                            sessao.rollback()
                    else:
                        QMessageBox.warning(dialog, 'Erro', 'Selecione um cliente.')
                elif tipo == 'Apartamento':
                    selected_apolice = apolice_list.currentItem()
                    if selected_apolice:
                        try:
                            # Extrair o texto do item selecionado
                            apolice_text = selected_apolice.text()

                            # Verificar se o texto contém "ID Apólice:"
                            if 'ID Apólice:' not in apolice_text:
                                raise ValueError("Formato inválido: ID não encontrado.")
                            
                            # Extrair o ID da parte correspondente
                            id_parts = [part for part in apolice_text.split(',') if 'ID Apólice:' in part]
                            if not id_parts:
                                raise ValueError("Formato inválido: ID não encontrado.")
                            
                            apolice_id = int(id_parts[0].split('ID Apólice:')[1].strip())

                            apartamento = Apartamento(
                                endereco=inputs[0].text(),
                                andar=int(inputs[1].text()),
                                tipo_ap=inputs[2].text(),
                                numero_ap=int(inputs[3].text()),
                                apolice_id=apolice_id
                            )
                            sessao.add(apartamento)
                            sessao.commit()
                            QMessageBox.information(dialog, 'Sucesso', 'Apartamento adicionado com sucesso!')
                            dialog.accept()
                        except (ValueError, IndexError) as e:
                            QMessageBox.warning(dialog, 'Erro', f'Erro ao adicionar Apartamento: {e}. Certifique-se de ter selecionado uma apólice válida e que o formato do texto esteja correto.')
                            sessao.rollback()
                    else:
                        QMessageBox.warning(dialog, 'Erro', 'Selecione uma apólice.')

                elif tipo == 'Acidente':
                    selected_apartamento = apartamento_list.currentItem()
                    if selected_apartamento:
                        try:
                            # Extrair o texto do item selecionado
                            apartamento_text = selected_apartamento.text()

                            # Verificar se o texto contém "ID Apartamento:"
                            if 'ID Apartamento:' not in apartamento_text:
                                raise ValueError("Formato inválido: ID Apartamento não encontrado.")
                            
                            # Extrair o ID da parte correspondente
                            id_parts = [part for part in apartamento_text.split(',') if 'ID Apartamento:' in part]
                            if not id_parts:
                                raise ValueError("Formato inválido: ID Apartamento não encontrado.")
                            
                            apartamento_id = int(id_parts[0].split('ID Apartamento:')[1].strip())

                            # Extrair a data de ocorrência
                            data_ocorrencia = datetime.strptime(inputs[1].text(), '%d-%m-%Y').date()
                            
                            acidente = Acidente(
                                descricao=inputs[0].text(),
                                data_ocorrencia=data_ocorrencia,
                                valor_acidente=float(inputs[2].text()),
                                tipo_acidente=inputs[3].text(),
                                fk_apartamento=apartamento_id  # Usar o ID do apartamento extraído
                            )
                            sessao.add(acidente)
                            sessao.commit()
                            QMessageBox.information(dialog, 'Sucesso', 'Acidente adicionado com sucesso!')
                            dialog.accept()
                        except (ValueError, IndexError) as e:
                            QMessageBox.warning(dialog, 'Erro', f'Erro ao adicionar Acidente: {e}. Certifique-se de ter selecionado um apartamento válido e inserido uma data e valor válidos.')
                            sessao.rollback()
                    else:
                        QMessageBox.warning(dialog, 'Erro', 'Selecione um apartamento.')



            except IntegrityError as ie:
                sessao.rollback()
                QMessageBox.warning(dialog, 'Erro de Integridade', f'Erro ao adicionar {tipo}: {ie}')
            except ValueError as ve:
                sessao.rollback()
                QMessageBox.warning(dialog, 'Erro de Valor', f'Erro ao adicionar {tipo}: Valor inválido. {ve}')
            except Exception as e:
                sessao.rollback()
                QMessageBox.warning(dialog, 'Erro', f'Erro ao adicionar {tipo}: {e}')

    def atualizar_registro(self, tipo, inputs, id_list, dialog):
        if self.role == "client" and tipo != 'Cliente':
          QMessageBox.warning(dialog, 'Acesso Negado', 'Você não tem permissão para atualizar este tipo de registro.')
          return
        try:
            selected_id = int(id_list.currentItem().text().split()[1])  # ID do item selecionado
            if tipo == 'Cliente':
                cliente = sessao.query(Cliente).filter(Cliente.id == selected_id).first()
                if cliente:
                    cliente.cpf = inputs[0].text()
                    cliente.nome = inputs[1].text()
                    cliente.endereco = inputs[2].text()
                    cliente.telefone = inputs[3].text()
                    cliente.email = inputs[4].text()
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Cliente não encontrado.')
                    return
            elif tipo == 'Apólice':
                apolice = sessao.query(Apolice).filter(Apolice.id == selected_id).first()
                if apolice:
                    apolice.data_contrato = datetime.strptime(inputs[0].text(), '%d-%m-%Y').date()
                    apolice.contato = inputs[1].text()
                    apolice.assinatura = inputs[2].text()
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Apólice não encontrada.')
                    return
            elif tipo == 'Apartamento':
                apartamento = sessao.query(Apartamento).filter(Apartamento.id == selected_id).first()
                if apartamento:
                    apartamento.endereco = inputs[0].text()
                    apartamento.andar = int(inputs[1].text())
                    apartamento.tipo_ap = inputs[2].text()
                    apartamento.numero_ap = int(inputs[3].text())
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Apartamento não encontrado.')
                    return
            elif tipo == 'Acidente':
                acidente = sessao.query(Acidente).filter(Acidente.id == selected_id).first()
                if acidente:
                    acidente.descricao = inputs[0].text()
                    acidente.data_ocorrencia = datetime.strptime(inputs[1].text(), '%d-%m-%Y').date()
                    acidente.valor_acidente = float(inputs[2].text())
                    acidente.tipo_acidente = inputs[3].text()
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Acidente não encontrado.')
                    return

            sessao.commit()
            QMessageBox.information(dialog, 'Sucesso', f'{tipo} atualizado com sucesso!')
            dialog.accept()
        except IntegrityError as ie:
            sessao.rollback()
            QMessageBox.warning(dialog, 'Erro de Integridade', f'Erro ao atualizar {tipo}: Violação de integridade.')
            print(f"Erro de integridade ao atualizar {tipo}: {ie}")
        except Exception as e:
            sessao.rollback()
            QMessageBox.warning(dialog, 'Erro', f'Erro ao atualizar {tipo}: {e}')
            print(f"Erro geral ao atualizar {tipo}: {e}")

    def deletar_registro(self, tipo, id_list, dialog):
        if self.role == "client":
            QMessageBox.warning(dialog, 'Acesso Negado', 'Você não tem permissão para deletar registros.')
            return
        try:
            selected_id = int(id_list.currentItem().text().split()[1])  # ID do item selecionado
            if tipo == 'Cliente':
                cliente = sessao.query(Cliente).filter(Cliente.id == selected_id).first()
                if cliente:
                    sessao.delete(cliente)
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Cliente não encontrado.')
                    return
            elif tipo == 'Apólice':
                apolice = sessao.query(Apolice).filter(Apolice.id == selected_id).first()
                if apolice:
                    sessao.delete(apolice)
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Apólice não encontrada.')
                    return
            elif tipo == 'Apartamento':
                apartamento = sessao.query(Apartamento).filter(Apartamento.id == selected_id).first()
                if apartamento:
                    sessao.delete(apartamento)
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Apartamento não encontrado.')
                    return
            elif tipo == 'Acidente':
                acidente = sessao.query(Acidente).filter(Acidente.id == selected_id).first()
                if acidente:
                    sessao.delete(acidente)
                else:
                    QMessageBox.warning(dialog, 'Erro', 'Acidente não encontrado.')
                    return

            sessao.commit()
            QMessageBox.information(dialog, 'Sucesso', f'{tipo} deletado com sucesso!')
            dialog.accept()
        except IntegrityError as ie:
            sessao.rollback()
            QMessageBox.warning(dialog, 'Erro de Integridade', f'Erro ao deletar {tipo}: Violação de integridade referencial.')
            print(f"Erro de integridade ao deletar {tipo}: {ie}")
        except Exception as e:
            sessao.rollback()
            QMessageBox.warning(dialog, 'Erro', f'Erro ao deletar {tipo}: {e}')
            print(f"Erro geral ao deletar {tipo}: {e}")

    def get_registros(self, tipo):
        if self.role == "client" and tipo == 'Cliente':
            cpf = self.get_client_cpf()  #Implement get_client_cpf method.
            return sessao.query(Cliente).filter(Cliente.cpf == cpf).all()
        elif self.role == "client" and tipo in ['Apólice', 'Apartamento', 'Acidente']:
            cpf = self.get_client_cpf()
            # Join tables to retrieve related data for the client based on their CPF.
            return self.get_client_data(cpf, tipo)
        try:
            if tipo == 'Cliente':
                return sessao.query(Cliente).all()
            elif tipo == 'Apólice':
                return sessao.query(Apolice).all()
            elif tipo == 'Apartamento':
                return sessao.query(Apartamento).all()
            elif tipo == 'Acidente':
                return sessao.query(Acidente).all()
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao obter registros de {tipo}: {e}')
            print(f"Erro ao obter registros de {tipo}: {e}")
            return []
        else:
            #Root user gets all data
            return super().get_registros(tipo)
        
    def get_client_cpf(self):
        return "123456789"
    
    def get_client_data(self,cpf,tipo):
        if tipo == 'Apólice':
            return sessao.query(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
        elif tipo == 'Apartamento':
            return sessao.query(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
        elif tipo == 'Acidente':
            return sessao.query(Acidente).join(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
        else:
            return []
        
    def logout(self):
        self.close()
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            main_window = MainMenu(login_dialog.username) # Pass the username back to MainMenu
            main_window.show()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = MainMenu()
        main_window.role = login_dialog.role if hasattr(login_dialog, 'role') else "root"
        main_window.show()
    sys.exit(app.exec_())