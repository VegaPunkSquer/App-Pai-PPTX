import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QColorDialog, QMessageBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QListWidget, QSlider, QProgressDialog
)
from PySide6.QtGui import QColor, QPixmap, QFont
from PySide6.QtCore import Qt, QSize
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Pt # Importação crucial para formatar fontes profissionalmente
import motor_ia

class ImageSelectionDialog(QDialog):
    """Janela flutuante com feedback visual claro para a escolha das imagens."""
    def __init__(self, slide_images_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escolha as Imagens dos Slides")
        self.resize(900, 700)
        self.slide_images_dict = slide_images_dict
        self.selected_images = {} # {indice_slide: caminho_escolhido}

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Lista de Slides na Esquerda
        self.list_slides = QListWidget()
        self.list_slides.setFixedWidth(200)
        self.list_slides.setStyleSheet("font-size: 14px; padding: 5px;")
        for slide_idx in self.slide_images_dict.keys():
            self.list_slides.addItem(f"Slide {slide_idx + 1}")
        
        self.list_slides.currentRowChanged.connect(self.show_options_for_slide)

        # Área de Opções de Imagens na Direita
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container_opcoes = QWidget()
        self.layout_opcoes = QVBoxLayout(self.container_opcoes)
        self.layout_opcoes.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.container_opcoes)

        layout.addWidget(self.list_slides)
        layout.addWidget(self.scroll_area)

        # Botão Concluir no fundo
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        btn_concluir = QPushButton("Concluir Escolhas e Gerar PPTX")
        btn_concluir.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 15px; font-size: 16px; border-radius: 5px;")
        btn_concluir.setCursor(Qt.PointingHandCursor)
        btn_concluir.clicked.connect(self.accept)
        main_layout.addWidget(btn_concluir)

        self.setLayout(main_layout)

        # Seleciona o primeiro item por padrão para já carregar a tela
        if self.list_slides.count() > 0:
            self.list_slides.setCurrentRow(0)

    def show_options_for_slide(self, row_idx):
        if row_idx < 0: return

        # Limpeza segura do layout anterior
        while self.layout_opcoes.count():
            item = self.layout_opcoes.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Pega o índice real do slide baseado na linha clicada
        try:
            slide_idx = list(self.slide_images_dict.keys())[row_idx]
            caminhos = self.slide_images_dict[slide_idx]
        except IndexError:
            return

        lbl_instrucao = QLabel(f"Selecione a imagem para ilustrar o Slide {slide_idx + 1}:")
        lbl_instrucao.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_instrucao.setStyleSheet("padding-bottom: 10px;")
        self.layout_opcoes.addWidget(lbl_instrucao)

        # Desenha as 3 opções com botões grandes
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
            
            # Lógica de Feedback Visual Super Claro
            if self.selected_images.get(slide_idx) == caminho:
                btn_select.setText("✅ IMAGEM SELECIONADA")
                btn_select.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 5px;")
                container_img.setStyleSheet("background-color: #e5f1fb; border: 2px solid #28a745; border-radius: 10px;")
            else:
                btn_select.setText("Escolher esta imagem")
                btn_select.setStyleSheet("background-color: #e0e0e0; color: black; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 5px;")
                container_img.setStyleSheet("border: 1px solid transparent;") # Reset

            # O lambda agora repassa a linha atual para forçar o recarregamento instantâneo
            btn_select.clicked.connect(lambda checked=False, s=slide_idx, c=caminho, r=row_idx: self.select_image(s, c, r))

            vbox.addWidget(lbl_img)
            vbox.addWidget(btn_select)
            self.layout_opcoes.addWidget(container_img)
            
        self.layout_opcoes.addStretch()

    def select_image(self, slide_idx, caminho, row_idx):
        self.selected_images[slide_idx] = caminho
        # Recarrega a visualização da linha atual para piscar o botão verde
        self.show_options_for_slide(row_idx)

class AppPaiVega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de PPTX - Gerador Profissional")
        self.resize(500, 500)
        
        self.pptx_path = None
        self.bg_path = None
        self.text_color = None
        self.fill_color = None

        self.init_ui()

    def create_color_indicator(self):
        """Cria uma 'bolinha' vazia para feedback de cor."""
        lbl = QLabel()
        lbl.setFixedSize(24, 24)
        lbl.setStyleSheet("background-color: transparent; border: 1px solid #ccc; border-radius: 12px;")
        return lbl

    def init_ui(self):
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setSpacing(15)

        # --- Controle de Zoom Global ---
        hbox_zoom = QHBoxLayout()
        lbl_zoom = QLabel("🔎 Zoom da Tela:")
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(50, 250)
        self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(self.apply_zoom)
        self.lbl_zoom_val = QLabel("100%")
        
        hbox_zoom.addWidget(lbl_zoom)
        hbox_zoom.addWidget(self.slider_zoom)
        hbox_zoom.addWidget(self.lbl_zoom_val)
        self.main_layout.addLayout(hbox_zoom)

        # 1. Carregar PPTX
        self.btn_load = QPushButton("1. Carregar Apresentação Pronta (.pptx)")
        self.btn_load.clicked.connect(self.load_pptx)
        self.lbl_pptx = QLabel("Nenhum arquivo selecionado")
        self.lbl_pptx.setStyleSheet("color: gray; font-style: italic;")

        self.main_layout.addWidget(self.btn_load)
        self.main_layout.addWidget(self.lbl_pptx)

        # --- BLOCO DA IA (Expansível) ---
        hbox_ia = QHBoxLayout()
        self.txt_tema = QTextEdit()
        self.txt_tema.setPlaceholderText("Ou digite o tema para a IA criar do zero (ex: A importância da assertividade, foco em liderança)...")
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
        self.btn_bg = QPushButton("4. Fundo do Slide (Opcional, ex: Logo Faculdade)")
        self.btn_bg.clicked.connect(self.load_bg)
        
        self.lbl_bg_preview = QLabel("Sem imagem")
        self.lbl_bg_preview.setFixedSize(80, 80)
        self.lbl_bg_preview.setAlignment(Qt.AlignCenter)
        self.lbl_bg_preview.setStyleSheet("border: 1px dashed #aaa; color: gray;")
        
        hbox_bg.addWidget(self.btn_bg)
        hbox_bg.addWidget(self.lbl_bg_preview)
        hbox_bg.addStretch()
        self.main_layout.addLayout(hbox_bg)

        # 5. Reduzir Imagens
        hbox_scale = QHBoxLayout()
        self.chk_scale = QCheckBox("5. Reduzir tamanho das imagens em (%):")
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

    def apply_zoom(self):
        val = self.slider_zoom.value()
        self.lbl_zoom_val.setText(f"{val}%")
        base_size = 9
        new_size = int(base_size * (val / 100.0))
        font = self.font()
        font.setPointSize(new_size)
        self.setFont(font)
        self.resize(self.sizeHint())

    def load_pptx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PPTX", "", "PowerPoint (*.pptx)")
        if path:
            self.pptx_path = path
            self.lbl_pptx.setText(os.path.basename(path))

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
            self.lbl_text_color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555; border-radius: 12px;")

    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.lbl_fill_color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555; border-radius: 12px;")

    def load_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.bg_path = path
            pixmap = QPixmap(path)
            self.lbl_bg_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_bg_preview.setStyleSheet("border: 1px solid #555;") 

    def gerar_com_ia(self):
        tema = self.txt_tema.toPlainText().strip()
        if not tema:
            QMessageBox.warning(self, "Aviso", "Por favor, introduza o tema primeiro!")
            return
        
        progress = QProgressDialog("Conectando com a IA (Gemini)...", "Cancelar", 0, 100, self)
        progress.setWindowTitle("Gerando Apresentação")
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setValue(5)
        progress.show()
        QApplication.processEvents()
        
        sucesso, roteiro_ou_erro = motor_ia.gerar_roteiro_slides(tema)
        if progress.wasCanceled(): return
        
        if not sucesso:
            progress.close()
            QMessageBox.critical(self, "Erro Detalhado na IA", f"Falha ao gerar:\n\n{roteiro_ou_erro}")
            return
            
        roteiro = roteiro_ou_erro
        total_slides = len(roteiro)
        progress.setValue(20)
        progress.setLabelText("Estrutura pronta! Buscando imagens de alta qualidade...")
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
            
            progresso_atual = 20 + int(((i + 1) / total_slides) * 65)
            progress.setValue(progresso_atual)

        progress.setValue(90)
        progress.setLabelText("Abrindo painel de escolhas...")
        QApplication.processEvents()
        progress.close()

        selected_images = {}
        if slide_images_dict:
            dialog = ImageSelectionDialog(slide_images_dict, self)
            if dialog.exec() == QDialog.Accepted:
                selected_images = dialog.selected_images
            else:
                QMessageBox.warning(self, "Aviso", "Geração cancelada.")
                return

        # =========================================================
        # O NOVO MOTOR DE RENDERIZAÇÃO PROFISSIONAL (Estilo Gamma)
        # =========================================================
        prs = Presentation()
        # Define proporção 16:9 moderna (padrão atual)
        prs.slide_width = 12192000
        prs.slide_height = 6858000

        for i, slide_data in enumerate(roteiro):
            # Usamos um slide totalmente em branco para desenhar o layout perfeito do zero
            slide = prs.slides.add_slide(prs.slide_layouts[6]) 
            
            # 1. Barra Lateral Decorativa (Dá um tom premium de template corporativo)
            barra_lateral = slide.shapes.add_shape(MSO_SHAPE_TYPE.RECTANGLE, 0, 0, int(prs.slide_width * 0.02), prs.slide_height)
            barra_lateral.fill.solid()
            barra_lateral.fill.fore_color.rgb = RGBColor(43, 92, 143) # Azul corporativo
            barra_lateral.line.fill.background() # Remove a borda preta feia

            # 2. Título do Slide (Formatado e posicionado no topo esquerdo)
            title_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.08), int(prs.slide_width * 0.45), int(prs.slide_height * 0.2))
            tf_title = title_box.text_frame
            tf_title.word_wrap = True
            p_title = tf_title.paragraphs[0]
            p_title.text = slide_data.get("titulo", "").upper()
            p_title.font.bold = True
            p_title.font.size = Pt(28)
            p_title.font.color.rgb = RGBColor(30, 60, 90) # Azul escuro para contraste

            # 3. Corpo de Texto em Tópicos (Abaixo do título)
            body_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.3), int(prs.slide_width * 0.45), int(prs.slide_height * 0.6))
            tf_body = body_box.text_frame
            tf_body.word_wrap = True

            # Lógica ninja: Pega o parágrafo gigante da IA e quebra em frases menores (tópicos/bullets)
            texto_bruto = slide_data.get("texto", "")
            frases = [f.strip() + "." for f in texto_bruto.split(".") if len(f.strip()) > 5]

            for idx, frase in enumerate(frases):
                p_body = tf_body.paragraphs[0] if idx == 0 else tf_body.add_paragraph()
                p_body.text = frase
                p_body.font.size = Pt(16)
                p_body.level = 0 # Adiciona a bolinha de bullet point
                p_body.space_after = Pt(14) # Espaçamento respirável entre os tópicos

            # 4. Inserção Inteligente de Imagem (Na Metade Direita do Slide)
            if i in selected_images:
                img_path = selected_images[i]
                try:
                    # Caixa imaginária da metade direita para a imagem não vazar
                    img_left_target = int(prs.slide_width * 0.54)
                    img_top_target = int(prs.slide_height * 0.1)
                    img_max_width = int(prs.slide_width * 0.42)
                    img_max_height = int(prs.slide_height * 0.8)

                    # Insere temporariamente para saber o tamanho original
                    pic = slide.shapes.add_picture(img_path, img_left_target, img_top_target)

                    # Calcula a escala matemática para caber na caixa sem distorcer
                    ratio_w = img_max_width / pic.width
                    ratio_h = img_max_height / pic.height
                    ratio = min(ratio_w, ratio_h)

                    novo_w = int(pic.width * ratio)
                    novo_h = int(pic.height * ratio)

                    # Aplica novo tamanho e centraliza vertical/horizontalmente na sua metade
                    pic.width = novo_w
                    pic.height = novo_h
                    pic.left = img_left_target + int((img_max_width - novo_w) / 2)
                    pic.top = img_top_target + int((img_max_height - novo_h) / 2)

                    # Opcional: Adiciona uma sombra sutil à imagem
                    pic.shadow.inherit = False
                except Exception as e:
                    print(f"Erro ao processar a imagem do slide {i}: {e}")

        # Salva o arquivo espetacular
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(base_dir, "apresentacao_ia_temp.pptx")
        prs.save(temp_path)
        
        self.pptx_path = temp_path
        self.lbl_pptx.setText("✨ Apresentação carregada e pronta para edição final!")
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Trabalho Concluído!")
        msg_box.setText("O layout da sua apresentação foi criado com sucesso.\nO PowerPoint será aberto agora para você revisar o design e o texto.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

        try:
            if os.name == 'nt': os.startfile(temp_path)
            else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', temp_path])
        except Exception:
            pass

    def process_and_save(self):
        if not self.pptx_path:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma apresentação primeiro.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_save_path = os.path.join(base_dir, "apresentacao_final.pptx")
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Apresentação Final", default_save_path, "PowerPoint (*.pptx)")
        if not save_path: return

        try:
            prs = Presentation(self.pptx_path)
            txt_rgb = RGBColor(self.text_color.red(), self.text_color.green(), self.text_color.blue()) if self.text_color else None
            fill_rgb = RGBColor(self.fill_color.red(), self.fill_color.green(), self.fill_color.blue()) if self.fill_color else None

            for slide in prs.slides:
                for shape in slide.shapes:
                    if self.chk_scale.isChecked() and shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                        percent = self.spin_scale.value()
                        scale_factor = 1.0 - (percent / 100.0)
                        
                        new_w = int(shape.width * scale_factor)
                        new_h = int(shape.height * scale_factor)
                        
                        delta_x = (shape.width - new_w) / 2
                        delta_y = (shape.height - new_h) / 2
                        
                        shape.left = int(shape.left + delta_x)
                        shape.top = int(shape.top + delta_y)
                        shape.width = new_w
                        shape.height = new_h

                    if hasattr(shape, "fill") and fill_rgb:
                        try:
                            if shape.fill.type == MSO_FILL.SOLID:
                                shape.fill.fore_color.rgb = fill_rgb
                        except AttributeError:
                            pass
                    
                    if shape.has_text_frame and txt_rgb:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                run.font.color.rgb = txt_rgb

                if self.bg_path:
                    pic = slide.shapes.add_picture(self.bg_path, 0, 0, prs.slide_width, prs.slide_height)
                    slide.shapes._spTree.remove(pic._element)
                    slide.shapes._spTree.insert(2, pic._element)

            prs.save(save_path)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Sucesso Final")
            msg_box.setText("Filtros aplicados e apresentação salva com sucesso!")
            msg_box.setIcon(QMessageBox.Information)
            btn_abrir = msg_box.addButton("Abrir Pasta do Arquivo", QMessageBox.ActionRole)
            msg_box.addButton("OK", QMessageBox.AcceptRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_abrir:
                if os.name == 'nt': 
                    subprocess.Popen(rf'explorer /select,"{os.path.normpath(save_path)}"')
                else: 
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', os.path.dirname(save_path)])

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao processar o arquivo final:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppPaiVega()
    window.show()
    sys.exit(app.exec())