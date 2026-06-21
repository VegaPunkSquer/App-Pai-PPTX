import requests

from atualizador import checar_e_atualizar
import sys
import os
import json
import subprocess
import traceback
import webbrowser
import time
from PySide6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QColorDialog, QMessageBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QListWidget, QSlider, QProgressDialog,
    QTabWidget, QComboBox, QLineEdit
)
from PySide6.QtGui import QColor, QPixmap, QFont, QPalette, QIcon
from PySide6.QtCore import QThread, Qt, QSize, Signal
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.util import Pt
import motor_ia
import ctypes
import comtypes.client

# --- RESOLUÇÃO DE CAMINHOS ABSOLUTOS ---
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable) # Onde o .exe está (para configs e saves)
    bundle_dir = sys._MEIPASS # Onde o PyInstaller extrai os assets embutidos
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundle_dir = base_dir

CONFIG_FILE = os.path.join(base_dir, "config.json")

# --- JANELA DE ESCOLHA DE IMAGENS ---
class ImageSelectionDialog(QDialog):
    def __init__(self, slide_images_dict, roteiro, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escolha as Imagens dos Slides")
        self.resize(900, 700)
        self.slide_images_dict = slide_images_dict
        self.roteiro = roteiro
        self.selected_images = {} 
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.list_slides = QListWidget()
        self.list_slides.setFixedWidth(200)
        self.list_slides.setStyleSheet("font-size: 14px; padding: 5px;")
        for slide_idx in self.slide_images_dict.keys():
            self.list_slides.addItem(f"Slide {slide_idx + 1}")
        
        self.list_slides.currentRowChanged.connect(self.show_options_for_slide)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.container_opcoes = QWidget()
        self.layout_opcoes = QVBoxLayout(self.container_opcoes)
        self.layout_opcoes.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.container_opcoes)

        layout.addWidget(self.list_slides)
        layout.addWidget(self.scroll_area)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        btn_concluir = QPushButton("Concluir Escolhas e Gerar PPTX")
        btn_concluir.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 15px; font-size: 16px; border-radius: 5px;")
        btn_concluir.setCursor(Qt.PointingHandCursor)
        btn_concluir.clicked.connect(self.accept)
        main_layout.addWidget(btn_concluir)

        self.setLayout(main_layout)

        if self.list_slides.count() > 0:
            self.list_slides.setCurrentRow(0)

    def show_options_for_slide(self, row_idx):
        if row_idx < 0: return

        while self.layout_opcoes.count():
            item = self.layout_opcoes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            slide_idx = list(self.slide_images_dict.keys())[row_idx]
            caminhos = self.slide_images_dict[slide_idx]
        except IndexError: return

        dados_slide = self.roteiro[slide_idx]
        titulo_slide = dados_slide.get("titulo", "Sem Título")
        texto_resumo = dados_slide.get("texto", "")[:120] + "..."
        
        lbl_instrucao = QLabel(f"Slide {slide_idx + 1}: {titulo_slide}")
        lbl_instrucao.setFont(QFont("Arial", 16, weight=QFont.Bold))
        lbl_instrucao.setWordWrap(True)
        self.layout_opcoes.addWidget(lbl_instrucao)

        lbl_contexto = QLabel(f"Contexto: {texto_resumo}")
        lbl_contexto.setFont(QFont("Arial", 11, italic=True))
        lbl_contexto.setStyleSheet("padding-bottom: 15px; color: gray;")
        lbl_contexto.setWordWrap(True)
        self.layout_opcoes.addWidget(lbl_contexto)

        for caminho in caminhos:
            container_img = QWidget()
            vbox = QVBoxLayout(container_img)
            vbox.setAlignment(Qt.AlignCenter)

            lbl_img = QLabel()
            pixmap = QPixmap(caminho).scaled(500, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img.setPixmap(pixmap)
            lbl_img.setAlignment(Qt.AlignCenter)

            btn_select = QPushButton()
            btn_select.setCursor(Qt.PointingHandCursor)
            
            if self.selected_images.get(slide_idx) == caminho:
                btn_select.setText("✅ IMAGEM SELECIONADA")
                btn_select.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 5px;")
                container_img.setStyleSheet("background-color: rgba(40, 167, 69, 0.2); border: 2px solid #28a745; border-radius: 10px;")
            else:
                btn_select.setText("Escolher esta imagem")
                btn_select.setStyleSheet("background-color: #e0e0e0; color: black; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 5px;")
                container_img.setStyleSheet("border: 1px solid transparent;")

            btn_select.clicked.connect(lambda checked=False, s=slide_idx, c=caminho, r=row_idx: self.select_image(s, c, r))

            vbox.addWidget(lbl_img)
            vbox.addWidget(btn_select)
            self.layout_opcoes.addWidget(container_img)
            
        self.layout_opcoes.addStretch()

    def select_image(self, slide_idx, caminho, row_idx):
        self.selected_images[slide_idx] = caminho
        self.show_options_for_slide(row_idx)
        
class WorkerAuthApp(QThread):
    sucesso = Signal(str)
    erro = Signal(str)

    def __init__(self, modo, payload):
        super().__init__()
        self.modo = modo # 'login' ou 'registrar'
        self.payload = payload

    def run(self):
        url = "https://vegap-masterapp.hf.space"
        endpoint = f"{url}/auth/app/{self.modo}"
        try:
            resp = requests.post(endpoint, json=self.payload, timeout=10)
            if resp.status_code in [200, 201]:
                dados = resp.json()
                self.sucesso.emit(dados.get("access_token", ""))
            else:
                self.erro.emit(f"Erro: {resp.json().get('detail', resp.text)}")
        except Exception as e:
            self.erro.emit(f"Falha de conexão com o Master: {str(e)}")

class LoginCadastroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conta VegaTech")
        self.setFixedSize(350, 400)
        self.token_recebido = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # ABA LOGIN
        self.tab_login = QWidget()
        layout_login = QVBoxLayout(self.tab_login)
        self.inp_login_email = QLineEdit()
        self.inp_login_email.setPlaceholderText("E-mail")
        self.inp_login_senha = QLineEdit()
        self.inp_login_senha.setPlaceholderText("Senha")
        self.inp_login_senha.setEchoMode(QLineEdit.Password)
        self.btn_logar = QPushButton("Entrar")
        self.btn_logar.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-weight: bold;")
        self.btn_logar.clicked.connect(self.fazer_login)
        
        layout_login.addWidget(QLabel("Já tem uma conta? Acesse:"))
        layout_login.addWidget(self.inp_login_email)
        layout_login.addWidget(self.inp_login_senha)
        layout_login.addWidget(self.btn_logar)
        layout_login.addStretch()
        
        # ABA CADASTRO
        self.tab_cadastro = QWidget()
        layout_cad = QVBoxLayout(self.tab_cadastro)
        self.inp_cad_nome = QLineEdit()
        self.inp_cad_nome.setPlaceholderText("Nome Completo")
        self.inp_cad_email = QLineEdit()
        self.inp_cad_email.setPlaceholderText("E-mail")
        self.inp_cad_doc = QLineEdit()
        self.inp_cad_doc.setPlaceholderText("CPF ou CNPJ (Apenas números)")
        self.inp_cad_senha = QLineEdit()
        self.inp_cad_senha.setPlaceholderText("Crie uma Senha")
        self.inp_cad_senha.setEchoMode(QLineEdit.Password)
        self.btn_cadastrar = QPushButton("Criar Conta")
        self.btn_cadastrar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        self.btn_cadastrar.clicked.connect(self.fazer_cadastro)
        
        layout_cad.addWidget(QLabel("Novo por aqui? Cadastre-se:"))
        layout_cad.addWidget(self.inp_cad_nome)
        layout_cad.addWidget(self.inp_cad_email)
        layout_cad.addWidget(self.inp_cad_doc)
        layout_cad.addWidget(self.inp_cad_senha)
        layout_cad.addWidget(self.btn_cadastrar)
        layout_cad.addStretch()
        
        self.tabs.addTab(self.tab_login, "Login")
        self.tabs.addTab(self.tab_cadastro, "Criar Conta")
        layout.addWidget(self.tabs)

    def fazer_login(self):
        email = self.inp_login_email.text().strip()
        senha = self.inp_login_senha.text()
        if not email or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha e-mail e senha.")
            return
        self.btn_logar.setEnabled(False)
        self.btn_logar.setText("Autenticando...")
        
        payload = {"email": email, "senha": senha}
        self.worker = WorkerAuthApp('login', payload)
        self.worker.sucesso.connect(self.auth_sucesso)
        self.worker.erro.connect(self.auth_erro)
        self.worker.start()

    def fazer_cadastro(self):
        nome = self.inp_cad_nome.text().strip()
        email = self.inp_cad_email.text().strip()
        doc = "".join(filter(str.isdigit, self.inp_cad_doc.text()))
        senha = self.inp_cad_senha.text()
        
        if not nome or not email or not doc or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
            return
            
        self.btn_cadastrar.setEnabled(False)
        self.btn_cadastrar.setText("Registrando...")
        
        payload = {"nome": nome, "email": email, "documento": doc, "senha": senha, "produto": "SmartSlides Pro"}
        self.worker = WorkerAuthApp('registrar', payload)
        self.worker.sucesso.connect(self.auth_sucesso)
        self.worker.erro.connect(self.auth_erro)
        self.worker.start()

    def auth_sucesso(self, token):
        self.token_recebido = token
        QMessageBox.information(self, "Sucesso", "Conta conectada com sucesso!")
        self.accept()

    def auth_erro(self, msg):
        self.btn_logar.setEnabled(True)
        self.btn_logar.setText("Entrar")
        self.btn_cadastrar.setEnabled(True)
        self.btn_cadastrar.setText("Criar Conta")
        QMessageBox.critical(self, "Aviso", msg)

# =========================================================
# LOJA UNIVERSAL (VITRINE, CHECKOUT E CUPÕES)
# =========================================================
class WorkerVitrine(QThread):
    sucesso = Signal(dict)
    erro = Signal(str)

    def run(self):
        try:
            # Usamos %20 no lugar do espaço para a URL ficar perfeitamente legível pro Master
            resp = requests.get("https://vegap-masterapp.hf.space/master/vitrine/SmartSlides%20Pro")
            if resp.status_code == 200:
                self.sucesso.emit(resp.json())
            else:
                self.erro.emit("Erro ao carregar a vitrine.")
        except Exception as e:
            self.erro.emit(str(e))

class WorkerCheckout(QThread):
    sucesso = Signal(dict)
    erro = Signal(str)

    def __init__(self, token, produto_id, plano_nome, cupom):
        super().__init__()
        self.payload = {
            "token": token,
            "produto_id": produto_id,
            "plano_nome": plano_nome,
            "cupom": cupom
        }

    def run(self):
        try:
            resp = requests.post("https://vegap-masterapp.hf.space/master/pagamentos/gerar-checkout", json=self.payload)
            if resp.status_code == 200:
                self.sucesso.emit(resp.json())
            else:
                self.erro.emit(resp.json().get("detail", "Erro desconhecido"))
        except Exception as e:
            self.erro.emit(str(e))

class WorkerStatusPagamento(QThread):
    sucesso = Signal()

    def __init__(self, cobranca_id):
        super().__init__()
        self.cobranca_id = cobranca_id
        self.rodando = True

    def run(self):
        while self.rodando:
            try:
                resp = requests.get(f"https://vegap-masterapp.hf.space/master/pagamentos/checar-status?cobranca_id={self.cobranca_id}")
                if resp.status_code == 200 and resp.json().get("pago"):
                    self.sucesso.emit()
                    break
            except:
                pass
            time.sleep(5)

    def stop(self):
        self.rodando = False

class LojaDialog(QDialog):
    def __init__(self, token_cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛒 Loja VegaTech - SmartSlides Pro")
        self.setFixedSize(450, 500)
        self.token_cliente = token_cliente
        self.produto_id = None
        self.worker_status = None
        self.init_ui()
        self.carregar_vitrine()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.lbl_titulo = QLabel("⏳ A carregar planos disponíveis...")
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.lbl_titulo)
        
        # --- NOVO: SCROLL AREA PARA OS PLANOS NÃO ESMAGAREM ---
        self.scroll_planos = QScrollArea()
        self.scroll_planos.setWidgetResizable(True)
        self.scroll_planos.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.widget_planos = QWidget()
        self.widget_planos.setStyleSheet("background-color: transparent;")
        self.container_planos = QVBoxLayout(self.widget_planos)
        self.container_planos.setContentsMargins(0, 0, 10, 0) # Margem pra barra de rolagem não colar
        self.container_planos.setSpacing(10)
        
        self.scroll_planos.setWidget(self.widget_planos)
        self.layout.addWidget(self.scroll_planos)
        # ------------------------------------------------------
        
        self.inp_cupom = QLineEdit()
        self.inp_cupom.setPlaceholderText("Tem um cupão de desconto? (Opcional)")
        self.inp_cupom.setStyleSheet("font-size: 14px; padding: 10px; border-radius: 5px; border: 1px solid gray;")
        self.layout.addWidget(self.inp_cupom)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #0078d7; font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(self.lbl_status)

    def carregar_vitrine(self):
        self.worker_vitrine = WorkerVitrine()
        self.worker_vitrine.sucesso.connect(self.montar_planos)
        self.worker_vitrine.erro.connect(lambda e: self.lbl_titulo.setText("Erro ao carregar a loja."))
        self.worker_vitrine.start()

    def montar_planos(self, dados):
        from PySide6.QtWidgets import QFrame # Garante a importação do QFrame para o visual
        
        self.produto_id = dados.get("id")
        planos = dados.get("planos_precos", {})
        
        # Limpa o container caso a pessoa clique duas vezes
        while self.container_planos.count():
            item = self.container_planos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        if not planos:
            self.lbl_titulo.setText("Nenhum plano configurado no Master.")
            return
            
        self.lbl_titulo.setText("Escolha o Pacote Ideal para Você:")
        
        # MÁGICA DA ORDENAÇÃO: Força a vitrine a seguir a hierarquia clássica de SaaS
        ordem_ciclos = {"mensal": 1, "trimestral": 2, "semestral": 3, "anual": 4, "unico": 5}
        planos_ordenados = sorted(
            planos.items(), 
            key=lambda x: ordem_ciclos.get(str(x[1].get("ciclo")).lower(), 99)
        )
        
        for nome_plano, detalhes in planos_ordenados:
            valor = float(detalhes.get("valor", 0.0))
            trial_dias = int(detalhes.get("trial_dias", 0))
            ciclo = detalhes.get("ciclo", "unico").capitalize()
            
            # MÁGICA VISUAL: Corta o "_MENSAL" do nome para o cliente ler só "SAAS"
            nome_exibicao = nome_plano.split("_")[0] if "_" in nome_plano else nome_plano
            
            # CRIA UM CARD CHIQUE DE ALTA CONVERSÃO
            card = QFrame()
            card.setStyleSheet("background-color: #262626; border: 1px solid #444; border-radius: 12px; margin-bottom: 5px;")
            card_layout = QVBoxLayout(card)
            
            # Título e Preço (Usa o nome maquiado)
            lbl_nome = QLabel(f"⭐ {nome_exibicao.upper()}")
            lbl_nome.setStyleSheet("font-size: 16px; font-weight: 900; color: white; border: none;")
            
            txt_ciclo = f" / {ciclo}" if ciclo != "Unico" else ""
            lbl_preco = QLabel(f"R$ {valor:.2f}{txt_ciclo}")
            lbl_preco.setStyleSheet("font-size: 24px; font-weight: 800; color: #28a745; border: none;")
            
            card_layout.addWidget(lbl_nome)
            card_layout.addWidget(lbl_preco)
            
            # GATILHO MENTAL DO TRIAL (O SEGREDO DA CONVERSÃO!)
            if trial_dias > 0:
                lbl_trial = QLabel(f"🎁 {trial_dias} DIAS TOTALMENTE GRÁTIS!")
                lbl_trial.setStyleSheet("""
                    font-size: 13px; font-weight: bold; color: #ffc107; 
                    background-color: rgba(255, 193, 7, 0.1); 
                    padding: 6px; border-radius: 4px; border: 1px solid #ffc107;
                """)
                lbl_trial.setAlignment(Qt.AlignCenter)
                card_layout.addWidget(lbl_trial)
            
            # Botão de Assinar
            btn_comprar = QPushButton(f"ASSINAR AGORA")
            btn_comprar.setMinimumHeight(45) # <--- BLINDAGEM CONTRA ESMAGAMENTO
            btn_comprar.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; font-size: 15px; border-radius: 6px; border: none;")
            btn_comprar.setCursor(Qt.PointingHandCursor)
            btn_comprar.clicked.connect(lambda checked=False, p=nome_plano: self.comprar_plano(p))
            
            card_layout.addWidget(btn_comprar)
            self.container_planos.addWidget(card)

    def comprar_plano(self, plano_nome):
        if not self.token_cliente:
            dialog_auth = LoginCadastroDialog(self)
            if dialog_auth.exec() == QDialog.Accepted:
                self.token_cliente = dialog_auth.token_recebido
            else:
                return

        cupom = self.inp_cupom.text().strip()
        self.lbl_status.setText("A gerar ambiente seguro de pagamento...")
        self.setEnabled(False)
        
        self.worker_checkout = WorkerCheckout(self.token_cliente, self.produto_id, plano_nome, cupom)
        self.worker_checkout.sucesso.connect(self.processar_checkout)
        self.worker_checkout.erro.connect(self.erro_checkout)
        self.worker_checkout.start()

    def processar_checkout(self, dados):
        if dados.get("gratuito"):
            QMessageBox.information(self, "Sucesso", dados.get("mensagem", "Acesso VIP liberado com sucesso!"))
            self.accept()
            return
            
        checkout_url = dados.get("checkout_url")
        cobranca_id = dados.get("cobranca_id")
        
        if checkout_url:
            webbrowser.open(checkout_url)
            self.lbl_status.setText("Navegador aberto! A aguardar o pagamento...")
            self.setEnabled(True)
            
            self.worker_status = WorkerStatusPagamento(cobranca_id)
            self.worker_status.sucesso.connect(self.pagamento_confirmado)
            self.worker_status.start()

    def erro_checkout(self, erro):
        self.setEnabled(True)
        self.lbl_status.setText("")
        QMessageBox.critical(self, "Erro", erro)

    def pagamento_confirmado(self):
        QMessageBox.information(self, "Sucesso", "Pagamento confirmado! Acesso Liberado!")
        self.accept()

    def closeEvent(self, event):
        if self.worker_status:
            self.worker_status.stop()
        super().closeEvent(event)

# --- JANELA DE CONFIGURAÇÕES ---
class ConfigDialog(QDialog):
    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configurações do App")
        self.resize(500, 400)
        self.config = current_config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Aba 1: Licença
        self.tab_licenca = QWidget()
        vbox_lic = QVBoxLayout(self.tab_licenca)
        
        vbox_lic.addWidget(QLabel("<b>Status da Licença atual:</b> (Simulação)"))
        self.combo_licenca = QComboBox()
        self.combo_licenca.addItems(["FREE (Edição Manual)", "BYOK (Sua Chave)", "SAAS (Chave Embutida)"])
        self.combo_licenca.setCurrentText(self.config.get("license", "FREE"))
        self.combo_licenca.currentTextChanged.connect(self.update_ia_tab_visibility)
        vbox_lic.addWidget(self.combo_licenca)
        vbox_lic.addStretch()
        
        # Aba 2: Inteligência Artificial
        self.tab_ia = QWidget()
        self.vbox_ia = QVBoxLayout(self.tab_ia)
        
        self.lbl_aviso_saas = QLabel("✅ <b>Licença SaaS Ativa</b>\nVocê está utilizando a chave premium embutida.\nNenhuma configuração extra é necessária.")
        self.lbl_aviso_saas.setStyleSheet("color: #28a745;")
        self.vbox_ia.addWidget(self.lbl_aviso_saas)
        
        self.container_byok = QWidget()
        vbox_byok = QVBoxLayout(self.container_byok)
        vbox_byok.setContentsMargins(0,0,0,0)
        vbox_byok.addWidget(QLabel("Sua Chave de API Gemini (BYOK):"))
        self.txt_api_key = QLineEdit(self.config.get("api_key", ""))
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        vbox_byok.addWidget(self.txt_api_key)
        self.vbox_ia.addWidget(self.container_byok)
        
        # --- MODELOS DINÂMICOS ---
        hbox_model = QHBoxLayout()
        self.combo_model = QComboBox()
        self.combo_model.addItem(self.config.get("model", "gemini-2.5-flash"))
        
        self.btn_load_models = QPushButton("🔄 Carregar Modelos")
        self.btn_load_models.clicked.connect(self.load_dynamic_models)
        
        hbox_model.addWidget(QLabel("Modelo de Inteligência Artificial:"))
        hbox_model.addWidget(self.combo_model)
        hbox_model.addWidget(self.btn_load_models)
        self.vbox_ia.addLayout(hbox_model)
        self.vbox_ia.addStretch()
        
        # Aba 3: Aparência & Acessibilidade
        self.tab_visual = QWidget()
        vbox_vis = QVBoxLayout(self.tab_visual)
        
        vbox_vis.addWidget(QLabel("Tema do Aplicativo:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Escuro", "Claro"])
        self.combo_theme.setCurrentText(self.config.get("theme", "Escuro"))
        vbox_vis.addWidget(self.combo_theme)
        
        vbox_vis.addWidget(QLabel("\n🔎 Zoom da Tela (Acessibilidade):"))
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(50, 250)
        self.slider_zoom.setValue(self.config.get("zoom", 100))
        self.lbl_zoom_val = QLabel(f"{self.slider_zoom.value()}%")
        self.slider_zoom.valueChanged.connect(lambda v: self.lbl_zoom_val.setText(f"{v}%"))
        
        hbox_zoom = QHBoxLayout()
        hbox_zoom.addWidget(self.slider_zoom)
        hbox_zoom.addWidget(self.lbl_zoom_val)
        vbox_vis.addLayout(hbox_zoom)
        vbox_vis.addStretch()

        self.tabs.addTab(self.tab_licenca, "Licença")
        self.tabs.addTab(self.tab_ia, "Inteligência Artificial")
        self.tabs.addTab(self.tab_visual, "Aparência")
        layout.addWidget(self.tabs)

        btn_salvar = QPushButton("Salvar Configurações")
        btn_salvar.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-weight: bold;")
        btn_salvar.clicked.connect(self.save_and_close)
        layout.addWidget(btn_salvar)
        
        self.update_ia_tab_visibility(self.combo_licenca.currentText())

    def update_ia_tab_visibility(self, licensa):
        if licensa == "SAAS (Chave Embutida)":
            self.lbl_aviso_saas.show()
            self.container_byok.hide()
            self.tabs.setTabEnabled(1, True)
        elif licensa == "BYOK (Sua Chave)":
            self.lbl_aviso_saas.hide()
            self.container_byok.show()
            self.tabs.setTabEnabled(1, True)
        else:
            self.tabs.setTabEnabled(1, False) 

    def load_dynamic_models(self):
        licensa = self.combo_licenca.currentText()
        chave = self.txt_api_key.text().strip() if licensa == "BYOK (Sua Chave)" else None
        
        self.btn_load_models.setText("⏳ Carregando...")
        QApplication.processEvents()
        
        try:
            modelos = motor_ia.listar_modelos(chave)
            self.combo_model.clear()
            self.combo_model.addItems(modelos)
            
            modelo_salvo = self.config.get("model", "gemini-2.5-flash")
            if modelo_salvo in modelos:
                self.combo_model.setCurrentText(modelo_salvo)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível carregar os modelos: {str(e)}")
            
        self.btn_load_models.setText("🔄 Carregar Modelos")

    def save_and_close(self):
        licenca_escolhida = self.combo_licenca.currentText()
        
        # 1. Barreira do BYOK (O Aviso Salva-Vidas)
        if licenca_escolhida == "BYOK (Sua Chave)":
            resp = QMessageBox.question(
                self, 
                "Aviso Importante - Plano BYOK", 
                "O plano BYOK (Bring Your Own Key) exige que você tenha sua própria chave de desenvolvedor da API do Google Gemini.\n\n"
                "Se você não é desenvolvedor ou não sabe do que se trata, recomendamos adquirir o plano SAAS para evitar dores de cabeça.\n\n"
                "Tem certeza que deseja prosseguir com o BYOK?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return # Aborta o salvamento, deixa ele na tela para trocar
                
        # 2. Barreira do SAAS (Autenticação Obrigatória + Checkout na Loja)
        if licenca_escolhida == "SAAS (Chave Embutida)":
            if not self.config.get("token_master"):
                dialog_auth = LoginCadastroDialog(self)
                if dialog_auth.exec() == QDialog.Accepted:
                    self.config["token_master"] = dialog_auth.token_recebido
                else:
                    return # Ele fechou a janela sem logar, então aborta o salvamento
            
            # Depois de garantir que o utilizador tem sessão iniciada, abre a Loja!
            loja = LojaDialog(self.config.get("token_master"), self)
            if loja.exec() == QDialog.Accepted:
                # Se ele pagou ou usou o cupão VIP, atualiza o token por precaução e avança
                self.config["token_master"] = loja.token_cliente
            else:
                # Se fechou a loja sem pagar, aborta a ativação da licença SAAS
                return

        # Se passou pelas barreiras, salva tudo
        self.config["license"] = licenca_escolhida
        self.config["api_key"] = self.txt_api_key.text().strip()
        self.config["model"] = self.combo_model.currentText()
        self.config["theme"] = self.combo_theme.currentText()
        self.config["zoom"] = self.slider_zoom.value()
        self.accept()

# --- APLICATIVO PRINCIPAL ---
class AppPaiVega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartSlides Pro")
        self.resize(500, 500)
        
        # --- ÍCONE DA JANELA E BARRA DE TAREFAS ---
        icon_path = os.path.join(bundle_dir, "assets", "SmartSlides.ico") # <-- CORRIGIDO PARA BUNDLE_DIR
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            # Macete do CTYPES: Força o Windows a respeitar o seu ícone
            if os.name == 'nt':
                myappid = 'vega.smartslides.pro.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.config = self.load_config()
        self.last_dir = self.config.get("last_dir", "") # GUARDA A ÚLTIMA PASTA
        self.pptx_path = None
        self.last_saved_pptx = None # Guarda o último editado para o conversor de PDF
        self.bg_path = None
        self.text_color = None
        self.fill_color = None

        self.init_ui()
        self.apply_theme()
        self.apply_zoom(self.config.get("zoom", 100))

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"license": "FREE", "api_key": "", "model": "gemini-2.5-flash", "theme": "Escuro", "zoom": 100}

    def save_config(self):
        self.config["last_dir"] = self.last_dir
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def open_config(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            self.save_config()
            self.apply_theme()
            self.apply_zoom(self.config["zoom"])
            self.update_main_ui_lock()

    def apply_theme(self):
        tema = self.config.get("theme", "Escuro")
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        if tema == "Escuro":
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.black)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
        app.setPalette(palette)

    def apply_zoom(self, val):
        base_size = 9
        new_size = int(base_size * (val / 100.0))
        font = self.font()
        font.setPointSize(new_size)
        self.setFont(font)

    def create_color_indicator(self):
        lbl = QLabel()
        lbl.setFixedSize(24, 24)
        lbl.setStyleSheet("background-color: transparent; border: 1px solid gray; border-radius: 12px;")
        return lbl

    def init_ui(self):
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setSpacing(15)

        hbox_top = QHBoxLayout()
        hbox_top.addStretch()
        self.btn_config = QPushButton("⚙️ Configurações / Licença")
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.clicked.connect(self.open_config)
        hbox_top.addWidget(self.btn_config)
        self.main_layout.addLayout(hbox_top)

        self.btn_load = QPushButton("1. Carregar Apresentação Pronta (.pptx)")
        self.btn_load.clicked.connect(self.load_pptx)
        self.lbl_pptx = QLabel("Nenhum arquivo selecionado")
        self.lbl_pptx.setStyleSheet("color: gray; font-style: italic;")

        self.main_layout.addWidget(self.btn_load)
        self.main_layout.addWidget(self.lbl_pptx)

        hbox_ia = QHBoxLayout()
        self.txt_tema = QTextEdit()
        self.txt_tema.setPlaceholderText("Ou digite o tema para a IA criar do zero...")
        self.txt_tema.setMaximumHeight(80) 
        
        self.btn_gerar_ia = QPushButton("Criar Apresentação\nAutomática (IA)")
        self.btn_gerar_ia.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold; padding: 10px;")
        self.btn_gerar_ia.setMinimumHeight(80)
        self.btn_gerar_ia.clicked.connect(self.gerar_com_ia)
        
        hbox_ia.addWidget(self.txt_tema)
        hbox_ia.addWidget(self.btn_gerar_ia)
        self.main_layout.addLayout(hbox_ia)

        hbox_text = QHBoxLayout()
        self.btn_text_color = QPushButton("2. Escolher Cor de Todo o Texto (Opcional)")
        self.btn_text_color.clicked.connect(self.choose_text_color)
        self.lbl_text_color_indicator = self.create_color_indicator()
        
        hbox_text.addWidget(self.btn_text_color)
        hbox_text.addWidget(self.lbl_text_color_indicator)
        hbox_text.addStretch()
        self.main_layout.addLayout(hbox_text)

        hbox_fill = QHBoxLayout()
        self.btn_fill_color = QPushButton("3. Escolher Cor de Fundo dos Cards (Opcional)")
        self.btn_fill_color.clicked.connect(self.choose_fill_color)
        self.lbl_fill_color_indicator = self.create_color_indicator()
        
        hbox_fill.addWidget(self.btn_fill_color)
        hbox_fill.addWidget(self.lbl_fill_color_indicator)
        hbox_fill.addStretch()
        self.main_layout.addLayout(hbox_fill)

        hbox_bg = QHBoxLayout()
        self.btn_bg = QPushButton("4. Fundo do Slide (Opcional)")
        self.btn_bg.clicked.connect(self.load_bg)
        self.lbl_bg_preview = QLabel("Sem imagem")
        self.lbl_bg_preview.setFixedSize(80, 80)
        self.lbl_bg_preview.setAlignment(Qt.AlignCenter)
        self.lbl_bg_preview.setStyleSheet("border: 1px dashed gray;")
        
        hbox_bg.addWidget(self.btn_bg)
        hbox_bg.addWidget(self.lbl_bg_preview)
        hbox_bg.addStretch()
        self.main_layout.addLayout(hbox_bg)

        hbox_scale = QHBoxLayout()
        self.chk_scale = QCheckBox("5. Reduzir imagens em (%):")
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(1, 99)
        self.spin_scale.setValue(20)
        self.spin_scale.setEnabled(False) 
        self.chk_scale.toggled.connect(self.spin_scale.setEnabled)
        
        hbox_scale.addWidget(self.chk_scale)
        hbox_scale.addWidget(self.spin_scale)
        hbox_scale.addStretch()
        self.main_layout.addLayout(hbox_scale)

        # 5.1. Aumentar Textos
        hbox_text_scale = QHBoxLayout()
        self.chk_text_scale = QCheckBox("5.1. Aumentar textos (Título e Corpo) em (%):")
        self.spin_text_scale = QSpinBox()
        self.spin_text_scale.setRange(1, 150)
        self.spin_text_scale.setValue(20)
        self.spin_text_scale.setEnabled(False) 
        
        self.lbl_text_preview = QLabel("Aa Exemplo")
        self.lbl_text_preview.setStyleSheet("color: gray; font-size: 14px;")
        self.lbl_text_preview.setVisible(False)

        def update_text_preview():
            if self.chk_text_scale.isChecked():
                self.lbl_text_preview.setVisible(True)
                base_px = 14
                new_px = int(base_px * (1 + (self.spin_text_scale.value() / 100.0)))
                self.lbl_text_preview.setStyleSheet(f"color: #28a745; font-size: {new_px}px; font-weight: bold;")
            else:
                self.lbl_text_preview.setVisible(False)

        self.chk_text_scale.toggled.connect(self.spin_text_scale.setEnabled)
        self.chk_text_scale.toggled.connect(update_text_preview)
        self.spin_text_scale.valueChanged.connect(update_text_preview)

        hbox_text_scale.addWidget(self.chk_text_scale)
        hbox_text_scale.addWidget(self.spin_text_scale)
        hbox_text_scale.addWidget(self.lbl_text_preview)
        hbox_text_scale.addStretch()
        self.main_layout.addLayout(hbox_text_scale)

        self.btn_save = QPushButton("6. Processar Apresentação e Salvar")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setStyleSheet("background-color: #333; color: white; font-weight: bold; font-size: 14px;")
        self.btn_save.clicked.connect(self.process_and_save)
        self.main_layout.addWidget(self.btn_save)

        # --- 7. BOTAO CONVERTER PARA PDF ---
        self.btn_pdf = QPushButton("7. Converter o PPTX atual para PDF")
        self.btn_pdf.setMinimumHeight(35)
        self.btn_pdf.setStyleSheet("background-color: #a8201a; color: white; font-weight: bold;")
        self.btn_pdf.clicked.connect(self.export_to_pdf)
        self.main_layout.addWidget(self.btn_pdf)

        self.setCentralWidget(self.main_container)
        self.update_main_ui_lock() 

    def update_main_ui_lock(self):
        if self.config.get("license", "FREE") == "FREE":
            self.txt_tema.setReadOnly(True)
            self.txt_tema.setPlaceholderText("🔒 Geração Inteligente bloqueada (Licença FREE).")
            self.txt_tema.setStyleSheet("background-color: #444; color: #888; border: 1px solid #333;")
            
            self.btn_gerar_ia.setEnabled(False)
            self.btn_gerar_ia.setStyleSheet("background-color: #555; color: #888; font-weight: bold; padding: 10px;")
        else:
            self.txt_tema.setReadOnly(False)
            self.txt_tema.setPlaceholderText("Ou digite o tema para a IA criar do zero...")
            self.txt_tema.setStyleSheet("") 
            
            self.btn_gerar_ia.setEnabled(True)
            self.btn_gerar_ia.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold; padding: 10px;")

    def load_pptx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PPTX", self.last_dir, "PowerPoint (*.pptx)")
        if path:
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.pptx_path = path
            self.lbl_pptx.setText(os.path.basename(path))

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
            self.lbl_text_color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray; border-radius: 12px;")

    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.lbl_fill_color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray; border-radius: 12px;")

    def load_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", self.last_dir, "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.bg_path = path
            pixmap = QPixmap(path)
            self.lbl_bg_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_bg_preview.setStyleSheet("border: 1px solid gray;") 

    def gerar_com_ia(self):
        licensa = self.config.get("license", "FREE")
        if licensa == "FREE":
            QMessageBox.warning(self, "Recurso Premium", "A geração por IA é um recurso Premium. Atualize para o plano BYOK ou SaaS nas Configurações.")
            return

        tema = self.txt_tema.toPlainText().strip()
        if not tema:
            QMessageBox.warning(self, "Aviso", "Por favor, introduza o tema primeiro!")
            return
        
        api_key_usuario = self.config.get("api_key") if licensa == "BYOK (Sua Chave)" else None
        sucesso_check, msg_check = motor_ia.testar_conectividade(api_key_usuario)
        if not sucesso_check:
            QMessageBox.critical(self, "Bloqueio na IA", f"Conexão recusada:\n\n{msg_check}")
            return
        
        progress = QProgressDialog("Conectando com a IA (Gemini)...", "Cancelar", 0, 100, self)
        progress.setWindowTitle("Gerando Apresentação")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setValue(5)
        progress.show()
        QApplication.processEvents()
        
        api_key_usuario = self.config.get("api_key") if licensa == "BYOK (Sua Chave)" else None
        modelo = self.config.get("model", "gemini-2.5-flash")

        try:
            sucesso, roteiro_ou_erro = motor_ia.gerar_roteiro_slides(tema, api_key_usuario, modelo)
            if progress.wasCanceled(): return
            
            if not sucesso:
                progress.close()
                QMessageBox.critical(self, "Erro Detalhado na IA", f"Falha ao gerar:\n\n{roteiro_ou_erro}")
                return
                
            roteiro = roteiro_ou_erro
            total_slides = len(roteiro)
            progress.setValue(20)
            progress.setLabelText("Estrutura pronta! Buscando imagens...")
            QApplication.processEvents()

            slide_images_dict = {}
            for i, slide_data in enumerate(roteiro):
                if progress.wasCanceled(): return
                palavra_chave = slide_data.get("palavra_chave_imagem", "")
                if palavra_chave:
                    progress.setLabelText(f"Baixando opções para o slide {i + 1} de {total_slides}...")
                    QApplication.processEvents()
                    paths = motor_ia.baixar_imagem_pexels(palavra_chave, i)
                    if paths:
                        slide_images_dict[i] = paths
                
                progress.setValue(20 + int(((i + 1) / total_slides) * 65))

            progress.setValue(90)
            progress.setLabelText("Abrindo painel de escolhas...")
            QApplication.processEvents()
            progress.close()

            selected_images = {}
            if slide_images_dict:
                dialog = ImageSelectionDialog(slide_images_dict, roteiro, self)
                if dialog.exec() == QDialog.Accepted:
                    selected_images = dialog.selected_images
                else:
                    try:
                        for caminhos in slide_images_dict.values():
                            for c in caminhos:
                                if os.path.exists(c): os.remove(c)
                    except: pass
                    return

            prs = Presentation()
            prs.slide_width = 12192000
            prs.slide_height = 6858000

            for i, slide_data in enumerate(roteiro):
                slide = prs.slides.add_slide(prs.slide_layouts[6]) 
                
                barra_lateral = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, int(prs.slide_width * 0.02), prs.slide_height)
                barra_lateral.fill.solid()
                barra_lateral.fill.fore_color.rgb = RGBColor(43, 92, 143) 
                barra_lateral.line.fill.background() 

                title_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.08), int(prs.slide_width * 0.45), int(prs.slide_height * 0.2))
                tf_title = title_box.text_frame
                tf_title.word_wrap = True
                p_title = tf_title.paragraphs[0]
                p_title.text = slide_data.get("titulo", "").upper()
                p_title.font.bold = True
                p_title.font.size = Pt(28)
                p_title.font.color.rgb = RGBColor(30, 60, 90)

                body_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.3), int(prs.slide_width * 0.45), int(prs.slide_height * 0.6))
                tf_body = body_box.text_frame
                tf_body.word_wrap = True

                frases = [f.strip() + "." for f in slide_data.get("texto", "").split(".") if len(f.strip()) > 5]
                for idx, frase in enumerate(frases):
                    p_body = tf_body.paragraphs[0] if idx == 0 else tf_body.add_paragraph()
                    p_body.text = frase
                    p_body.font.size = Pt(16)
                    p_body.level = 0
                    p_body.space_after = Pt(14) 

                if i in selected_images:
                    try:
                        img_left = int(prs.slide_width * 0.54)
                        img_top = int(prs.slide_height * 0.1)
                        img_max_w = int(prs.slide_width * 0.42)
                        img_max_h = int(prs.slide_height * 0.8)

                        pic = slide.shapes.add_picture(selected_images[i], img_left, img_top)
                        ratio = min(img_max_w / pic.width, img_max_h / pic.height)

                        pic.width = int(pic.width * ratio)
                        pic.height = int(pic.height * ratio)
                        pic.left = img_left + int((img_max_w - pic.width) / 2)
                        pic.top = img_top + int((img_max_h - pic.height) / 2)
                    except: pass

            temp_path = os.path.join(base_dir, "apresentacao_ia_temp.pptx")
            prs.save(temp_path)
            
            try:
                for caminhos in slide_images_dict.values():
                    for c in caminhos:
                        if os.path.exists(c): os.remove(c)
            except: pass

            self.pptx_path = temp_path
            self.lbl_pptx.setText("✨ Apresentação carregada e pronta para edição final!")
            
            try:
                if os.name == 'nt': os.startfile(temp_path)
                else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', temp_path])
            except: pass

        except Exception as e:
            progress.close()
            erro_msg = traceback.format_exc()
            log_path = os.path.join(base_dir, "erro_ia_log.txt")
            
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"ERRO CRÍTICO NA IA:\n{erro_msg}")
            
            QMessageBox.critical(self, "Falha Fatal", f"O aplicativo encontrou um erro e gerou um log.\n\nSalvo em:\n{log_path}\n\nErro: {str(e)}")

    def process_and_save(self):
        if not self.pptx_path:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma apresentação primeiro.")
            return

        default_save_path = os.path.join(self.last_dir if self.last_dir else base_dir, "apresentacao_final.pptx")
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Apresentação Final", default_save_path, "PowerPoint (*.pptx)")
        if not save_path: return
        
        self.last_dir = os.path.dirname(save_path)
        self.save_config()

        try:
            prs = Presentation(self.pptx_path)
            txt_rgb = RGBColor(self.text_color.red(), self.text_color.green(), self.text_color.blue()) if self.text_color else None
            fill_rgb = RGBColor(self.fill_color.red(), self.fill_color.green(), self.fill_color.blue()) if self.fill_color else None

            for slide in prs.slides:
                for shape in slide.shapes:
                    if self.chk_scale.isChecked() and shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                        scale = 1.0 - (self.spin_scale.value() / 100.0)
                        nw, nh = int(shape.width * scale), int(shape.height * scale)
                        shape.left += int((shape.width - nw) / 2)
                        shape.top += int((shape.height - nh) / 2)
                        shape.width, shape.height = nw, nh

                    if hasattr(shape, "fill") and fill_rgb:
                        try:
                            if shape.fill.type == MSO_FILL.SOLID: shape.fill.fore_color.rgb = fill_rgb
                        except: pass
                    
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if txt_rgb:
                                    run.font.color.rgb = txt_rgb
                                
                                if self.chk_text_scale.isChecked():
                                    percentual = self.spin_text_scale.value()
                                    fator = 1.0 + (percentual / 100.0)
                                    tamanho = run.font.size if run.font.size is not None else paragraph.font.size
                                    if tamanho is None:
                                        tamanho = Pt(18)
                                    
                                    run.font.size = Pt(int(tamanho.pt * fator))

                if self.bg_path:
                    pic = slide.shapes.add_picture(self.bg_path, 0, 0, prs.slide_width, prs.slide_height)
                    slide.shapes._spTree.remove(pic._element)
                    slide.shapes._spTree.insert(2, pic._element)

            salvo_com_sucesso = False
            while not salvo_com_sucesso:
                try:
                    prs.save(save_path)
                    salvo_com_sucesso = True
                except PermissionError:
                    resp = QMessageBox.warning(
                        self, 
                        "Arquivo Aberto e Bloqueado", 
                        "O arquivo PowerPoint destino já está aberto e travado.\n\n"
                        "Deseja que o aplicativo feche o PowerPoint para continuar a edição?", 
                        QMessageBox.Ok | QMessageBox.Cancel
                    )
                    if resp == QMessageBox.Ok:
                        if os.name == 'nt':
                            os.system("taskkill /f /im POWERPNT.EXE")
                            import time; time.sleep(1.5)
                    else:
                        return 
                        
            # --- AUTO OPEN (Abre automaticamente o PPTX após edição) ---
            self.last_saved_pptx = save_path
            try:
                if os.name == 'nt': os.startfile(save_path)
                else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', save_path])
            except: pass

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar arquivo:\n{str(e)}")

    def export_to_pdf(self):
        # Tenta pegar o último que o usuário editou/salvou. Se não tiver, pega o que ele carregou no passo 1.
        alvo = self.last_saved_pptx if self.last_saved_pptx else self.pptx_path
        
        if not alvo or not os.path.exists(alvo):
            QMessageBox.warning(self, "Aviso", "Por favor, carregue ou salve uma apresentação primeiro.")
            return
            
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", alvo.replace(".pptx", ".pdf"), "PDF (*.pdf)")
        if not pdf_path: return
        
        progress = QProgressDialog("Convertendo para PDF (Aguarde...)", "Cancelar", 0, 0, self)
        progress.setWindowTitle("Gerando PDF")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        try:
            # 32 é o código do formato PDF no PowerPoint
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            deck = powerpoint.Presentations.Open(os.path.abspath(alvo))
            deck.SaveAs(os.path.abspath(pdf_path), 32)
            deck.Close()
            powerpoint.Quit()
            
            progress.close()
            QMessageBox.information(self, "Sucesso", "Apresentação convertida para PDF com sucesso!")
            
            if os.name == 'nt': os.startfile(pdf_path)
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Erro no PDF", f"Falha ao converter.\nVerifique se o PowerPoint não está com janelas de diálogo travando o fundo.\n\nDetalhes:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. GIRA A CHAVE DO RADAR ANTES DE ABRIR O APP
    if checar_e_atualizar():
        # Se achou atualização e o usuário aceitou, o app morre aqui para substituir o arquivo
        os._exit(0)
        
    # 2. Se não tem atualização, abre a janela normalmente
    window = AppPaiVega()
    window.show()
    sys.exit(app.exec())