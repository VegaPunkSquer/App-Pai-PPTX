import sys
import os
import json
import subprocess
from PySide6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QColorDialog, QMessageBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QListWidget, QSlider, QProgressDialog,
    QTabWidget, QComboBox, QLineEdit
)
from PySide6.QtGui import QColor, QPixmap, QFont, QPalette
from PySide6.QtCore import Qt, QSize
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.util import Pt
import motor_ia

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

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

# --- JANELA DE CONFIGURAÇÕES (O CORAÇÃO COMERCIAL) ---
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
        
        self.vbox_ia.addWidget(QLabel("Modelo de Inteligência Artificial:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.0-fast", "gemini-3.0-think"])
        self.combo_model.setCurrentText(self.config.get("model", "gemini-2.5-flash"))
        self.vbox_ia.addWidget(self.combo_model)
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

        # Adiciona as abas
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
        """Bloqueia ou libera campos dependendo do tipo de licença pago."""
        if licensa == "SAAS (Chave Embutida)":
            self.lbl_aviso_saas.show()
            self.container_byok.hide()
            self.tabs.setTabEnabled(1, True)
        elif licensa == "BYOK (Sua Chave)":
            self.lbl_aviso_saas.hide()
            self.container_byok.show()
            self.tabs.setTabEnabled(1, True)
        else: # FREE
            self.tabs.setTabEnabled(1, False) # Trava a aba de IA

    def save_and_close(self):
        self.config["license"] = self.combo_licenca.currentText()
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
        
        self.config = self.load_config()
        self.pptx_path = None
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
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def open_config(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.config = dialog.config
            self.save_config()
            self.apply_theme()
            self.apply_zoom(self.config["zoom"])

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
            palette = app.style().standardPalette() # Tema claro padrão
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

        # Botão de Configurações no Topo
        hbox_top = QHBoxLayout()
        hbox_top.addStretch()
        self.btn_config = QPushButton("⚙️ Configurações / Licença")
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.clicked.connect(self.open_config)
        hbox_top.addWidget(self.btn_config)
        self.main_layout.addLayout(hbox_top)

        # 1. Carregar PPTX
        self.btn_load = QPushButton("1. Carregar Apresentação Pronta (.pptx)")
        self.btn_load.clicked.connect(self.load_pptx)
        self.lbl_pptx = QLabel("Nenhum arquivo selecionado")
        self.lbl_pptx.setStyleSheet("color: gray; font-style: italic;")

        self.main_layout.addWidget(self.btn_load)
        self.main_layout.addWidget(self.lbl_pptx)

        # BLOCO DA IA 
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

        # 2. Cor do Texto
        hbox_text = QHBoxLayout()
        self.btn_text_color = QPushButton("2. Escolher Cor de Todo o Texto (Opcional)")
        self.btn_text_color.clicked.connect(self.choose_text_color)
        self.lbl_text_color_indicator = self.create_color_indicator()
        
        hbox_text.addWidget(self.btn_text_color)
        hbox_text.addWidget(self.lbl_text_color_indicator)
        hbox_text.addStretch()
        self.main_layout.addLayout(hbox_text)

        # 3. Cor de Preenchimento
        hbox_fill = QHBoxLayout()
        self.btn_fill_color = QPushButton("3. Escolher Cor de Fundo dos Cards (Opcional)")
        self.btn_fill_color.clicked.connect(self.choose_fill_color)
        self.lbl_fill_color_indicator = self.create_color_indicator()
        
        hbox_fill.addWidget(self.btn_fill_color)
        hbox_fill.addWidget(self.lbl_fill_color_indicator)
        hbox_fill.addStretch()
        self.main_layout.addLayout(hbox_fill)

        # 4. Plano de Fundo
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

        # 5. Reduzir Imagens
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

        # 6. Salvar
        self.btn_save = QPushButton("6. Processar Apresentação e Salvar")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setStyleSheet("background-color: #333; color: white; font-weight: bold; font-size: 14px;")
        self.btn_save.clicked.connect(self.process_and_save)
        self.main_layout.addWidget(self.btn_save)

        self.setCentralWidget(self.main_container)

    def load_pptx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PPTX", "", "PowerPoint (*.pptx)")
        if path:
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
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.bg_path = path
            pixmap = QPixmap(path)
            self.lbl_bg_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_bg_preview.setStyleSheet("border: 1px solid gray;") 

    def gerar_com_ia(self):
        tema = self.txt_tema.toPlainText().strip()
        if not tema:
            QMessageBox.warning(self, "Aviso", "Por favor, introduza o tema primeiro!")
            return
        
        # --- O CÃO DE GUARDA (Check Salva-Vidas) ---
        sucesso_check, msg_check = motor_ia.testar_conectividade()
        if not sucesso_check:
            QMessageBox.critical(self, "Bloqueio na IA", f"O Google recusou a conexão:\n\n{msg_check}")
            return
        # -------------------------------------------
        
        progress = QProgressDialog("Conectando com a IA (Gemini)...", "Cancelar", 0, 100, self)
        progress.setWindowTitle("Gerando Apresentação")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setValue(5)
        progress.show()
        QApplication.processEvents()
        
        # Injeta a chave dependendo da licença
        licenca = self.config.get("license", "FREE")
        api_key_usuario = self.config.get("api_key") if licenca == "BYOK (Sua Chave)" else None
        modelo = self.config.get("model", "gemini-2.5-flash")

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

        # Renderização do PPTX
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

        temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apresentacao_ia_temp.pptx")
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

    def process_and_save(self):
        if not self.pptx_path:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma apresentação primeiro.")
            return

        default_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apresentacao_final.pptx")
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Apresentação Final", default_save_path, "PowerPoint (*.pptx)")
        if not save_path: return

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
                            if shape.fill.type == MSO_FILL.SOLID:
                                shape.fill.fore_color.rgb = fill_rgb
                        except AttributeError:
                            pass
                    
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                # Troca a cor se foi pedido
                                if txt_rgb:
                                    run.font.color.rgb = txt_rgb
                                
                                # Aumenta a fonte (se foi pedido e se a fonte já tiver um tamanho)
                                if self.chk_text_scale.isChecked() and run.font.size is not None:
                                    percentual = self.spin_text_scale.value()
                                    novo_tamanho_pt = run.font.size.pt * (1.0 + (percentual / 100.0))
                                    run.font.size = Pt(int(novo_tamanho_pt))

                if self.bg_path:
                    pic = slide.shapes.add_picture(self.bg_path, 0, 0, prs.slide_width, prs.slide_height)
                    slide.shapes._spTree.remove(pic._element)
                    slide.shapes._spTree.insert(2, pic._element)

            prs.save(save_path)
            QMessageBox.information(self, "Sucesso", "Filtros aplicados e apresentação salva com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar arquivo:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppPaiVega()
    window.show()
    sys.exit(app.exec())