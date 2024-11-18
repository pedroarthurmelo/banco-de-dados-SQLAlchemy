import sys
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QWidget, QLabel, QDialog, QGridLayout, QLineEdit, 
    QMessageBox, QTabWidget, QListWidget, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QValidator, QIntValidator, QRegExpValidator
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def parse_data(data_str):
    """Tenta converter uma string para uma data, aceitando múltiplos formatos."""
    formatos = ['%d/%m/%Y', '%d-%m-%Y', '%d%m%Y']  # Formatos aceitos
    for formato in formatos:
        try:
            return datetime.strptime(data_str, formato).date()
        except ValueError:
            continue
    raise ValueError(f"Formato de data inválido: '{data_str}'. Use dd/mm/aaaa, dd-mm-aaaa ou ddmmaaaa.")

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
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)
    endereco = Column(String(100))
    telefone = Column(String(15))
    email = Column(String(50))
    password_hash = Column(String(128), nullable=False)
    apolices = relationship("Apolice", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome={self.nome}, cpf={self.cpf})>"

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
    

class Funcionario(Base):
    __tablename__ = 'funcionario'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)
    cargo = Column(String(50), nullable=False)
    departamento = Column(String(50), nullable=False)
    data_contratacao = Column(Date, nullable=False)
    salario = Column(Float, nullable=False)
    password_hash = Column(String(128), nullable=False)

    def __repr__(self):
        return f"<Funcionario(id={self.id}, nome={self.nome}, cpf={self.cpf})>"
    
Base.metadata.create_all(engine)

class CPFValidator(QRegExpValidator):
    def __init__(self):
        super().__init__()
        # Only allow 11 digits
        regex = QRegExp('^[0-9]{0,11}$')
        self.setRegExp(regex)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.cpf = None
        self.role = None
        self.setWindowTitle("Login")
        layout = QGridLayout()
        self.register_dialog = None

        layout.addWidget(QLabel("CPF:"), 0, 0)
        self.cpf_input = QLineEdit()
        layout.addWidget(self.cpf_input, 0, 1)

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
        cpf = self.cpf_input.text()
        password = self.password_input.text()

        # Try login as cliente
        cliente = sessao.query(Cliente).filter_by(cpf=cpf).first()
        if cliente and bcrypt.checkpw(password.encode('utf-8'), cliente.password_hash.encode('utf-8')):
            self.cpf = cpf
            self.role = "CLIENTE"
            self.accept()
            return

        # Try login as funcionario
        funcionario = sessao.query(Funcionario).filter_by(cpf=cpf).first()
        if funcionario and bcrypt.checkpw(password.encode('utf-8'), funcionario.password_hash.encode('utf-8')):
            self.cpf = cpf
            self.role = "FUNCIONÁRIO"
            self.accept()
            return

        QMessageBox.warning(self, "Login Failed", "CPF ou senha incorretos.")

    def show_registration(self):
        if self.registration_dialog is None:
            self.registration_dialog = RegistrationDialog(self)
        self.registration_dialog.show()

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registro de Novo Usuário")
        self.layout = QGridLayout()
        
        # Role selection
        self.layout.addWidget(QLabel("Tipo de Registro:"), 0, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["CLIENTE", "FUNCIONÁRIO"])
        self.role_combo.currentTextChanged.connect(self.toggle_fields)
        self.layout.addWidget(self.role_combo, 0, 1)

        # Common fields
        self.layout.addWidget(QLabel("CPF (apenas números):"), 1, 0)
        self.cpf_input = QLineEdit()
        self.cpf_input.setValidator(CPFValidator())
        self.layout.addWidget(self.cpf_input, 1, 1)

        self.layout.addWidget(QLabel("Nome:"), 2, 0)
        self.nome_input = QLineEdit()
        self.layout.addWidget(self.nome_input, 2, 1)

        self.layout.addWidget(QLabel("Senha:"), 3, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input, 3, 1)

        self.layout.addWidget(QLabel("Confirmar Senha:"), 4, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.confirm_password_input, 4, 1)

        # Cliente specific fields
        self.cliente_widgets = []
        self.cliente_widgets.append((QLabel("Endereço:"), QLineEdit()))
        self.cliente_widgets.append((QLabel("Telefone:"), QLineEdit()))
        self.cliente_widgets.append((QLabel("Email:"), QLineEdit()))

        # Funcionario specific fields
        self.funcionario_widgets = []
        self.funcionario_widgets.append((QLabel("Cargo:"), QLineEdit()))
        self.funcionario_widgets.append((QLabel("Departamento:"), QLineEdit()))
        self.funcionario_widgets.append((QLabel("Data Contratação (DD-MM-YYYY):"), QLineEdit()))
        self.funcionario_widgets.append((QLabel("Salário:"), QLineEdit()))

        # Add all widgets but hide funcionario ones initially
        row = 5
        for label, input_field in self.cliente_widgets + self.funcionario_widgets:
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(input_field, row, 1)
            if (label, input_field) in self.funcionario_widgets:
                label.hide()
                input_field.hide()
            row += 1

        self.show_password_checkbox = QCheckBox("Mostrar Senha")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        self.layout.addWidget(self.show_password_checkbox, row, 0, 1, 2)

        self.register_button = QPushButton("Registrar")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button, row + 1, 0, 1, 2)

        self.setLayout(self.layout)

    def toggle_fields(self, role):
        # Show/hide appropriate fields based on role
        for label, input_field in self.cliente_widgets:
            label.setVisible(role == "CLIENTE")
            input_field.setVisible(role == "CLIENTE")
            input_field.clear()

        for label, input_field in self.funcionario_widgets:
            label.setVisible(role == "FUNCIONÁRIO")
            input_field.setVisible(role == "FUNCIONÁRIO")
            input_field.clear()

    def toggle_password_visibility(self, state):
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        self.confirm_password_input.setEchoMode(mode)

    def register(self):
        # Validate common fields
        cpf = self.cpf_input.text()
        nome = self.nome_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_combo.currentText()

        if len(cpf) != 11 or not cpf.isdigit():
            QMessageBox.warning(self, "Erro", "CPF deve conter exatamente 11 dígitos.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            if role == "CLIENTE":
                cliente = Cliente(
                    cpf=cpf,
                    nome=nome,
                    endereco=self.cliente_widgets[0][1].text(),
                    telefone=self.cliente_widgets[1][1].text(),
                    email=self.cliente_widgets[2][1].text(),
                    password_hash=hashed_password.decode('utf-8')
                )
                sessao.add(cliente)
            else:  # FUNCIONÁRIO
                try:
                    data_contratacao = parse_data(self.funcionario_widgets[2][1].text())
                    salario = float(self.funcionario_widgets[3][1].text())
                except ValueError:
                    QMessageBox.warning(self, "Erro", "Data ou salário inválido.")
                    return

                funcionario = Funcionario(
                    cpf=cpf,
                    nome=nome,
                    cargo=self.funcionario_widgets[0][1].text(),
                    departamento=self.funcionario_widgets[1][1].text(),
                    data_contratacao=data_contratacao,
                    salario=salario,
                    password_hash=hashed_password.decode('utf-8')
                )
                sessao.add(funcionario)

            sessao.commit()
            QMessageBox.information(self, "Sucesso", "Registro realizado com sucesso!")
            self.accept()

        except IntegrityError:
            sessao.rollback()
            QMessageBox.warning(self, "Erro", "CPF já cadastrado.")
        except Exception as e:
            sessao.rollback()
            QMessageBox.warning(self, "Erro", f"Erro ao registrar: {str(e)}")

class MainMenu(QMainWindow):
    def __init__(self, username=None, role=None):
        super().__init__()
        self.setWindowTitle('SGBD - Seguradora')
        self.setGeometry(720, 250, 500, 500)
        self.username = username
        self.role = role
        self.cpf = username

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.initUI()
    
    def initUI(self):
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

        title_label = QLabel('Seguradora')
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        title_label.setAlignment(Qt.AlignCenter)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.user_label = QLabel(f"Usuário Logado: {self.username}")
        self.user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        layout.addWidget(self.user_label)

        layout.addWidget(title_label)  
        layout.addWidget(self.tabs)  
        self.setCentralWidget(central_widget)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        if self.role != "CLIENTE":  # Handles both "FUNCIONÁRIO" and other non-client roles
            tabs_to_add = ['Cliente', 'Apólice', 'Apartamento', 'Acidente']
            for tab_title in tabs_to_add:
                self.add_tab(tab_title, tab_title)

        elif self.role == 'CLIENTE': # Separate handling for client roles
            self.customize_client_view()

    def customize_client_view(self):
    # Remove tabs or disable certain operations for CLIENTE
        if self.tabs.count() > 0:
         for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            for btn in tab.findChildren(QPushButton):
                btn.setEnabled(False)

        self.add_client_specific_tabs()

    def add_client_specific_tabs(self):
    
            personal_tab = QWidget()
            personal_layout = QVBoxLayout()
            
            view_personal_btn = QPushButton('Consultar Dados Pessoais')
            view_personal_btn.clicked.connect(self.view_personal_data)
            personal_layout.addWidget(view_personal_btn)
            
            view_apolices_btn = QPushButton('Consultar Apólices')
            view_apolices_btn.clicked.connect(lambda: self.form_dialog('Apólice', 'Ler'))
            personal_layout.addWidget(view_apolices_btn)
            
            view_apartamentos_btn = QPushButton('Consultar Apartamentos')
            view_apartamentos_btn.clicked.connect(lambda: self.form_dialog('Apartamento', 'Ler'))
            personal_layout.addWidget(view_apartamentos_btn)
            
            view_acidentes_btn = QPushButton('Consultar Acidentes')
            view_acidentes_btn.clicked.connect(lambda: self.form_dialog('Acidente', 'Ler'))
            personal_layout.addWidget(view_acidentes_btn)
            
            personal_tab.setLayout(personal_layout)
            self.tabs.addTab(personal_tab, 'Área do Cliente')

    def view_personal_data(self):
        cliente = sessao.query(Cliente).filter_by(cpf=self.cpf).first()
        if cliente:
            data = f"""
            Dados Pessoais:
            CPF: {cliente.cpf}
            Nome: {cliente.nome}
            Endereço: {cliente.endereco}
            Telefone: {cliente.telefone}
            Email: {cliente.email}
            """
            QMessageBox.information(self, 'Dados Pessoais', data)
        else:
            QMessageBox.warning(self, 'Erro', 'Não foi possível encontrar seus dados pessoais.')

    def get_client_cpf(self):
        return self.cpf if self.role == "CLIENTE" else None
    
    def get_registros(self, tipo):
        if self.role == 'CLIENTE':
            cpf = self.get_client_cpf()
            if tipo == 'Cliente':
                return sessao.query(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Apólice':
                return sessao.query(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Apartamento':
                return sessao.query(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Acidente':
                return sessao.query(Acidente).join(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
        else:
            
            return super().get_registros(tipo)


    def add_tab(self, title, tipo):
        tab = QWidget()
        layout = QVBoxLayout()

        if tipo == 'Cliente' and self.role != "CLIENTE":
            actions = ['Ler', 'Atualizar', 'Deletar']
        else:
            actions = ['Adicionar', 'Ler', 'Atualizar', 'Deletar']

        for action in actions:
            btn = QPushButton(f'{action} {tipo}')
            btn.clicked.connect(lambda checked, a=action, t=tipo: self.form_dialog(t, a))
            layout.addWidget(btn)

        tab.setLayout(layout) # Set the layout with the correctly created buttons
        self.tabs.addTab(tab, title)
        

        tab.setLayout(layout)
        self.tabs.addTab(tab, title)

    def form_dialog(self, tipo, operacao):
        dialog = QDialog(self)
        dialog.setWindowTitle(f'{operacao} {tipo}')
        dialog.resize(600, 600)
        layout = QGridLayout()
        campos = [] 

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
            campos = ['Endereço', 'Andar', 'Tipo de Apartamento (Padrão,Kitnet,Cobertura,Duplex,Triplex,Flat)', 'Número do Apartamento'] # Add ID da Apólice
        elif tipo == 'Acidente':
            campos = ['Descrição', 'Data da Ocorrência (DD-MM-YYYY)', 'Valor do Acidente', 'Tipo de Acidente'] # Add ID do Apartamento

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
                    data_contrato = parse_data(inputs[0].text())
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
                            data_ocorrencia = parse_data(inputs[1].text())
                            
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
                    apolice.data_contrato = parse_data(inputs[0].text())
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
                    acidente.data_ocorrencia = parse_data(inputs[1].text())
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
        if self.role == 'CLIENTE':
            cpf = self.get_client_cpf()
            if tipo == 'Cliente':
                return sessao.query(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Apólice':
                return sessao.query(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Apartamento':
                return sessao.query(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
            elif tipo == 'Acidente':
                return sessao.query(Acidente).join(Apartamento).join(Apolice).join(Cliente).filter(Cliente.cpf == cpf).all()
        else:
            if tipo == 'Cliente':
                return sessao.query(Cliente).all()
            elif tipo == 'Apólice':
                return sessao.query(Apolice).all()
            elif tipo == 'Apartamento':
                return sessao.query(Apartamento).all()
            elif tipo == 'Acidente':
                return sessao.query(Acidente).all()
            else:
                return []

        
    def get_client_cpf(self):
        return self.cpf if self.role == "CLIENTE" else None

    
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
        self.close() # Close the main window
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            main_menu = MainMenu(login_dialog.cpf, login_dialog.role)
            main_menu.show()
        else:
            sys.exit(0)
        

def main():
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = MainMenu(login_dialog.cpf, login_dialog.role)
        main_window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
