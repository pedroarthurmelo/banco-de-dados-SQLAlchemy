import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QWidget, QLabel, QDialog, QGridLayout, QLineEdit, 
    QMessageBox, QTabWidget, QListWidget
)
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
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
    id = Column(Integer, primary_key=True)
    cpf = Column(String(11), unique=True)
    nome = Column(String(50))
    endereco = Column(String(100))
    telefone = Column(String(15))
    email = Column(String(50))
    apolices = relationship("Apolice", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome={self.nome}, cpf={self.cpf})>"

# Tabela Apólice
class Apolice(Base):
    __tablename__ = 'apolice'
    id = Column(Integer, primary_key=True)
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
    id = Column(Integer, primary_key=True)
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
    id = Column(Integer, primary_key=True)
    descricao = Column(String(200))
    data_ocorrencia = Column(Date)
    valor_acidente = Column(Float)
    tipo_acidente = Column(String(50))
    fk_apartamento = Column(Integer, ForeignKey('apartamento.id'))
    apartamento = relationship("Apartamento", back_populates="acidentes")

    def __repr__(self):
        return f"<Acidente(id={self.id}, descricao={self.descricao}, data_ocorrencia={self.data_ocorrencia}, apartamento_id={self.fk_apartamento})>"

# Criando as tabelas no banco de dados (se já não existirem)
Base.metadata.create_all(engine)

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerenciamento de Dados')
        self.setGeometry(100, 100, 500, 400)

        # Estilo da janela
        self.setStyleSheet(""" 
            QMainWindow { 
                background-color: #F0F0F0; 
            } 
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-size: 16px; 
                border-radius: 5px; 
                padding: 10px; 
            } 
            QPushButton:hover { 
                background-color: #45a049; 
            } 
            QDialog { 
                background-color: #FFF; 
            } 
            QLabel { 
                font-size: 14px; 
            } 
            QLineEdit { 
                padding: 5px; 
                border: 1px solid #ccc; 
                border-radius: 3px; 
            } 
        """)

        # Criar o QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

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

        layout = QGridLayout()

        if operacao == 'Ler':
            layout.addWidget(QLabel(f'Lista de {tipo}s:'), 0, 0)
            list_widget = QListWidget()
            layout.addWidget(list_widget, 1, 0, 1, 2)

            # Carregar os registros no QListWidget
            registros = self.get_registros(tipo)
            if tipo == 'Apartamento':
                for registro in registros:
                    # Obter IDs dos acidentes relacionados ao apartamento
                    acidente_id = [acidente.id for acidente in registro.acidentes]
                    list_widget.addItem(f"ID Apartamento: {registro.id} - IDs Acidentes: {acidente_id}")

            elif tipo == 'Apólice':
                for registro in registros:
                    # Obter ID do cliente relacionado à apólice
                    cliente_id = registro.cliente.id
                    list_widget.addItem(f"ID Apólice: {registro.id} - ID Cliente: {cliente_id}")

            else:  # Para Cliente e Acidente, apenas liste os registros
                for registro in registros:
                    list_widget.addItem(str(registro))

            submit_btn = QPushButton(f'Fechar')
            submit_btn.clicked.connect(dialog.accept)
            layout.addWidget(submit_btn, 2, 0, 1, 2)

        elif operacao == 'Adicionar':
            campos, inputs = self.criar_campos(tipo, layout)

            # Adicionar lista de apólices para Apartamento
            if tipo == 'Apartamento':
                layout.addWidget(QLabel('Apólices já cadastradas:'), len(campos), 0, 1, 2)
                apolice_list = QListWidget()
                apolices = self.get_registros('Apólice')
                for apolice in apolices:
                    apolice_list.addItem(f"ID {apolice.id} - {apolice.contato}")
                layout.addWidget(apolice_list, len(campos) + 1, 0, 1, 2)

            # Adicionar lista de clientes para Apólice
            if tipo == 'Apólice':
                layout.addWidget(QLabel('Clientes já cadastrados:'), len(campos), 0, 1, 2)
                cliente_list = QListWidget()
                clientes = self.get_registros('Cliente')
                for cliente in clientes:
                    cliente_list.addItem(f"ID {cliente.id} - {cliente.nome}")
                layout.addWidget(cliente_list, len(campos) + 1, 0, 1, 2)
            
            if tipo == 'Acidente':
                layout.addWidget(QLabel('Apartamentos já cadastrados:'), len(campos), 0, 1, 2)
                apartamento_list = QListWidget()
                apartamentos = self.get_registros('Apartamento')
                for apartamento in apartamentos:
                    apartamento_list.addItem(f"ID {apartamento.id} - {apartamento.endereco}")
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
            # Lista de IDs existentes
            layout.addWidget(QLabel(f'Selecione o ID do {tipo} para {operacao.lower()}:'))
            id_list = QListWidget()
            layout.addWidget(id_list, 1, 0, 1, 2)
            registros = self.get_registros(tipo)
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
            campos = ['Endereço', 'Andar', 'Tipo de Apartamento', 'Número do Apartamento']
        elif tipo == 'Acidente':
            campos = ['Descrição', 'Data da Ocorrência (DD-MM-YYYY)', 'Valor do Acidente', 'Tipo de Acidente']

        for i, campo in enumerate(campos):
            layout.addWidget(QLabel(campo), start_row + i, 0)
            input_field = QLineEdit()
            layout.addWidget(input_field, start_row + i, 1)
            inputs.append(input_field)

        return campos, inputs

    def adicionar_registro(self, tipo, inputs, dialog, apolice_list=None, cliente_list=None, apartamento_list=None):
        try:
            if tipo == 'Cliente':
                cliente = Cliente(
                    cpf=inputs[0].text(),
                    nome=inputs[1].text(),
                    endereco=inputs[2].text(),
                    telefone=inputs[3].text(),
                    email=inputs[4].text()
                )
                sessao.add(cliente)
                sessao.commit()
            elif tipo == 'Apólice':
                data_contrato = datetime.strptime(inputs[0].text(), '%d-%m-%Y').date()
                apolice = Apolice(
                    data_contrato=data_contrato,
                    contato=inputs[1].text(),
                    assinatura=inputs[2].text(),
                    fk_cliente=int(cliente_list.currentItem().text().split()[1])  # ID do cliente selecionado
                )
                sessao.add(apolice)
                sessao.commit()
            elif tipo == 'Apartamento':
                apartamento = Apartamento(
                    endereco=inputs[0].text(),
                    andar=int(inputs[1].text()),
                    tipo_ap=inputs[2].text(),
                    numero_ap=int(inputs[3].text()),
                    apolice_id=int(apolice_list.currentItem().text().split()[1])  # ID da apólice selecionada
                )
                sessao.add(apartamento)
                sessao.commit()
            elif tipo == 'Acidente':
                data_ocorrencia = datetime.strptime(inputs[1].text(), '%d-%m-%Y').date()
                acidente = Acidente(
                    descricao=inputs[0].text(),
                    data_ocorrencia=data_ocorrencia,
                    valor_acidente=float(inputs[2].text()),
                    tipo_acidente=inputs[3].text(),
                    fk_apartamento=int(apartamento_list.currentItem().text().split()[1])  # ID do apartamento selecionado
                )
                sessao.add(acidente)
                sessao.commit()

            QMessageBox.information(dialog, 'Sucesso', f'{tipo} adicionado com sucesso!')
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, 'Erro', f'Erro ao adicionar {tipo}: {e}')

    def atualizar_registro(self, tipo, inputs, id_list, dialog):
        try:
            selected_id = int(id_list.currentItem().text().split()[1])  # ID do item selecionado
            if tipo == 'Cliente':
                cliente = sessao.query(Cliente).filter(Cliente.id == selected_id).first()
                cliente.cpf = inputs[0].text()
                cliente.nome = inputs[1].text()
                cliente.endereco = inputs[2].text()
                cliente.telefone = inputs[3].text()
                cliente.email = inputs[4].text()
            elif tipo == 'Apólice':
                apolice = sessao.query(Apolice).filter(Apolice.id == selected_id).first()
                apolice.data_contrato = datetime.strptime(inputs[0].text(), '%d-%m-%Y').date()
                apolice.contato = inputs[1].text()
                apolice.assinatura = inputs[2].text()
            elif tipo == 'Apartamento':
                apartamento = sessao.query(Apartamento).filter(Apartamento.id == selected_id).first()
                apartamento.endereco = inputs[0].text()
                apartamento.andar = int(inputs[1].text())
                apartamento.tipo_ap = inputs[2].text()
                apartamento.numero_ap = int(inputs[3].text())
            elif tipo == 'Acidente':
                acidente = sessao.query(Acidente).filter(Acidente.id == selected_id).first()
                acidente.descricao = inputs[0].text()
                acidente.data_ocorrencia = datetime.strptime(inputs[1].text(), '%d-%m-%Y').date()
                acidente.valor_acidente = float(inputs[2].text())
                acidente.tipo_acidente = inputs[3].text()

            sessao.commit()
            QMessageBox.information(dialog, 'Sucesso', f'{tipo} atualizado com sucesso!')
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, 'Erro', f'Erro ao atualizar {tipo}: {e}')

    def deletar_registro(self, tipo, id_list, dialog):
        try:
            selected_id = int(id_list.currentItem().text().split()[1])  # ID do item selecionado
            if tipo == 'Cliente':
                cliente = sessao.query(Cliente).filter(Cliente.id == selected_id).first()
                sessao.delete(cliente)
            elif tipo == 'Apólice':
                apolice = sessao.query(Apolice).filter(Apolice.id == selected_id).first()
                sessao.delete(apolice)
            elif tipo == 'Apartamento':
                apartamento = sessao.query(Apartamento).filter(Apartamento.id == selected_id).first()
                sessao.delete(apartamento)
            elif tipo == 'Acidente':
                acidente = sessao.query(Acidente).filter(Acidente.id == selected_id).first()
                sessao.delete(acidente)

            sessao.commit()
            QMessageBox.information(dialog, 'Sucesso', f'{tipo} deletado com sucesso!')
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, 'Erro', f'Erro ao deletar {tipo}: {e}')

    def get_registros(self, tipo):
        if tipo == 'Cliente':
            return sessao.query(Cliente).all()
        elif tipo == 'Apólice':
            return sessao.query(Apolice).all()
        elif tipo == 'Apartamento':
            return sessao.query(Apartamento).all()
        elif tipo == 'Acidente':
            return sessao.query(Acidente).all()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())