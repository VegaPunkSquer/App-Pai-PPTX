import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QColorDialog, QMessageBox,
    QCheckBox, QSpinBox
)
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import Qt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE

class AppPaiVega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de PPTX - Versão Refinada")
        self.resize(450, 400)
        
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
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 1. Carregar PPTX
        self.btn_load = QPushButton("1. Carregar Apresentação (.pptx)")
        self.btn_load.clicked.connect(self.load_pptx)
        self.lbl_pptx = QLabel("Nenhum arquivo selecionado")
        self.lbl_pptx.setStyleSheet("color: gray; font-style: italic;")

        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_pptx)

        # 2. Cor do Texto
        hbox_text = QHBoxLayout()
        self.btn_text_color = QPushButton("2. Escolher Cor do Texto (Opcional)")
        self.btn_text_color.clicked.connect(self.choose_text_color)
        self.lbl_text_color_indicator = self.create_color_indicator()
        
        hbox_text.addWidget(self.btn_text_color)
        hbox_text.addWidget(self.lbl_text_color_indicator)
        hbox_text.addStretch()
        layout.addLayout(hbox_text)

        # 3. Cor de Preenchimento
        hbox_fill = QHBoxLayout()
        self.btn_fill_color = QPushButton("3. Escolher Cor de Preenchimento (Opcional)")
        self.btn_fill_color.clicked.connect(self.choose_fill_color)
        self.lbl_fill_color_indicator = self.create_color_indicator()
        
        hbox_fill.addWidget(self.btn_fill_color)
        hbox_fill.addWidget(self.lbl_fill_color_indicator)
        hbox_fill.addStretch()
        layout.addLayout(hbox_fill)

        # 4. Plano de Fundo
        hbox_bg = QHBoxLayout()
        self.btn_bg = QPushButton("4. Escolher Plano de Fundo (Opcional)")
        self.btn_bg.clicked.connect(self.load_bg)
        
        # Preview da imagem
        self.lbl_bg_preview = QLabel("Sem imagem")
        self.lbl_bg_preview.setFixedSize(80, 80)
        self.lbl_bg_preview.setAlignment(Qt.AlignCenter)
        self.lbl_bg_preview.setStyleSheet("border: 1px dashed #aaa; color: gray;")
        
        hbox_bg.addWidget(self.btn_bg)
        hbox_bg.addWidget(self.lbl_bg_preview)
        hbox_bg.addStretch()
        layout.addLayout(hbox_bg)

        # 5. Reduzir Imagens (Gamma)
        hbox_scale = QHBoxLayout()
        self.chk_scale = QCheckBox("5. Reduzir tamanho das imagens em (%):")
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(1, 99)
        self.spin_scale.setValue(20)
        self.spin_scale.setEnabled(False) # Habilita só se marcar a caixinha
        self.chk_scale.toggled.connect(self.spin_scale.setEnabled)
        
        hbox_scale.addWidget(self.chk_scale)
        hbox_scale.addWidget(self.spin_scale)
        hbox_scale.addStretch()
        layout.addLayout(hbox_scale)

        # 6. Salvar (atualizando o número)
        self.btn_save = QPushButton("6. Processar e Salvar")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setStyleSheet("font-weight: bold;")
        self.btn_save.clicked.connect(self.process_and_save)
        layout.addWidget(self.btn_save)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_pptx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PPTX", "", "PowerPoint (*.pptx)")
        if path:
            self.pptx_path = path
            # Mostra só o nome do arquivo para não poluir a tela
            self.lbl_pptx.setText(os.path.basename(path))

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
            self.lbl_text_color_indicator.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #555; border-radius: 12px;"
            )

    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.lbl_fill_color_indicator.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #555; border-radius: 12px;"
            )

    def load_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.bg_path = path
            # Cria o preview escalando a imagem proporcionalmente
            pixmap = QPixmap(path)
            self.lbl_bg_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_bg_preview.setStyleSheet("border: 1px solid #555;") # Tira o tracejado

    def process_and_save(self):
        if not self.pptx_path:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma apresentação primeiro.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_save_path = os.path.join(base_dir, "apresentacao_editada.pptx")
        
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Apresentação", default_save_path, "PowerPoint (*.pptx)")
        
        if not save_path:
            return

        try:
            prs = Presentation(self.pptx_path)

            txt_rgb = RGBColor(self.text_color.red(), self.text_color.green(), self.text_color.blue()) if self.text_color else None
            fill_rgb = RGBColor(self.fill_color.red(), self.fill_color.green(), self.fill_color.blue()) if self.fill_color else None

            for slide in prs.slides:
                # 1. Modificar textos e preenchimentos nas formas existentes
                for shape in slide.shapes:
                    
                    # Lógica ninja para manter a proporção e o centro
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
                        # Aplica o preenchimento apenas se a forma ja possuir um fundo solido (ignora texto puro)
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
            
            # Popup de sucesso com botões personalizados
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Sucesso")
            msg_box.setText("Apresentação gerada com sucesso!")
            msg_box.setIcon(QMessageBox.Information)
            
            btn_ok = msg_box.addButton("OK", QMessageBox.AcceptRole)
            btn_abrir = msg_box.addButton("Abrir Local do Arquivo", QMessageBox.ActionRole)
            
            msg_box.exec()
            
            # Se o usuário clicou em "Abrir Local do Arquivo"
            if msg_box.clickedButton() == btn_abrir:
                # O explorer /select vai abrir a pasta e já deixar o arquivo selecionado
                if os.name == 'nt': # Verifica se é Windows
                    subprocess.Popen(rf'explorer /select,"{os.path.normpath(save_path)}"')
                else: # Fallback para Mac/Linux, caso resolvam usar em outro lugar
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', os.path.dirname(save_path)])

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao processar o arquivo:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppPaiVega()
    window.show()
    sys.exit(app.exec())