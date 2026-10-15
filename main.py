import sys
import os
import idiomas

# --- RESOLUÇÃO DE CAMINHOS ABSOLUTOS E PASTA DE SISTEMA ---
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    bundle_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bundle_dir = base_dir

# O GOLPE DO APPDATA: Cria uma pasta invisível no sistema para configs e históricos.
# Assim o .exe pode ficar em qualquer lugar sem dar erro de permissão no Windows.
if os.name == 'nt':
    user_data_dir = os.path.join(os.getenv('APPDATA'), "VegaTech", "VegaSlides")
else:
    user_data_dir = os.path.join(os.path.expanduser("~"), ".vegatech", "VegaSlides")

os.makedirs(user_data_dir, exist_ok=True) # Cria a pasta automaticamente e silenciosamente

# Todas as gravações do app agora vão para a pasta segura
CONFIG_FILE = os.path.join(user_data_dir, "config.json")
HISTORICO_JSON_FILE = os.path.join(user_data_dir, "historico_roteiros.json")
PASTA_HISTORICO_PPTX = os.path.join(user_data_dir, "historico_geracoes")
LOG_FILE = os.path.join(user_data_dir, "erro_ia_log.txt")
TEMP_PPTX_FILE = os.path.join(user_data_dir, "apresentacao_ia_temp.pptx")
CACHE_ROTEIRO_FILE = os.path.join(user_data_dir, "ultimo_roteiro_temp.json")
PASTA_CACHE_SESSAO = os.path.join(user_data_dir, "cache_sessao")
os.makedirs(PASTA_CACHE_SESSAO, exist_ok=True)
CACHE_ROTEIRO_FILE = os.path.join(user_data_dir, "ultimo_roteiro_temp.json")

# ==========================================
# 🚚 MIGRAÇÃO AUTOMÁTICA DE ARQUIVOS ANTIGOS
# ==========================================
import shutil

# 1. Migra as Configurações
old_config = os.path.join(base_dir, "config.json")
if os.path.exists(old_config) and not os.path.exists(CONFIG_FILE):
    try: shutil.copy2(old_config, CONFIG_FILE)
    except: pass

# 2. Migra a Lista de Histórico
old_hist_json = os.path.join(base_dir, "historico_roteiros.json")
if os.path.exists(old_hist_json) and not os.path.exists(HISTORICO_JSON_FILE):
    try: shutil.copy2(old_hist_json, HISTORICO_JSON_FILE)
    except: pass
    
# 3. Migra as Apresentações Físicas Salvas
old_hist_folder = os.path.join(base_dir, "historico_geracoes")
if os.path.exists(old_hist_folder) and not os.path.exists(PASTA_HISTORICO_PPTX):
    try: shutil.copytree(old_hist_folder, PASTA_HISTORICO_PPTX)
    except: pass

# ==========================================
# 📋 LEITURA AUTOMÁTICA DO MANIFESTO (VERSÃO E ID)
# ==========================================
MANIFESTO_FILE = os.path.join(base_dir, "vega_manifesto.json")
VERSAO_ATUAL = "v1.0.0"
PRODUTO_ID_MASTER = 1 # Usado para bater na sua API
PLANOS_MANIFESTO = {} # <-- O CÉREBRO DAS PULSEIRAS
NOME_APP_MASTER = "VegaSlides" # <-- VARIÁVEL MODULAR DO NOME

if os.path.exists(MANIFESTO_FILE):
    try:
        import json as _json_temp
        with open(MANIFESTO_FILE, "r", encoding="utf-8") as _f:
            _dados_manifesto = _json_temp.load(_f)
            VERSAO_ATUAL = _dados_manifesto.get("versao_atual", "v1.0.0")
            NOME_APP_MASTER = _dados_manifesto.get("nome", "VegaSlides")
            if "produto_id_master" in _dados_manifesto:
                PRODUTO_ID_MASTER = _dados_manifesto["produto_id_master"]
            if "planos_precos" in _dados_manifesto:
                PLANOS_MANIFESTO = _dados_manifesto["planos_precos"]
    except Exception:
        pass

# ==========================================
# 🚀 O SEGREDO DA VELOCIDADE: SPLASH SCREEN NO TOPO
# ==========================================
# Importamos APENAS o essencial visual para a tela abrir instantaneamente
from PySide6.QtWidgets import QApplication, QSplashScreen, QLabel, QProgressBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class SplashScreenVega(QSplashScreen):
    def __init__(self, caminho_img):
        pixmap = QPixmap(caminho_img).scaled(650, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().__init__(pixmap, Qt.FramelessWindowHint) # Removido o WindowStaysOnTopHint que travava a tela
        
        self.lbl_status = QLabel("Iniciando VegaSlides...", self)
        self.lbl_status.setStyleSheet("color: white; font-weight: bold; font-size: 13px; background-color: rgba(0,0,0,150); padding: 2px; border-radius: 4px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setGeometry(20, pixmap.height() - 70, pixmap.width() - 40, 25)
        
        self.barra = QProgressBar(self)
        self.barra.setGeometry(20, pixmap.height() - 40, pixmap.width() - 40, 20)
        self.barra.setStyleSheet("""
            QProgressBar { border: 1px solid #555; border-radius: 5px; background-color: #222; text-align: center; color: white; font-weight: bold; }
            QProgressBar::chunk { background-color: #0078d7; border-radius: 4px; }
        """)

    def atualizar(self, valor, texto):
        self.barra.setValue(valor)
        self.lbl_status.setText(texto)
        QApplication.processEvents()

# Inicia o núcleo e mostra a imagem ANTES do Python ler o resto do arquivo!
app = None
splash = None
if __name__ == "__main__":
    app = QApplication(sys.argv)
    caminho_splash = os.path.join(bundle_dir, "assets", "SmartSlides.png")
    splash = SplashScreenVega(caminho_splash)
    splash.show()
    splash.atualizar(5, "Iniciando o núcleo do aplicativo...")

# ==========================================
# IMPORTS PESADOS (Carregam enquanto a Splash já está na tela)
# ==========================================
if splash: splash.atualizar(15, "Carregando bibliotecas de interface (PySide6)...")
import time
from PySide6.QtWidgets import (
    QDialog, QFrame, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QColorDialog, QFontDialog, QMessageBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QListWidget, QSlider, QProgressDialog,
    QTabWidget, QComboBox, QLineEdit, QInputDialog, QStackedWidget,
    QSizeGrip, QSizePolicy
)
from PySide6.QtGui import QColor, QFont, QPalette, QIcon, QPainter, QPen
from PySide6.QtCore import QThread, QSize, Signal, QPoint, QRect, QEvent

if splash: splash.atualizar(40, "Carregando motor do PowerPoint (isso leva uns segundos)...")
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.util import Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import MSO_AUTO_SIZE, MSO_VERTICAL_ANCHOR

if splash: splash.atualizar(75, "Conectando motores de Inteligência Artificial...")
import math
import requests
import motor_ia
import json
import subprocess
import traceback
import webbrowser
import ctypes
import comtypes.client
from atualizador import checar_e_atualizar

# =========================================================
# 📐 MOTOR MATEMÁTICO DE FORMAS PARAMÉTRICAS (SMARTART VEGA)
# =========================================================
class MotorFormasVega:
    @staticmethod
    def desenhar_forma(slide, prs, forma_dados, cor_primaria_rgb, cor_secundaria_rgb=None):
        tipo = forma_dados.get("tipo", "ciclo_radial")
        itens = forma_dados.get("itens", [])
        centro = forma_dados.get("centro", "")
        
        if not cor_secundaria_rgb:
            cor_secundaria_rgb = RGBColor(245, 247, 250)
            
        n = max(len(itens), 1)

        # ---------------------------------------------------------
        # CATEGORIA 1: CICLOS E RELAÇÕES
        # ---------------------------------------------------------
        if tipo == "ciclo_radial":
            cx = int(prs.slide_width * 0.50)
            cy = int(prs.slide_height * 0.54)
            raio_orbita = int(prs.slide_height * 0.28)
            r_c = int(prs.slide_height * 0.13)
            
            shape_c = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx - r_c, cy - r_c, r_c * 2, r_c * 2)
            shape_c.fill.solid(); shape_c.fill.fore_color.rgb = cor_primaria_rgb; shape_c.line.fill.background()
            tf_c = shape_c.text_frame; tf_c.word_wrap = True; tf_c.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            p_c = tf_c.paragraphs[0]; p_c.text = centro if centro else "CENTRO"; p_c.font.bold = True; p_c.font.size = Pt(15); p_c.font.color.rgb = RGBColor(255, 255, 255); p_c.alignment = 2

            w_sat, h_sat = int(prs.slide_width * 0.16), int(prs.slide_height * 0.11)
            for idx, item_txt in enumerate(itens):
                angulo = (2 * math.pi / n) * idx - (math.pi / 2)
                sx = int(cx + raio_orbita * math.cos(angulo))
                sy = int(cy + raio_orbita * math.sin(angulo))
                
                conector = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, min(cx, sx), min(cy, sy), max(abs(sx - cx), 2), max(abs(sy - cy), 2))
                conector.fill.solid(); conector.fill.fore_color.rgb = RGBColor(210, 215, 225); conector.line.fill.background()
                slide.shapes._spTree.remove(conector._element); slide.shapes._spTree.insert(2, conector._element)

                shape_s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx - (w_sat // 2), sy - (h_sat // 2), w_sat, h_sat)
                shape_s.fill.solid(); shape_s.fill.fore_color.rgb = cor_secundaria_rgb; shape_s.line.color.rgb = cor_primaria_rgb
                tf_s = shape_s.text_frame; tf_s.word_wrap = True; tf_s.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p_s = tf_s.paragraphs[0]; p_s.text = item_txt; p_s.font.bold = True; p_s.font.size = Pt(12); p_s.font.color.rgb = cor_primaria_rgb; p_s.alignment = 2

        elif tipo == "ciclo_setas":
            cx, cy = int(prs.slide_width * 0.50), int(prs.slide_height * 0.54)
            raio_orbita = int(prs.slide_height * 0.28)
            w_b, h_b = int(prs.slide_width * 0.17), int(prs.slide_height * 0.12)
            for idx, item_txt in enumerate(itens):
                ang = (2 * math.pi / n) * idx - (math.pi / 2)
                bx = int(cx + raio_orbita * math.cos(ang))
                by = int(cy + raio_orbita * math.sin(ang))
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx - (w_b // 2), by - (h_b // 2), w_b, h_b)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = f"{idx + 1}. {item_txt}"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = cor_primaria_rgb; p.alignment = 2

        elif tipo == "diamante_central":
            cx, cy = int(prs.slide_width * 0.50), int(prs.slide_height * 0.54)
            tam_d = int(prs.slide_height * 0.30)
            shape_d = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, cx - (tam_d // 2), cy - (tam_d // 2), tam_d, tam_d)
            shape_d.fill.solid(); shape_d.fill.fore_color.rgb = cor_primaria_rgb; shape_d.line.fill.background()
            tf_d = shape_d.text_frame; tf_d.word_wrap = True; tf_d.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            p_d = tf_d.paragraphs[0]; p_d.text = centro if centro else "FOCO"; p_d.font.bold = True; p_d.font.size = Pt(15); p_d.font.color.rgb = RGBColor(255, 255, 255); p_d.alignment = 2

            w_b, h_b = int(prs.slide_width * 0.22), int(prs.slide_height * 0.13)
            # Afastamento seguro: metade do diamante + metade da caixa + respiro de margem
            offset_x = (tam_d // 2) + (w_b // 2) + int(prs.slide_width * 0.04)
            offset_y = (tam_d // 2) + (h_b // 2) + int(prs.slide_height * 0.05)
            posicoes = [
                (cx, cy - offset_y),  # Topo
                (cx + offset_x, cy),  # Direita
                (cx, cy + offset_y),  # Base
                (cx - offset_x, cy)   # Esquerda
            ]
            for idx in range(min(4, n)):
                bx, by = posicoes[idx]
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx - (w_b // 2), by - (h_b // 2), w_b, h_b)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = itens[idx]; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = cor_primaria_rgb; p.alignment = 2

        elif tipo == "grid_hexagonos":
            larg_h = int(prs.slide_width * 0.17)
            alt_h = int(prs.slide_height * 0.26)
            top_base = int(prs.slide_height * 0.40)
            left_inicial = int((prs.slide_width - (n * larg_h * 0.88)) / 2)
            for idx, item_txt in enumerate(itens):
                hx = int(left_inicial + idx * (larg_h * 0.85))
                hy = top_base if idx % 2 == 0 else top_base - int(alt_h * 0.45)
                shape = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, hx, hy, larg_h, alt_h)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb if idx % 2 == 0 else cor_primaria_rgb
                cor_f = cor_primaria_rgb if idx % 2 == 0 else RGBColor(255, 255, 255)
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = item_txt; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = cor_f; p.alignment = 2

        # ---------------------------------------------------------
        # CATEGORIA 2: PROCESSOS E FLUXOS
        # ---------------------------------------------------------
        elif tipo in ["processo_chevron", "processo_linear"]:
            w_total = int(prs.slide_width * 0.86)
            h_chev = int(prs.slide_height * 0.30)
            top_chev = int(prs.slide_height * 0.38)
            w_chev = int(w_total / n)
            left_base = int(prs.slide_width * 0.07)
            for idx, item_txt in enumerate(itens):
                cx = left_base + (idx * w_chev)
                shape = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, cx, top_chev, w_chev, h_chev)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_primaria_rgb if idx == 0 else cor_secundaria_rgb
                shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = f"ETAPA {idx + 1}\n{item_txt}"; p.font.bold = True; p.font.size = Pt(13)
                p.font.color.rgb = RGBColor(255, 255, 255) if idx == 0 else cor_primaria_rgb; p.alignment = 2

        elif tipo == "timeline_zigzag":
            eixo_y = int(prs.slide_height * 0.52)
            w_total = int(prs.slide_width * 0.86)
            left_base = int(prs.slide_width * 0.07)
            linha = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_base, eixo_y - 2, w_total, 4)
            linha.fill.solid(); linha.fill.fore_color.rgb = cor_primaria_rgb; linha.line.fill.background()
            
            w_card = int(w_total / n) - 15
            h_card = int(prs.slide_height * 0.18)
            for idx, item_txt in enumerate(itens):
                no_x = left_base + int((idx + 0.5) * (w_total / n))
                no = slide.shapes.add_shape(MSO_SHAPE.OVAL, no_x - 10, eixo_y - 10, 20, 20)
                no.fill.solid(); no.fill.fore_color.rgb = cor_primaria_rgb; no.line.fill.background()
                
                card_y = eixo_y - h_card - 25 if idx % 2 == 0 else eixo_y + 25
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, no_x - (w_card // 2), card_y, w_card, h_card)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = f"{idx + 1}. {item_txt}"; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = cor_primaria_rgb; p.alignment = 2

        elif tipo == "funil_conversao":
            cx = int(prs.slide_width * 0.50)
            topo_y = int(prs.slide_height * 0.22)
            base_y = int(prs.slide_height * 0.88)
            h_total = base_y - topo_y
            larg_max = int(prs.slide_width * 0.65)
            larg_min = int(prs.slide_width * 0.20)
            gap = int(prs.slide_height * 0.01)
            for idx, item_txt in enumerate(itens):
                y1 = topo_y + int((idx / float(n)) * h_total)
                y2 = topo_y + int(((idx + 1) / float(n)) * h_total) - (gap if idx < n - 1 else 0)
                h_camada = y2 - y1
                larg_topo = larg_max - int((idx / float(n)) * (larg_max - larg_min))
                
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx - (larg_topo // 2), y1, larg_topo, h_camada)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_primaria_rgb if idx == 0 else cor_secundaria_rgb
                shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = f"{idx + 1}. {item_txt}"; p.font.bold = True; p.font.size = Pt(13)
                p.font.color.rgb = RGBColor(255, 255, 255) if idx == 0 else cor_primaria_rgb; p.alignment = 2

        elif tipo == "escada_crescimento":
            w_total = int(prs.slide_width * 0.86)
            left_base = int(prs.slide_width * 0.07)
            w_degrau = int(w_total / n) - 10
            base_inferior = int(prs.slide_height * 0.86)
            for idx, item_txt in enumerate(itens):
                h_degrau = int(prs.slide_height * (0.20 + (0.45 * ((idx + 1) / float(n)))))
                degrau_x = left_base + (idx * (w_degrau + 10))
                degrau_y = base_inferior - h_degrau
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, degrau_x, degrau_y, w_degrau, h_degrau)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_primaria_rgb if idx == n - 1 else cor_secundaria_rgb
                shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                p = tf.paragraphs[0]; p.text = f"NÍVEL {idx + 1}\n\n{item_txt}"; p.font.bold = True; p.font.size = Pt(12)
                p.font.color.rgb = RGBColor(255, 255, 255) if idx == n - 1 else cor_primaria_rgb; p.alignment = 2

        # ---------------------------------------------------------
        # CATEGORIA 3: HIERARQUIA E PIRÂMIDES
        # ---------------------------------------------------------
        elif tipo == "piramide":
            cx = int(prs.slide_width * 0.50)
            topo_y = int(prs.slide_height * 0.20)
            base_y = int(prs.slide_height * 0.88)
            h_total = base_y - topo_y
            larg_base_max = int(prs.slide_width * 0.65)
            gap = int(prs.slide_height * 0.012)
            for idx, item_txt in enumerate(itens):
                y1 = topo_y + int((idx / float(n)) * h_total)
                y2 = topo_y + int(((idx + 1) / float(n)) * h_total) - (gap if idx < n - 1 else 0)
                h_camada = y2 - y1
                larg_camada = int(((idx + 1) / float(n)) * larg_base_max)
                sh_tipo = MSO_SHAPE.ISOSCELES_TRIANGLE if idx == 0 else MSO_SHAPE.TRAPEZOID
                shape_p = slide.shapes.add_shape(sh_tipo, cx - (larg_camada // 2), y1, larg_camada, h_camada)
                shape_p.fill.solid(); shape_p.fill.fore_color.rgb = cor_primaria_rgb if idx == 0 else cor_secundaria_rgb
                shape_p.line.color.rgb = cor_primaria_rgb
                tf_p = shape_p.text_frame; tf_p.word_wrap = True; tf_p.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p_p = tf_p.paragraphs[0]; p_p.text = f"{idx + 1}. {item_txt}"; p_p.font.bold = True; p_p.font.size = Pt(13)
                p_p.font.color.rgb = RGBColor(255, 255, 255) if idx == 0 else cor_primaria_rgb; p_p.alignment = 2

        elif tipo == "piramide_invertida":
            cx = int(prs.slide_width * 0.50)
            topo_y = int(prs.slide_height * 0.20)
            base_y = int(prs.slide_height * 0.88)
            h_total = base_y - topo_y
            larg_base_max = int(prs.slide_width * 0.65)
            gap = int(prs.slide_height * 0.012)
            for idx, item_txt in enumerate(itens):
                y1 = topo_y + int((idx / float(n)) * h_total)
                y2 = topo_y + int(((idx + 1) / float(n)) * h_total) - (gap if idx < n - 1 else 0)
                h_camada = y2 - y1
                larg_camada = int(((n - idx) / float(n)) * larg_base_max)
                shape_p = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx - (larg_camada // 2), y1, larg_camada, h_camada)
                shape_p.fill.solid(); shape_p.fill.fore_color.rgb = cor_primaria_rgb if idx == n - 1 else cor_secundaria_rgb
                shape_p.line.color.rgb = cor_primaria_rgb
                tf_p = shape_p.text_frame; tf_p.word_wrap = True; tf_p.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p_p = tf_p.paragraphs[0]; p_p.text = f"{idx + 1}. {item_txt}"; p_p.font.bold = True; p_p.font.size = Pt(13)
                p_p.font.color.rgb = RGBColor(255, 255, 255) if idx == n - 1 else cor_primaria_rgb; p_p.alignment = 2

        elif tipo == "organograma":
            cx = int(prs.slide_width * 0.50)
            w_pai, h_pai = int(prs.slide_width * 0.28), int(prs.slide_height * 0.15)
            shape_pai = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx - (w_pai // 2), int(prs.slide_height * 0.22), w_pai, h_pai)
            shape_pai.fill.solid(); shape_pai.fill.fore_color.rgb = cor_primaria_rgb; shape_pai.line.fill.background()
            tf_pai = shape_pai.text_frame; tf_pai.word_wrap = True; tf_pai.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            p_pai = tf_pai.paragraphs[0]; p_pai.text = centro if centro else "LIDERANÇA"; p_pai.font.bold = True; p_pai.font.size = Pt(14); p_pai.font.color.rgb = RGBColor(255, 255, 255); p_pai.alignment = 2

            w_total = int(prs.slide_width * 0.86)
            left_base = int(prs.slide_width * 0.07)
            w_filho = int(w_total / n) - 15
            h_filho = int(prs.slide_height * 0.25)
            filhos_y = int(prs.slide_height * 0.55)
            for idx, item_txt in enumerate(itens):
                fx = left_base + (idx * (w_filho + 15))
                shape_f = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, fx, filhos_y, w_filho, h_filho)
                shape_f.fill.solid(); shape_f.fill.fore_color.rgb = cor_secundaria_rgb; shape_f.line.color.rgb = cor_primaria_rgb
                tf_f = shape_f.text_frame; tf_f.word_wrap = True; tf_f.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p_f = tf_f.paragraphs[0]; p_f.text = item_txt; p_f.font.bold = True; p_f.font.size = Pt(12); p_f.font.color.rgb = cor_primaria_rgb; p_f.alignment = 2

        # ---------------------------------------------------------
        # CATEGORIA 4: MATRIZES E COMPARAÇÕES
        # ---------------------------------------------------------
        elif tipo == "matriz_2x2":
            w_quad = int(prs.slide_width * 0.40)
            h_quad = int(prs.slide_height * 0.28)
            top_base = int(prs.slide_height * 0.26)
            left_base = int(prs.slide_width * 0.08)
            gap = 15
            posicoes = [
                (left_base, top_base),
                (left_base + w_quad + gap, top_base),
                (left_base, top_base + h_quad + gap),
                (left_base + w_quad + gap, top_base + h_quad + gap)
            ]
            rotulos = ["FORÇAS (S)", "OPORTUNIDADES (O)", "FRAQUEZAS (W)", "AMEAÇAS (T)"]
            for idx in range(min(4, n)):
                x_pos, y_pos = posicoes[idx]
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, w_quad, h_quad)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                p_r = tf.paragraphs[0]; p_r.text = rotulos[idx]; p_r.font.bold = True; p_r.font.size = Pt(13); p_r.font.color.rgb = cor_primaria_rgb
                p_t = tf.add_paragraph(); p_t.text = itens[idx]; p_t.font.size = Pt(12); p_t.font.color.rgb = RGBColor(50, 50, 50); p_t.space_before = Pt(6)

        elif tipo == "quatro_cantos":
            cx, cy = int(prs.slide_width * 0.50), int(prs.slide_height * 0.54)
            w_c, h_c = int(prs.slide_width * 0.24), int(prs.slide_height * 0.18)
            centro_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx - (w_c // 2), cy - (h_c // 2), w_c, h_c)
            centro_box.fill.solid(); centro_box.fill.fore_color.rgb = cor_primaria_rgb; centro_box.line.fill.background()
            tf_c = centro_box.text_frame; tf_c.word_wrap = True; tf_c.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            p_c = tf_c.paragraphs[0]; p_c.text = centro if centro else "OBJETIVO"; p_c.font.bold = True; p_c.font.size = Pt(14); p_c.font.color.rgb = RGBColor(255, 255, 255); p_c.alignment = 2

            w_bloco = int(prs.slide_width * 0.28)
            h_bloco = int(prs.slide_height * 0.24)
            coords = [
                (int(prs.slide_width * 0.08), int(prs.slide_height * 0.20)),
                (int(prs.slide_width * 0.64), int(prs.slide_height * 0.20)),
                (int(prs.slide_width * 0.08), int(prs.slide_height * 0.64)),
                (int(prs.slide_width * 0.64), int(prs.slide_height * 0.64))
            ]
            for idx in range(min(4, n)):
                bx, by = coords[idx]
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, w_bloco, h_bloco)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
                p = tf.paragraphs[0]; p.text = itens[idx]; p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = cor_primaria_rgb; p.alignment = 2

        elif tipo == "pilares_comparativos":
            w_total = int(prs.slide_width * 0.86)
            left_base = int(prs.slide_width * 0.07)
            top_pilar = int(prs.slide_height * 0.24)
            h_pilar = int(prs.slide_height * 0.62)
            w_pilar = int(w_total / n) - 15
            for idx, item_txt in enumerate(itens):
                px = left_base + (idx * (w_pilar + 15))
                shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, top_pilar, w_pilar, h_pilar)
                shape.fill.solid(); shape.fill.fore_color.rgb = cor_secundaria_rgb; shape.line.color.rgb = cor_primaria_rgb
                tf = shape.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                p_tit = tf.paragraphs[0]; p_tit.text = f"PILAR {idx + 1}"; p_tit.font.bold = True; p_tit.font.size = Pt(13); p_tit.font.color.rgb = cor_primaria_rgb; p_tit.alignment = 2
                p_txt = tf.add_paragraph(); p_txt.text = item_txt; p_txt.font.size = Pt(12); p_txt.font.color.rgb = RGBColor(60, 60, 60); p_txt.space_before = Pt(10)

# --- JANELA DE ESCOLHA DE IMAGENS ---
class ImageSelectionDialog(QDialog):
    def __init__(self, slide_images_dict, roteiro, parent=None):
        super().__init__(parent)
        self.setWindowTitle(idiomas.tr("img_sel_titulo"))
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
        
        btn_concluir = QPushButton(idiomas.tr("img_sel_btn_concluir"))
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

        lbl_contexto = QLabel(idiomas.tr("img_sel_contexto").format(texto_resumo))
        lbl_contexto.setFont(QFont("Arial", 11, italic=True))
        lbl_contexto.setStyleSheet("padding-bottom: 15px; color: gray;")
        lbl_contexto.setWordWrap(True)
        self.layout_opcoes.addWidget(lbl_contexto)
        
        # --- LÓGICA DO CHECKBOX DE PULAR IMAGEM (ITEM 4) ---
        chk_sem_imagem = QCheckBox(idiomas.tr("img_sel_sem_img"))
        chk_sem_imagem.setStyleSheet("font-weight: bold; color: #a8201a; font-size: 14px; padding: 5px;")
        chk_sem_imagem.setCursor(Qt.PointingHandCursor)
        
        if self.selected_images.get(slide_idx) == "NONE":
            chk_sem_imagem.setChecked(True)
            
        chk_sem_imagem.toggled.connect(lambda checked, s=slide_idx, r=row_idx: self.toggle_no_image(checked, s, r))
        self.layout_opcoes.addWidget(chk_sem_imagem)

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
                btn_select.setText(idiomas.tr("img_sel_selecionada"))
                btn_select.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 5px;")
                container_img.setStyleSheet("background-color: rgba(40, 167, 69, 0.2); border: 2px solid #28a745; border-radius: 10px;")
            else:
                btn_select.setText(idiomas.tr("img_sel_escolher"))
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
        
    def toggle_no_image(self, checked, slide_idx, row_idx):
        if checked:
            self.selected_images[slide_idx] = "NONE"
        else:
            if self.selected_images.get(slide_idx) == "NONE":
                del self.selected_images[slide_idx]
        self.show_options_for_slide(row_idx)
        
# =========================================================
# 🎛️ MODAL 2: REVISOR DE ELEMENTOS (CARDS E FORMAS COM PREVIEW)
# =========================================================
class PreviewSlideCompletoWidget(QFrame):
    """Miniatura 16:9 real do slide completo: fundo branco, barra lateral azul, título e cards/formas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(480, 270)
        self.setStyleSheet("background-color: #ffffff; border: 2px solid #555; border-radius: 6px;")
        self.slide_dados = {}
        self.card_destaque_idx = 0

    def atualizar(self, slide_dados, card_destaque_idx=0):
        self.slide_dados = slide_dados
        self.card_destaque_idx = card_destaque_idx
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # 1. Barra Lateral Azul Vega
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2b5c8f"))
        painter.drawRect(0, 0, int(w * 0.025), h)

        # 2. Título do Slide no Topo
        titulo_txt = self.slide_dados.get("titulo", "").upper()
        if titulo_txt:
            painter.setPen(QColor("#1e3c5a"))
            fonte_tit = QFont("Arial", 9, QFont.Bold)
            painter.setFont(fonte_tit)
            ret_tit = QRect(int(w * 0.06), int(h * 0.06), int(w * 0.88), int(h * 0.14))
            painter.drawText(ret_tit, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, titulo_txt)

        # 3. Desenho de Formas (SmartArt)
        if "smartart" in self.slide_dados:
            forma = self.slide_dados["smartart"]
            tipo = forma.get("tipo", "diamante_central")
            itens = forma.get("itens", [])
            centro = forma.get("centro", "NÚCLEO")
            cx, cy = w // 2, int(h * 0.58)

            if tipo == "diamante_central":
                tam_d = int(h * 0.32)
                poly_d = QPolygonF([
                    QPointF(cx, cy - tam_d // 2),
                    QPointF(cx + tam_d // 2, cy),
                    QPointF(cx, cy + tam_d // 2),
                    QPointF(cx - tam_d // 2, cy)
                ])
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#2b5c8f"))
                painter.drawPolygon(poly_d)

                # Texto Centro
                painter.setPen(QColor("#ffffff"))
                painter.setFont(QFont("Arial", 7, QFont.Bold))
                painter.drawText(QRect(cx - tam_d // 2, cy - tam_d // 2, tam_d, tam_d), Qt.AlignCenter | Qt.TextWordWrap, centro)

                # 4 Cards Satélites
                wb, hb = int(w * 0.22), int(h * 0.16)
                pos = [
                    (cx - wb // 2, cy - tam_d // 2 - hb - 6),
                    (cx + tam_d // 2 + 10, cy - hb // 2),
                    (cx - wb // 2, cy + tam_d // 2 + 6),
                    (cx - tam_d // 2 - wb - 10, cy - hb // 2)
                ]
                for idx_i in range(min(4, len(itens))):
                    bx, by = pos[idx_i]
                    painter.setPen(QPen(QColor("#2b5c8f"), 1))
                    painter.setBrush(QColor("#f5f7fa"))
                    painter.drawRoundedRect(bx, by, wb, hb, 4, 4)
                    painter.setPen(QColor("#2b5c8f"))
                    painter.setFont(QFont("Arial", 6, QFont.Bold))
                    painter.drawText(QRect(bx + 2, by + 2, wb - 4, hb - 4), Qt.AlignCenter | Qt.TextWordWrap, itens[idx_i])
            return

        # 4. Desenho de Cards Lado a Lado
        topicos = self.slide_dados.get("topicos", [])
        num_cards = min(len(topicos), 3)
        if num_cards > 0:
            area_w = int(w * 0.88)
            card_w = (area_w // num_cards) - 8
            card_h = int(h * 0.65)
            left_inicial = int(w * 0.06)
            top_card = int(h * 0.24)

            for idx_c, topico in enumerate(topicos[:num_cards]):
                bx = left_inicial + (idx_c * (card_w + 8))
                eh_foco = (idx_c == self.card_destaque_idx)

                # Fundo do Card
                painter.setPen(QPen(QColor("#0078d7") if eh_foco else QColor("#ccd5e0"), 2 if eh_foco else 1))
                painter.setBrush(QColor("#ffffff") if eh_foco else QColor("#f5f7fa"))
                painter.drawRoundedRect(bx, top_card, card_w, card_h, 6, 6)

                # Título do Card
                icone = topico.get("icone", "📌")
                tit_c = f"{icone} {topico.get('titulo', '')}"
                painter.setPen(QColor("#2b5c8f"))
                painter.setFont(QFont("Arial", 7, QFont.Bold))
                ret_card_tit = QRect(bx + 4, top_card + 6, card_w - 8, int(card_h * 0.26))
                painter.drawText(ret_card_tit, Qt.AlignCenter | Qt.TextWordWrap, tit_c)

                # CÁLCULO DINÂMICO AUTOMÁTICO DO TEXTO PARA OCUPAR O CARD
                texto_c = topico.get("texto", "")
                tam_chars = len(texto_c)
                if tam_chars < 60:
                    base_tam = 9
                elif tam_chars < 120:
                    base_tam = 8
                else:
                    base_tam = 7

                escala = topico.get("escala_texto", 0)
                tam_fonte_final = max(6, int(base_tam + (escala / 15.0)))

                painter.setPen(QColor("#444444"))
                painter.setFont(QFont("Arial", tam_fonte_final))
                ret_card_txt = QRect(bx + 6, top_card + int(card_h * 0.30), card_w - 12, int(card_h * 0.66))
                painter.drawText(ret_card_txt, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, texto_c)


class RevisorElementosDialog(QDialog):
    def __init__(self, roteiro, parent=None):
        super().__init__(parent)
        self.setWindowTitle(idiomas.tr("rev_titulo"))
        self.resize(940, 740)
        self.setMinimumSize(850, 640)
        self.roteiro = roteiro
        self.elementos = self._extrair_elementos()
        self.idx_atual = 0
        self.init_ui()

    def _extrair_elementos(self):
        elementos = []
        for s_idx, slide in enumerate(self.roteiro):
            if "smartart" in slide:
                elementos.append({
                    "tipo": "forma",
                    "slide_idx": s_idx,
                    "sub_idx": 0,
                    "slide_ref": slide,
                    "titulo_slide": slide.get("titulo", "Sem Título"),
                    "dado": slide["smartart"]
                })
            elif slide.get("tipo_layout") == "cards" and "topicos" in slide:
                for t_idx, topico in enumerate(slide["topicos"][:3]):
                    elementos.append({
                        "tipo": "card",
                        "slide_idx": s_idx,
                        "sub_idx": t_idx,
                        "slide_ref": slide,
                        "titulo_slide": slide.get("titulo", "Sem Título"),
                        "dado": topico,
                        "escala_texto": topico.get("escala_texto", 0)
                    })
        return elementos

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(8)

        # BARRA DE MODO DE VISUALIZAÇÃO NO TOPO (FOCO vs LISTA)
        hbox_modo = QHBoxLayout()
        lbl_modo = QLabel(idiomas.tr("rev_modo_label"))
        self.btn_modo_foco = QPushButton(idiomas.tr("rev_modo_foco"))
        self.btn_modo_foco.setCheckable(True)
        self.btn_modo_foco.setChecked(True)
        self.btn_modo_lista = QPushButton(idiomas.tr("rev_modo_lista"))
        self.btn_modo_lista.setCheckable(True)

        self.btn_modo_foco.clicked.connect(lambda: self.alternar_modo(0))
        self.btn_modo_lista.clicked.connect(lambda: self.alternar_modo(1))

        hbox_modo.addWidget(lbl_modo)
        hbox_modo.addWidget(self.btn_modo_foco)
        hbox_modo.addWidget(self.btn_modo_lista)
        hbox_modo.addStretch()
        main_layout.addLayout(hbox_modo)

        # STACK DE MODOS
        self.stack_modos = QStackedWidget()
        self.pagina_foco = QWidget()
        self.pagina_lista = QWidget()
        self.stack_modos.addWidget(self.pagina_foco)
        self.stack_modos.addWidget(self.pagina_lista)
        main_layout.addWidget(self.stack_modos, 1)

        self._construir_pagina_foco()
        self._construir_pagina_lista()

        # Botão de Conclusão Inferior
        btn_concluir = QPushButton(idiomas.tr("rev_btn_concluir"))
        btn_concluir.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 15px; border-radius: 5px;")
        btn_concluir.setCursor(Qt.PointingHandCursor)
        btn_concluir.clicked.connect(self.accept)
        main_layout.addWidget(btn_concluir)

        self.atualizar_elemento_foco()

    def alternar_modo(self, idx):
        self.stack_modos.setCurrentIndex(idx)
        self.btn_modo_foco.setChecked(idx == 0)
        self.btn_modo_lista.setChecked(idx == 1)

    def _construir_pagina_foco(self):
        lay = QVBoxLayout(self.pagina_foco)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Navegador Superior
        hbox_nav = QHBoxLayout()
        self.btn_ant = QPushButton(idiomas.tr("rev_btn_anterior"))
        self.btn_ant.setCursor(Qt.PointingHandCursor)
        self.btn_ant.clicked.connect(self.anterior_foco)
        self.lbl_contador = QLabel(idiomas.tr("rev_elemento_contador").format(1, 1))
        self.lbl_contador.setStyleSheet("font-weight: bold; font-size: 14px; color: #fff;")
        self.btn_prox = QPushButton(idiomas.tr("rev_btn_proximo"))
        self.btn_prox.setCursor(Qt.PointingHandCursor)
        self.btn_prox.clicked.connect(self.proximo_foco)

        hbox_nav.addWidget(self.btn_ant)
        hbox_nav.addStretch()
        hbox_nav.addWidget(self.lbl_contador)
        hbox_nav.addStretch()
        hbox_nav.addWidget(self.btn_prox)
        lay.addLayout(hbox_nav)

        # PREVIEW WYSIWYG 16:9
        hbox_prev = QHBoxLayout()
        self.preview_slide = PreviewSlideCompletoWidget()
        hbox_prev.addStretch()
        hbox_prev.addWidget(self.preview_slide)
        hbox_prev.addStretch()
        lay.addLayout(hbox_prev)

        # ÁREA DE SCROLL COM CONTAINER DEDICADO PARA EDIÇÃO
        self.scroll_foco = QScrollArea()
        self.scroll_foco.setWidgetResizable(True)
        self.scroll_foco.setStyleSheet("border: 1px solid #444; border-radius: 6px; background-color: #222;")
        self.container_foco = QWidget()
        self.lay_foco_dinamico = QVBoxLayout(self.container_foco)
        self.lay_foco_dinamico.setContentsMargins(15, 10, 15, 10)
        self.scroll_foco.setWidget(self.container_foco)
        lay.addWidget(self.scroll_foco, 1)

    def _construir_pagina_lista(self):
        lay = QVBoxLayout(self.pagina_lista)
        lay.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        conteudo = QWidget()
        self.lay_itens_lista = QVBoxLayout(conteudo)
        self.lay_itens_lista.setSpacing(14)

        for el in self.elementos:
            card_item = self._criar_widget_editor(el, modo_lista=True)
            self.lay_itens_lista.addWidget(card_item)

        self.lay_itens_lista.addStretch()
        scroll.setWidget(conteudo)
        lay.addWidget(scroll)

    def _limpar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._limpar_layout(item.layout())

    def _criar_widget_editor(self, el, modo_lista=False):
        box = QFrame()
        box.setStyleSheet("background-color: #262626; border: 1px solid #444; border-radius: 6px; padding: 12px;")
        l = QVBoxLayout(box)
        l.setSpacing(10)

        tipo = el["tipo"]
        tit_slide = el["titulo_slide"]
        slide_dados = el["slide_ref"]
        sub_idx = el["sub_idx"]

        if tipo == "card":
            topico = el["dado"]
            lbl_tit_texto = idiomas.tr("rev_slide_card_tit").format(el['slide_idx'] + 1, tit_slide, sub_idx + 1) if modo_lista else idiomas.tr("rev_slide_card_edit").format(el['slide_idx'] + 1, tit_slide, sub_idx + 1)
            lbl_tit = QLabel(lbl_tit_texto)
            lbl_tit.setStyleSheet("color: #0078d7; font-size: 13px; border: none;")
            l.addWidget(lbl_tit)

            preview_local = None
            if modo_lista:
                hbox_prev_item = QHBoxLayout()
                preview_local = PreviewSlideCompletoWidget()
                preview_local.setFixedSize(384, 216)
                preview_local.atualizar(slide_dados, sub_idx)
                hbox_prev_item.addStretch()
                hbox_prev_item.addWidget(preview_local)
                hbox_prev_item.addStretch()
                l.addLayout(hbox_prev_item)

            l.addWidget(QLabel(idiomas.tr("rev_card_tit_lbl")))
            inp_tit = QLineEdit(topico.get("titulo", ""))
            inp_tit.setStyleSheet("padding: 6px; font-size: 13px;")
            l.addWidget(inp_tit)

            l.addWidget(QLabel(idiomas.tr("rev_card_corpo_lbl")))
            txt_corpo = QTextEdit()
            txt_corpo.setPlainText(topico.get("texto", ""))
            txt_corpo.setMinimumHeight(75)
            txt_corpo.setStyleSheet("padding: 6px; font-size: 13px;")
            l.addWidget(txt_corpo)

            widget_slider = QWidget()
            hbox_tam = QHBoxLayout(widget_slider)
            hbox_tam.setContentsMargins(0, 4, 0, 4)

            lbl_rotulo_tam = QLabel(idiomas.tr("rev_card_tam_lbl"))
            lbl_rotulo_tam.setStyleSheet("font-size: 13px; border: none;")

            sl_tam = QSlider(Qt.Horizontal)
            sl_tam.setRange(-20, 50)
            sl_tam.setValue(topico.get("escala_texto", 0))

            lbl_valor_tam = QLabel(f"{sl_tam.value():+d}%" if sl_tam.value() != 0 else "0%")
            lbl_valor_tam.setStyleSheet("font-weight: bold; font-size: 13px; color: #0078d7; min-width: 45px; border: none;")

            lbl_aviso_limite = QLabel("")
            lbl_aviso_limite.setStyleSheet("color: #ffc107; font-size: 12px; font-weight: bold; border: none;")

            def sync_edicao():
                t = inp_tit.text()
                c = txt_corpo.toPlainText()
                v = sl_tam.value()
                topico["titulo"] = t
                topico["texto"] = c
                topico["escala_texto"] = v

                lbl_valor_tam.setText(f"{v:+d}%" if v != 0 else "0%")
                limite_seguro = 15 if len(c) > 120 else (30 if len(c) > 60 else 50)
                lbl_aviso_limite.setText(idiomas.tr("rev_aviso_transbordo") if v > limite_seguro else "")

                if preview_local:
                    preview_local.atualizar(slide_dados, sub_idx)
                elif hasattr(self, 'preview_slide'):
                    self.preview_slide.atualizar(slide_dados, sub_idx)

            inp_tit.textChanged.connect(sync_edicao)
            txt_corpo.textChanged.connect(sync_edicao)
            sl_tam.valueChanged.connect(sync_edicao)

            hbox_tam.addWidget(lbl_rotulo_tam)
            hbox_tam.addWidget(sl_tam, 1)
            hbox_tam.addWidget(lbl_valor_tam)
            hbox_tam.addWidget(lbl_aviso_limite)
            l.addWidget(widget_slider)

        elif tipo == "forma":
            forma = el["dado"]
            lbl_tit = QLabel(idiomas.tr("rev_slide_forma_tit").format(el['slide_idx'] + 1, tit_slide, forma.get('tipo', '')))
            lbl_tit.setStyleSheet("color: #6f42c1; font-size: 13px; font-weight: bold; border: none;")
            l.addWidget(lbl_tit)

            preview_forma_local = None
            if modo_lista:
                hbox_prev_forma = QHBoxLayout()
                preview_forma_local = PreviewSlideCompletoWidget()
                preview_forma_local.setFixedSize(384, 216)
                preview_forma_local.atualizar(slide_dados, 0)
                hbox_prev_forma.addStretch()
                hbox_prev_forma.addWidget(preview_forma_local)
                hbox_prev_forma.addStretch()
                l.addLayout(hbox_prev_forma)

            if "centro" in forma:
                l.addWidget(QLabel(idiomas.tr("rev_forma_centro_lbl")))
                inp_c = QLineEdit(forma.get("centro", ""))
                inp_c.setStyleSheet("padding: 6px;")
                def sync_c(t):
                    forma["centro"] = t
                    if preview_forma_local:
                        preview_forma_local.atualizar(slide_dados, 0)
                    elif hasattr(self, 'preview_slide'):
                        self.preview_slide.atualizar(slide_dados, 0)
                inp_c.textChanged.connect(sync_c)
                l.addWidget(inp_c)

            itens = forma.get("itens", [])
            l.addWidget(QLabel(idiomas.tr("rev_forma_itens_lbl")))
            for i_pos, item_txt in enumerate(itens):
                inp_i = QLineEdit(item_txt)
                inp_i.setStyleSheet("padding: 5px;")
                def bind_i(t, pos=i_pos):
                    itens[pos] = t
                    if preview_forma_local:
                        preview_forma_local.atualizar(slide_dados, 0)
                    elif hasattr(self, 'preview_slide'):
                        self.preview_slide.atualizar(slide_dados, 0)
                inp_i.textChanged.connect(bind_i)
                l.addWidget(inp_i)

        return box

    def atualizar_elemento_foco(self):
        if not self.elementos:
            self._limpar_layout(self.lay_foco_dinamico)
            self.lay_foco_dinamico.addWidget(QLabel(idiomas.tr("rev_vazio")))
            self.btn_ant.setEnabled(False)
            self.btn_prox.setEnabled(False)
            self.lbl_contador.setText(idiomas.tr("rev_elemento_contador").format(0, 0))
            return

        self.btn_ant.setEnabled(self.idx_atual > 0)
        self.btn_prox.setEnabled(self.idx_atual < len(self.elementos) - 1)
        self.lbl_contador.setText(idiomas.tr("rev_elemento_contador").format(self.idx_atual + 1, len(self.elementos)))

        self._limpar_layout(self.lay_foco_dinamico)

        el = self.elementos[self.idx_atual]
        self.preview_slide.atualizar(el["slide_ref"], el["sub_idx"])

        widget_atual = self._criar_widget_editor(el)
        self.lay_foco_dinamico.addWidget(widget_atual)
        self.lay_foco_dinamico.addStretch()

    def anterior_foco(self):
        if self.idx_atual > 0:
            self.idx_atual -= 1
            self.atualizar_elemento_foco()

    def proximo_foco(self):
        if self.idx_atual < len(self.elementos) - 1:
            self.idx_atual += 1
            self.atualizar_elemento_foco()
            
# =========================================================
# 🧩 PREVIEW VISUAL VETORIAL DA FORMA (SMARTART)
# =========================================================
from PySide6.QtGui import QPolygonF
from PySide6.QtCore import QPointF

class PreviewWidgetForma(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 220)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #444; border-radius: 8px;")
        self.tipo = "ciclo_radial"
        self.qtd_itens = 5

    def atualizar(self, tipo, qtd):
        self.tipo = tipo
        self.qtd_itens = qtd
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cor_primaria = QColor("#0078d7")
        cor_secundaria = QColor("#4a4a4a")
        cor_linha = QColor("#777777")
        w, h = self.width(), self.height()
        n = max(self.qtd_itens, 1)

        # 1. CICLOS E RELAÇÕES
        if self.tipo == "ciclo_radial":
            cx, cy = w // 2, h // 2
            raio = min(w, h) // 3
            for i in range(n):
                ang = (2 * math.pi / n) * i - (math.pi / 2)
                sx = int(cx + raio * math.cos(ang))
                sy = int(cy + raio * math.sin(ang))
                painter.setPen(QPen(cor_linha, 1, Qt.DashLine))
                painter.drawLine(cx, cy, sx, sy)
                painter.setPen(Qt.NoPen); painter.setBrush(cor_secundaria)
                painter.drawEllipse(sx - 13, sy - 13, 26, 26)
            painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria)
            painter.drawEllipse(cx - 20, cy - 20, 40, 40)

        elif self.tipo == "ciclo_setas":
            cx, cy = w // 2, h // 2
            raio = min(w, h) // 3
            painter.setPen(QPen(cor_primaria, 2, Qt.DotLine)); painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - raio, cy - raio, raio * 2, raio * 2)
            for i in range(n):
                ang = (2 * math.pi / n) * i - (math.pi / 2)
                bx = int(cx + raio * math.cos(ang))
                by = int(cy + raio * math.sin(ang))
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i == 0 else cor_secundaria)
                painter.drawRoundedRect(bx - 16, by - 12, 32, 24, 4, 4)

        elif self.tipo == "diamante_central":
            cx, cy = w // 2, h // 2
            poly_d = QPolygonF([QPointF(cx, cy - 26), QPointF(cx + 26, cy), QPointF(cx, cy + 26), QPointF(cx - 26, cy)])
            painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria); painter.drawPolygon(poly_d)
            dist = 45
            posicoes = [(cx, cy - dist), (cx + dist, cy), (cx, cy + dist), (cx - dist, cy)]
            for i in range(min(4, n)):
                px, py = posicoes[i]
                painter.setPen(Qt.NoPen); painter.setBrush(cor_secundaria)
                painter.drawRoundedRect(px - 18, py - 10, 36, 20, 4, 4)

        elif self.tipo == "grid_hexagonos":
            larg_h, alt_h = 44, 38
            cy = h // 2
            left_base = (w - (n * 36)) // 2
            for i in range(n):
                hx = left_base + i * 36
                hy = cy - 10 if i % 2 == 0 else cy + 10
                poly_hex = QPolygonF([
                    QPointF(hx + 10, hy - 18), QPointF(hx + 34, hy - 18),
                    QPointF(hx + 44, hy), QPointF(hx + 34, hy + 18),
                    QPointF(hx + 10, hy + 18), QPointF(hx, hy)
                ])
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i % 2 == 0 else cor_secundaria)
                painter.drawPolygon(poly_hex)

        # 2. PROCESSOS E FLUXOS
        elif self.tipo in ["processo_chevron", "processo_linear"]:
            larg = max((w - 40) // n, 20)
            alt = 46
            cy = (h - alt) // 2
            ponta = 12
            for i in range(n):
                bx = 20 + i * larg
                poly = QPolygonF([
                    QPointF(bx, cy),
                    QPointF(bx + larg - ponta, cy),
                    QPointF(bx + larg, cy + (alt // 2)),
                    QPointF(bx + larg - ponta, cy + alt),
                    QPointF(bx, cy + alt),
                    QPointF(bx + ponta, cy + (alt // 2)) if i > 0 else QPointF(bx, cy + (alt // 2))
                ])
                painter.setPen(Qt.NoPen)
                painter.setBrush(cor_primaria if i == 0 else cor_secundaria)
                painter.drawPolygon(poly)

        elif self.tipo == "timeline_zigzag":
            eixo_y = h // 2
            painter.setPen(QPen(cor_primaria, 2)); painter.drawLine(20, eixo_y, w - 20, eixo_y)
            gap = (w - 40) // n
            for i in range(n):
                cx = 20 + int((i + 0.5) * gap)
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria)
                painter.drawEllipse(cx - 5, eixo_y - 5, 10, 10)
                card_y = eixo_y - 35 if i % 2 == 0 else eixo_y + 12
                painter.setBrush(cor_secundaria)
                painter.drawRoundedRect(cx - 20, card_y, 40, 22, 4, 4)

        elif self.tipo == "funil_conversao":
            cx = w / 2.0
            topo_y, base_y = 20.0, float(h - 25)
            h_total = base_y - topo_y
            larg_max, larg_min = w - 40.0, 50.0
            for i in range(n):
                y1 = topo_y + (i / float(n)) * h_total
                y2 = topo_y + ((i + 1) / float(n)) * h_total - 3.0
                lt = larg_max - (i / float(n)) * (larg_max - larg_min)
                lb = larg_max - ((i + 1) / float(n)) * (larg_max - larg_min)
                poly = QPolygonF([
                    QPointF(cx - (lt / 2.0), y1), QPointF(cx + (lt / 2.0), y1),
                    QPointF(cx + (lb / 2.0), y2), QPointF(cx - (lb / 2.0), y2)
                ])
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i == 0 else cor_secundaria)
                painter.drawPolygon(poly)

        elif self.tipo == "escada_crescimento":
            larg = (w - 40) // n
            for i in range(n):
                alt = int(30 + (h - 70) * ((i + 1) / float(n)))
                bx = 20 + i * larg
                by = h - 20 - alt
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i == n - 1 else cor_secundaria)
                painter.drawRoundedRect(bx, by, larg - 6, alt, 4, 4)

        # 3. HIERARQUIA E PIRÂMIDES
        elif self.tipo == "piramide":
            cx = w / 2.0
            topo_y, base_y = 20.0, float(h - 25)
            h_total = base_y - topo_y
            larg_base = min(w - 40.0, h_total * 1.3)
            for i in range(n):
                y1 = topo_y + (i / float(n)) * h_total
                y2 = topo_y + ((i + 1) / float(n)) * h_total - 3.0
                larg_top = (y1 - topo_y) / h_total * larg_base
                larg_bot = (y2 - topo_y) / h_total * larg_base
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i == 0 else cor_secundaria)
                if i == 0:
                    poly = QPolygonF([QPointF(cx, y1), QPointF(cx - (larg_bot / 2.0), y2), QPointF(cx + (larg_bot / 2.0), y2)])
                else:
                    poly = QPolygonF([QPointF(cx - (larg_top / 2.0), y1), QPointF(cx + (larg_top / 2.0), y1),
                                      QPointF(cx + (larg_bot / 2.0), y2), QPointF(cx - (larg_bot / 2.0), y2)])
                painter.drawPolygon(poly)

        elif self.tipo == "piramide_invertida":
            cx = w / 2.0
            topo_y, base_y = 20.0, float(h - 25)
            h_total = base_y - topo_y
            larg_base = min(w - 40.0, h_total * 1.3)
            for i in range(n):
                y1 = topo_y + (i / float(n)) * h_total
                y2 = topo_y + ((i + 1) / float(n)) * h_total - 3.0
                larg_top = ((n - i) / float(n)) * larg_base
                larg_bot = ((n - (i + 1)) / float(n)) * larg_base
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if i == n - 1 else cor_secundaria)
                if i == n - 1:
                    poly = QPolygonF([QPointF(cx - (larg_top / 2.0), y1), QPointF(cx + (larg_top / 2.0), y1), QPointF(cx, y2)])
                else:
                    poly = QPolygonF([QPointF(cx - (larg_top / 2.0), y1), QPointF(cx + (larg_top / 2.0), y1),
                                      QPointF(cx + (larg_bot / 2.0), y2), QPointF(cx - (larg_bot / 2.0), y2)])
                painter.drawPolygon(poly)

        elif self.tipo == "organograma":
            cx = w // 2
            painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria)
            painter.drawRoundedRect(cx - 30, 20, 60, 25, 4, 4)
            painter.setPen(QPen(cor_primaria, 2)); painter.drawLine(cx, 45, cx, 65)
            larg_f = (w - 40) // n
            for i in range(n):
                fx = 20 + int((i + 0.5) * larg_f)
                painter.drawLine(fx, 65, fx, 85)
                painter.setPen(Qt.NoPen); painter.setBrush(cor_secundaria)
                painter.drawRoundedRect(fx - (larg_f // 2) + 4, 85, larg_f - 8, 45, 4, 4)
                painter.setPen(QPen(cor_primaria, 2))
            painter.drawLine(20 + int(0.5 * larg_f), 65, 20 + int((n - 0.5) * larg_f), 65)

        # 4. MATRIZES E COMPARAÇÕES
        elif self.tipo == "matriz_2x2":
            bw, bh = (w - 60) // 2, (h - 60) // 2
            x1, y1 = 20, 20
            x2, y2 = x1 + bw + 15, y1 + bh + 15
            for idx, (bx, by) in enumerate([(x1, y1), (x2, y1), (x1, y2), (x2, y2)]):
                painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria if idx == 0 else cor_secundaria)
                painter.drawRoundedRect(bx, by, bw, bh, 4, 4)

        elif self.tipo == "quatro_cantos":
            cx, cy = w // 2, h // 2
            painter.setPen(Qt.NoPen); painter.setBrush(cor_primaria)
            painter.drawRoundedRect(cx - 25, cy - 18, 50, 36, 4, 4)
            coords = [(20, 20), (w - 65, 20), (20, h - 55), (w - 65, h - 55)]
            for bx, by in coords:
                painter.setBrush(cor_secundaria)
                painter.drawRoundedRect(bx, by, 45, 35, 4, 4)

        elif self.tipo == "pilares_comparativos":
            larg = (w - 40) // n
            for i in range(n):
                bx = 20 + i * larg
                painter.setPen(Qt.NoPen); painter.setBrush(cor_secundaria)
                painter.drawRoundedRect(bx, 25, larg - 6, h - 50, 4, 4)
                painter.setBrush(cor_primaria)
                painter.drawRoundedRect(bx, 25, larg - 6, 18, 4, 4)


class DialogSeletorForma(QDialog):
    CATALOGO = {
        "Ciclos e Relações": [
            ("🔄 Ciclo Radial Clássico", "ciclo_radial", "Núcleo central com satélites ao redor conectados por linhas.", False),
            ("🔁 Ciclo com Setas Curvas", "ciclo_setas", "Anel de etapas sequenciais indicando ciclo e feedback contínuo.", False),
            ("💎 Diamante Central", "diamante_central", "Losango central em destaque conectado a 4 satélites diagonais.", True),
            ("🛑 Colmeia Hexagonal", "grid_hexagonos", "Arranjo modular de hexágonos regulares encaixados pelas arestas.", False)
        ],
        "Processos e Fluxos": [
            ("⏩ Processo em Chevron", "processo_chevron", "Setas pontudas encaixadas horizontalmente indicando progressão.", False),
            ("〰️ Linha do Tempo Zig-Zag", "timeline_zigzag", "Eixo horizontal com marcos alternando acima e abaixo da linha.", False),
            ("🌪️ Funil de Conversão", "funil_conversao", "Camadas trapezoidais decrescentes até a etapa final.", False),
            ("📶 Escada de Crescimento", "escada_crescimento", "Degraus ascendentes indicando elevação de nível ou maturidade.", False)
        ],
        "Hierarquia e Pirâmides": [
            ("🔺 Pirâmide Hierárquica", "piramide", "Triângulo no topo com trapézios empilhados em base crescente.", False),
            ("🔻 Pirâmide Invertida", "piramide_invertida", "Base superior larga afunilando para o objetivo central na base.", False),
            ("🌳 Organograma / Árvore", "organograma", "Nó raiz de liderança ramificando para equipes subordinadas.", False)
        ],
        "Matrizes e Comparações": [
            ("🔲 Matriz 2x2 (SWOT/FOFA)", "matriz_2x2", "Quatro quadrantes para análise estratégica com eixos cartesianos.", True),
            ("🎯 Quatro Cantos (Four Corners)", "quatro_cantos", "Objetivo central cercado por 4 pilares fundamentais.", True),
            ("🏛️ Pilares Comparativos", "pilares_comparativos", "Colunas verticais estilizadas para comparar itens lado a lado.", False)
        ]
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catálogo de Formas / SmartArt VegaSlides")
        self.setMinimumSize(780, 500)
        self.resize(840, 540)
        self.forma_selecionada = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        lbl_tit = QLabel("<b>Escolha a estrutura visual para inserir no roteiro:</b>")
        lbl_tit.setStyleSheet("font-size: 15px;")
        main_layout.addWidget(lbl_tit)

        hbox_corpo = QHBoxLayout()
        vbox_esq = QVBoxLayout()
        vbox_esq.setSpacing(10)

        # 1. Filtro por Categoria
        vbox_esq.addWidget(QLabel("Categoria de Formas:"))
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(list(self.CATALOGO.keys()))
        self.combo_cat.setStyleSheet("padding: 7px; font-size: 13px; font-weight: bold;")
        self.combo_cat.currentIndexChanged.connect(self.carregar_variantes_categoria)
        vbox_esq.addWidget(self.combo_cat)

        # 2. Modelo Específico
        vbox_esq.addWidget(QLabel("Modelo Específico:"))
        self.combo_modelo = QComboBox()
        self.combo_modelo.setStyleSheet("padding: 7px; font-size: 13px;")
        self.combo_modelo.currentIndexChanged.connect(self.atualizar_preview_ao_vivo)
        vbox_esq.addWidget(self.combo_modelo)

        # 3. Quantidade de Itens
        self.lbl_itens = QLabel("Quantidade de itens:")
        vbox_esq.addWidget(self.lbl_itens)
        self.spin_itens = QSpinBox()
        self.spin_itens.setRange(3, 8)
        self.spin_itens.setValue(5)
        self.spin_itens.setStyleSheet("padding: 6px; font-size: 13px;")
        self.spin_itens.valueChanged.connect(self.atualizar_preview_ao_vivo)
        vbox_esq.addWidget(self.spin_itens)

        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #bbb; font-size: 12px; margin-top: 5px;")
        vbox_esq.addWidget(self.lbl_desc)
        vbox_esq.addStretch()

        hbox_corpo.addLayout(vbox_esq, 1)

        # Painel da Direita (Preview com Canvas Vetorial)
        vbox_dir = QVBoxLayout()
        vbox_dir.addWidget(QLabel("<b>Pré-visualização Gráfica Real:</b>"))
        self.canvas_preview = PreviewWidgetForma()
        vbox_dir.addWidget(self.canvas_preview)
        vbox_dir.addStretch()
        hbox_corpo.addLayout(vbox_dir, 1)

        main_layout.addLayout(hbox_corpo)

        btn_inserir = QPushButton("✔ Inserir Esta Forma no Prompt")
        btn_inserir.setStyleSheet("background-color: #6f42c1; color: white; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 6px;")
        btn_inserir.setCursor(Qt.PointingHandCursor)
        btn_inserir.clicked.connect(self.confirmar)
        main_layout.addWidget(btn_inserir)

        self.carregar_variantes_categoria()

    def carregar_variantes_categoria(self):
        cat_selecionada = self.combo_cat.currentText()
        lista_formas = self.CATALOGO.get(cat_selecionada, [])
        self.combo_modelo.blockSignals(True)
        self.combo_modelo.clear()
        for rotulo, cod, desc, fixo in lista_formas:
            self.combo_modelo.addItem(rotulo, (cod, desc, fixo))
        self.combo_modelo.blockSignals(False)
        self.atualizar_preview_ao_vivo()

    def atualizar_preview_ao_vivo(self):
        dado = self.combo_modelo.currentData()
        if not dado: return
        cod, desc, fixo = dado
        self.lbl_desc.setText(desc)

        if fixo:
            self.spin_itens.blockSignals(True)
            self.spin_itens.setValue(4)
            self.spin_itens.setEnabled(False)
            self.spin_itens.blockSignals(False)
            self.lbl_itens.setText("Quantidade de itens (Fixado em 4):")
        else:
            self.spin_itens.setEnabled(True)
            self.lbl_itens.setText("Quantidade de itens:")

        self.canvas_preview.atualizar(cod, self.spin_itens.value())

    def confirmar(self):
        dado = self.combo_modelo.currentData()
        if not dado: return
        cod, _, _ = dado
        qtd = self.spin_itens.value()
        self.forma_selecionada = f"[FORMA: {cod} | ITENS: {qtd}]"
        self.accept()

class WorkerAuthApp(QThread):
    sucesso = Signal(dict)
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
                self.sucesso.emit(dados) # <-- Manda TUDO que a API cuspir de volta
            else:
                self.erro.emit(f"Erro: {resp.json().get('detail', resp.text)}")
        except Exception as e:
            self.erro.emit(f"Falha de conexão com o Master: {str(e)}")

class LoginCadastroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conta VegaTech")
        self.setMinimumSize(400, 550)
        self.resize(400, 600)
        self.token_recebido = None
        self.init_ui()

    def init_ui(self):
        import idiomas
        
        def tr_safe(chave, padrao):
            res = idiomas.tr(chave) if hasattr(idiomas, 'tr') else chave
            return padrao if res == chave else res

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.setWindowTitle(tr_safe("auth_title", "Conta VegaTech"))
        
        # ABA LOGIN
        self.tab_login = QWidget()
        layout_login = QVBoxLayout(self.tab_login)
        self.inp_login_email = QLineEdit()
        self.inp_login_email.setPlaceholderText(tr_safe("auth_email", "E-mail"))
        self.inp_login_senha = QLineEdit()
        self.inp_login_senha.setPlaceholderText(tr_safe("auth_senha", "Senha"))
        self.inp_login_senha.setEchoMode(QLineEdit.Password)
        aplicar_toggle_senha(self.inp_login_senha)
        
        self.btn_recuperar = QPushButton(tr_safe("auth_link_recuperar", "Esqueci minha senha"))
        self.btn_recuperar.setCursor(Qt.PointingHandCursor)
        self.btn_recuperar.setStyleSheet("background: transparent; border: none; color: #0078d7; text-align: right; text-decoration: underline; font-size: 12px; margin-bottom: 5px;")
        self.btn_recuperar.clicked.connect(self.abrir_recuperar_senha)

        self.btn_logar = QPushButton(tr_safe("auth_btn_entrar", "Entrar"))
        self.btn_logar.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-weight: bold;")
        self.btn_logar.clicked.connect(self.fazer_login)
        
        layout_login.addWidget(QLabel(tr_safe("auth_log_title", "Já tem uma conta? Acesse:")))
        layout_login.addWidget(QLabel(tr_safe("auth_email", "E-mail:")))
        layout_login.addWidget(self.inp_login_email)
        layout_login.addWidget(QLabel(tr_safe("auth_senha", "Senha:")))
        layout_login.addWidget(self.inp_login_senha)
        layout_login.addWidget(self.btn_recuperar)
        layout_login.addWidget(self.btn_logar)
        layout_login.addStretch()
        
        # ABA CADASTRO
        self.tab_cadastro = QWidget()
        layout_cad = QVBoxLayout(self.tab_cadastro)
        
        self.chk_gringo = QCheckBox(tr_safe("cad_chk_gringo", "Sou de fora do Brasil (International User)"))
        self.chk_gringo.setStyleSheet("color: #ffc107; font-weight: bold; margin-bottom: 5px;")
        self.chk_gringo.toggled.connect(self.alternar_modo_gringo)

        self.inp_cad_nome = QLineEdit()
        self.inp_cad_nome.setPlaceholderText(tr_safe("auth_nome", "Nome Completo"))
        self.inp_cad_email = QLineEdit()
        self.inp_cad_email.setPlaceholderText(tr_safe("auth_email", "E-mail"))
        
        # Container de Documento (Brasil) vs País (Gringo)
        self.container_doc = QWidget()
        lay_doc = QVBoxLayout(self.container_doc)
        lay_doc.setContentsMargins(0, 0, 0, 0)
        self.lbl_doc = QLabel("CPF/CNPJ:")
        self.inp_cad_doc = QLineEdit()
        self.inp_cad_doc.setPlaceholderText(tr_safe("auth_doc_ph", "Apenas números"))
        lay_doc.addWidget(self.lbl_doc)
        lay_doc.addWidget(self.inp_cad_doc)

        self.container_pais = QWidget()
        lay_pais = QVBoxLayout(self.container_pais)
        lay_pais.setContentsMargins(0, 0, 0, 0)
        self.lbl_pais = QLabel(tr_safe("auth_lbl_pais", "País (Country):"))
        self.combo_pais = QComboBox()
        self.combo_pais.addItems(["United States", "Canada", "United Kingdom", "Portugal", "Australia", "Other"])
        lay_pais.addWidget(self.lbl_pais)
        lay_pais.addWidget(self.combo_pais)
        self.container_pais.hide()

        self.inp_cad_senha = QLineEdit()
        self.inp_cad_senha.setPlaceholderText(tr_safe("auth_senha_nova", "Crie uma Senha"))
        self.inp_cad_senha.setEchoMode(QLineEdit.Password)
        aplicar_toggle_senha(self.inp_cad_senha)
        
        self.btn_cadastrar = QPushButton(tr_safe("auth_btn_criar", "Criar Conta"))
        self.btn_cadastrar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        self.btn_cadastrar.clicked.connect(self.fazer_cadastro)
        
        layout_cad.addWidget(QLabel(tr_safe("auth_cad_title", "Novo por aqui? Cadastre-se:")))
        layout_cad.addWidget(self.chk_gringo)
        layout_cad.addWidget(QLabel(tr_safe("auth_nome", "Nome Completo:")))
        layout_cad.addWidget(self.inp_cad_nome)
        layout_cad.addWidget(QLabel(tr_safe("auth_email", "E-mail:")))
        layout_cad.addWidget(self.inp_cad_email)
        layout_cad.addWidget(self.container_doc)
        layout_cad.addWidget(self.container_pais)
        layout_cad.addWidget(QLabel(tr_safe("auth_senha", "Senha:")))
        layout_cad.addWidget(self.inp_cad_senha)
        layout_cad.addWidget(self.btn_cadastrar)
        layout_cad.addStretch()

        self.tabs.addTab(self.tab_login, tr_safe("auth_tab_login", "Login"))
        self.tabs.addTab(self.tab_cadastro, tr_safe("auth_tab_cad", "Criar Conta"))
        layout.addWidget(self.tabs)

    def alternar_modo_gringo(self, checked):
        if checked:
            self.container_doc.hide()
            self.container_pais.show()
        else:
            self.container_pais.hide()
            self.container_doc.show()

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
        senha = self.inp_cad_senha.text()
        
        is_gringo = self.chk_gringo.isChecked()
        doc = "".join(filter(str.isdigit, self.inp_cad_doc.text())) if not is_gringo else "EXTRANGEIRO"
        pais = self.combo_pais.currentText() if is_gringo else "BR"
        
        if not nome or not email or not senha or (not is_gringo and not doc):
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos obrigatórios.")
            return
            
        self.btn_cadastrar.setEnabled(False)
        self.btn_cadastrar.setText("Registrando...")
        
        payload = {
            "nome": nome, 
            "email": email, 
            "documento": doc, 
            "senha": senha, 
            "produto": NOME_APP_MASTER,
            "pais": pais
        }
        self.worker = WorkerAuthApp('registrar', payload)
        self.worker.sucesso.connect(self.auth_sucesso)
        self.worker.erro.connect(self.auth_erro)
        self.worker.start()

    def auth_sucesso(self, dados):
        self.token_recebido = dados.get("access_token", "")
        
        # A MÁGICA: Se a API mandar as flags de VIP, já destranca o app na hora!
        if self.parent() and hasattr(self.parent(), 'config'):
            self.parent().config["saas_padrao_ativo"] = dados.get("saas_padrao_ativo", False)
            self.parent().config["saas_elite_ativo"] = dados.get("saas_elite_ativo", False)
            self.parent().config["byok_ativo"] = dados.get("byok_ativo", False)
            
            # Se for VIP, já muda o Dropdown e a memória pro plano certo automaticamente
            if self.parent().config["saas_padrao_ativo"] or self.parent().config["saas_elite_ativo"]:
                self.parent().config["license"] = "SAAS (Chave Embutida)"
            elif self.parent().config["byok_ativo"]:
                self.parent().config["license"] = "BYOK (Sua Chave)"
                
        QMessageBox.information(self, "Sucesso", "Conta conectada com sucesso!")
        self.accept()

    def auth_erro(self, msg):
        self.btn_logar.setEnabled(True)
        self.btn_logar.setText("Entrar")
        self.btn_cadastrar.setEnabled(True)
        self.btn_cadastrar.setText("Criar Conta")
        QMessageBox.critical(self, "Aviso", msg)

    def abrir_recuperar_senha(self):
        email_atual = self.inp_login_email.text().strip()
        dialog = RecuperarSenhaDialog(email_atual, self)
        if dialog.exec() == QDialog.Accepted:
            self.inp_login_senha.clear()
            self.inp_login_senha.setFocus()


class RecuperarSenhaDialog(QDialog):
    def __init__(self, email_inicial="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recuperação de Senha - VegaTech")
        self.setFixedSize(380, 320)
        self.email_inicial = email_inicial
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.page_email = QWidget()
        lay_p1 = QVBoxLayout(self.page_email)
        lay_p1.addWidget(QLabel("<b>Digite seu e-mail cadastrado:</b>"))
        self.inp_rec_email = QLineEdit(self.email_inicial)
        self.inp_rec_email.setPlaceholderText("seuemail@exemplo.com")
        lay_p1.addWidget(self.inp_rec_email)

        self.btn_enviar_cod = QPushButton("Enviar Código de 6 Dígitos")
        self.btn_enviar_cod.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_enviar_cod.setCursor(Qt.PointingHandCursor)
        self.btn_enviar_cod.clicked.connect(self.solicitar_codigo)
        lay_p1.addWidget(self.btn_enviar_cod)
        lay_p1.addStretch()
        self.stack.addWidget(self.page_email)

        self.page_codigo = QWidget()
        lay_p2 = QVBoxLayout(self.page_codigo)
        self.lbl_aviso_envio = QLabel("Código enviado para o seu e-mail!\nDigite abaixo o código de 6 dígitos e sua nova senha:")
        self.lbl_aviso_envio.setWordWrap(True)
        lay_p2.addWidget(self.lbl_aviso_envio)

        self.inp_codigo = QLineEdit()
        self.inp_codigo.setPlaceholderText("Código de 6 dígitos")
        self.inp_codigo.setMaxLength(10)
        lay_p2.addWidget(self.inp_codigo)

        self.inp_nova_senha = QLineEdit()
        self.inp_nova_senha.setPlaceholderText("Nova Senha")
        self.inp_nova_senha.setEchoMode(QLineEdit.Password)
        aplicar_toggle_senha(self.inp_nova_senha)
        lay_p2.addWidget(self.inp_nova_senha)

        self.btn_confirmar = QPushButton("Redefinir Senha")
        self.btn_confirmar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        self.btn_confirmar.setCursor(Qt.PointingHandCursor)
        self.btn_confirmar.clicked.connect(self.confirmar_redefinicao)
        lay_p2.addWidget(self.btn_confirmar)
        lay_p2.addStretch()
        self.stack.addWidget(self.page_codigo)

    def solicitar_codigo(self):
        email = self.inp_rec_email.text().strip().lower()
        if not email:
            QMessageBox.warning(self, "Aviso", "Preencha o e-mail.")
            return

        self.btn_enviar_cod.setEnabled(False)
        self.btn_enviar_cod.setText("Enviando código...")
        QApplication.processEvents()

        try:
            resp = requests.post(
                "https://vegap-masterapp.hf.space/auth/app/recuperar-senha",
                json={"email": email},
                timeout=15
            )
            if resp.status_code in [200, 201]:
                QMessageBox.information(self, "Sucesso", "Código de verificação enviado! Verifique sua caixa de entrada e spam.")
                self.stack.setCurrentIndex(1)
            else:
                msg = resp.json().get("detail", "Falha ao solicitar código.")
                QMessageBox.critical(self, "Erro", msg)
                self.btn_enviar_cod.setEnabled(True)
                self.btn_enviar_cod.setText("Enviar Código de 6 Dígitos")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha de conexão: {str(e)}")
            self.btn_enviar_cod.setEnabled(True)
            self.btn_enviar_cod.setText("Enviar Código de 6 Dígitos")

    def confirmar_redefinicao(self):
        email = self.inp_rec_email.text().strip().lower()
        codigo = self.inp_codigo.text().strip()
        nova_senha = self.inp_nova_senha.text()

        if not codigo or not nova_senha:
            QMessageBox.warning(self, "Aviso", "Preencha o código e a nova senha.")
            return

        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.setText("Atualizando...")
        QApplication.processEvents()

        try:
            resp = requests.post(
                "https://vegap-masterapp.hf.space/auth/app/confirmar-recuperacao",
                json={"email": email, "codigo": codigo, "nova_senha": nova_senha},
                timeout=15
            )
            if resp.status_code in [200, 201]:
                QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso! Você já pode entrar com sua nova senha.")
                self.accept()
            else:
                msg = resp.json().get("detail", "Código inválido ou expirado.")
                QMessageBox.critical(self, "Erro", msg)
                self.btn_confirmar.setEnabled(True)
                self.btn_confirmar.setText("Redefinir Senha")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha de conexão: {str(e)}")
            self.btn_confirmar.setEnabled(True)
            self.btn_confirmar.setText("Redefinir Senha")

# =========================================================
# LOJA UNIVERSAL (VITRINE, CHECKOUT E CUPÕES)
# =========================================================
class WorkerVitrine(QThread):
    sucesso = Signal(dict)
    erro = Signal(str)
    
    def __init__(self, moeda="BRL"):
        super().__init__()
        self.moeda = moeda

    def run(self):
        try:
            # 1. Puxa a lista global da Nave-Mãe e descobre o nome VERDADEIRO pelo ID!
            resp_global = requests.get("https://vegap-masterapp.hf.space/master/vitrine-global", timeout=10)
            if resp_global.status_code != 200:
                self.erro.emit("Erro ao conectar com a Nave-Mãe.")
                return
                
            nome_real = None
            global PRODUTO_ID_MASTER
            for app in resp_global.json():
                if app.get("id") == PRODUTO_ID_MASTER:
                    nome_real = app.get("nome")
                    break
                    
            if not nome_real:
                self.erro.emit("Aplicativo não encontrado pelo ID no servidor.")
                return

            # 2. Usa o nome blindado e atualizado para pedir a vitrine
            import urllib.parse
            nome_url = urllib.parse.quote(nome_real)
            url = f"https://vegap-masterapp.hf.space/master/vitrine/{nome_url}?moeda={self.moeda}"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                self.sucesso.emit(resp.json())
            else:
                self.erro.emit("Erro ao carregar a vitrine.")
        except Exception as e:
            self.erro.emit(str(e))
            if resp.status_code == 200:
                self.sucesso.emit(resp.json())
            else:
                self.erro.emit("Erro ao carregar a vitrine.")
        except Exception as e:
            self.erro.emit(str(e))

class WorkerCheckout(QThread):
    sucesso = Signal(dict)
    erro = Signal(str)

    def __init__(self, token, produto_id, plano_nome, cupom, gateway="asaas"):
        super().__init__()
        self.payload = {
            "token": token,
            "produto_id": produto_id,
            "plano_nome": plano_nome,
            "cupom": cupom,
            "gateway": gateway # Diz pro backend se é pra gerar link do Asaas ou do Stripe
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
    def __init__(self, token_cliente, filtro_loja="SAAS", parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛒 Loja VegaTech - VegaSlides")
        self.setFixedSize(450, 500)
        self.token_cliente = token_cliente
        self.filtro_loja = filtro_loja # "SAAS" ou "BYOK"
        self.produto_id = None
        self.worker_status = None
        self.plano_em_andamento = None
        self.plano_comprado = None # Guarda o recibo final
        self.init_ui()
        self.carregar_vitrine()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        import idiomas
        self.lbl_titulo = QLabel(idiomas.tr("loja_loading"))
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.lbl_titulo)
        
        # CHAVINHA DE MOEDA (BRL / USD)
        hbox_moeda = QHBoxLayout()
        self.lbl_moeda = QLabel("Moeda (Currency):")
        self.combo_moeda = QComboBox()
        self.combo_moeda.addItems(["BRL (R$) - Brasil", "USD ($) - International"])
        self.combo_moeda.setStyleSheet("padding: 4px; font-weight: bold;")
        self.combo_moeda.currentIndexChanged.connect(self.carregar_vitrine)
        hbox_moeda.addWidget(self.lbl_moeda)
        hbox_moeda.addWidget(self.combo_moeda)
        hbox_moeda.addStretch()
        self.layout.addLayout(hbox_moeda)
        
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
        self.inp_cupom.setPlaceholderText(idiomas.tr("loja_cupom"))
        self.inp_cupom.setStyleSheet("font-size: 14px; padding: 10px; border-radius: 5px; border: 1px solid gray;")
        self.layout.addWidget(self.inp_cupom)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #0078d7; font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(self.lbl_status)

    def carregar_vitrine(self):
        import idiomas
        self.lbl_titulo.setText(idiomas.tr("loja_loading"))
        
        while self.container_planos.count():
            item = self.container_planos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        moeda_escolhida = "USD" if self.combo_moeda.currentIndex() == 1 else "BRL"
        
        self.worker_vitrine = WorkerVitrine(moeda=moeda_escolhida)
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
        
        import idiomas
        if not planos:
            self.lbl_titulo.setText(idiomas.tr("loja_vazio"))
            return
            
        self.lbl_titulo.setText(idiomas.tr("loja_escolha"))
        
        # MÁGICA DA ORDENAÇÃO: Força a vitrine a seguir a hierarquia clássica de SaaS
        ordem_ciclos = {"mensal": 1, "trimestral": 2, "semestral": 3, "anual": 4, "unico": 5}
        planos_ordenados = sorted(
            planos.items(), 
            key=lambda x: ordem_ciclos.get(str(x[1].get("ciclo")).lower(), 99)
        )
        
        for nome_plano, detalhes in planos_ordenados:
            # Cruza o plano do DB com o manifesto local para achar a pulseira (1, 2 ou 3)
            config_plano = PLANOS_MANIFESTO.get(nome_plano.upper(), {})
            pulseira = str(config_plano.get("nivel", "1")).upper()
            
            # GOLPE VEGATECH: Filtro Absoluto por Pulseira!
            if self.filtro_loja == "BYOK" and pulseira != "2":
                continue
            if self.filtro_loja == "SAAS" and pulseira == "2":
                continue
            if self.filtro_loja == "ELITE" and pulseira != "3":
                continue
                
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
            simbolo_moeda = "$" if self.combo_moeda.currentIndex() == 1 else "R$"
            lbl_preco = QLabel(f"{simbolo_moeda} {valor:.2f}{txt_ciclo}")
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
            btn_comprar = QPushButton(idiomas.tr("loja_btn_assinar"))
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

        import idiomas
        cupom = self.inp_cupom.text().strip()
        self.lbl_status.setText(idiomas.tr("loja_gerando"))
        self.setEnabled(False)
        
        gateway_escolhido = "stripe" if self.combo_moeda.currentIndex() == 1 else "asaas"
        
        self.plano_em_andamento = plano_nome # Anota qual botão ele clicou
        self.worker_checkout = WorkerCheckout(self.token_cliente, self.produto_id, plano_nome, cupom, gateway_escolhido)
        self.worker_checkout.sucesso.connect(self.processar_checkout)
        self.worker_checkout.erro.connect(self.erro_checkout)
        self.worker_checkout.start()

    def processar_checkout(self, dados):
        if dados.get("gratuito"):
            self.plano_comprado = self.plano_em_andamento # Grava o recibo!
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
        
        # Intercepta token velho ou expirado e força o login na marra
        if "expirada" in erro.lower() or "login" in erro.lower() or "autenticado" in erro.lower():
            QMessageBox.warning(self, "Sessão Expirada", "Sua sessão expirou. Por favor, faça login novamente para continuar.")
            self.token_cliente = None
            
            # Limpa o token estragado lá na configuração do app pai
            if self.parent() and hasattr(self.parent(), 'config'):
                self.parent().config["token_master"] = ""
                if hasattr(self.parent(), 'save_config'):
                    self.parent().save_config()
            
            # Abre a tela de login automaticamente
            dialog_auth = LoginCadastroDialog(self)
            if dialog_auth.exec() == QDialog.Accepted:
                self.token_cliente = dialog_auth.token_recebido
                if self.parent() and hasattr(self.parent(), 'config'):
                    self.parent().config["token_master"] = self.token_cliente
                    if hasattr(self.parent(), 'save_config'):
                        self.parent().save_config()
                # Opcional: Tenta comprar de novo sem o usuário clicar
                if self.plano_em_andamento:
                    self.comprar_plano(self.plano_em_andamento)
        else:
            QMessageBox.critical(self, "Erro", erro)

    def pagamento_confirmado(self):
        self.plano_comprado = self.plano_em_andamento # Grava o recibo!
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
        
        # O TÍTULO EXPLÍCITO DA ABA
        self.lbl_explicacao_licenca = QLabel()
        self.lbl_explicacao_licenca.setWordWrap(True)
        self.lbl_explicacao_licenca.setStyleSheet("margin-bottom: 10px;") 
        vbox_lic.addWidget(self.lbl_explicacao_licenca)
        
        self.lbl_status_lic = QLabel()
        vbox_lic.addWidget(self.lbl_status_lic)
        self.combo_licenca = QComboBox()
        self.combo_licenca.addItem("FREE (Edição Manual)", "FREE (Edição Manual)")
        self.combo_licenca.addItem("BYOK (Sua Chave)", "BYOK (Sua Chave)")
        self.combo_licenca.addItem("SAAS (Chave Embutida)", "SAAS (Chave Embutida)")
        
        lic_atual = self.config.get("license", "FREE")
        if "SAAS" in lic_atual: lic_atual = "SAAS (Chave Embutida)" # Conserta se ficou salvo o lixo da versão anterior
        
        self.combo_licenca.setCurrentText(lic_atual)
        self.combo_licenca.currentTextChanged.connect(self.update_ia_tab_visibility)
        vbox_lic.addWidget(self.combo_licenca)
        vbox_lic.addStretch()
        
        # Aba 2: Inteligência Artificial
        self.tab_ia = QWidget()
        self.vbox_ia = QVBoxLayout(self.tab_ia)
        
        self.lbl_aviso_saas = QLabel("✅ <b>Licença SaaS Ativa</b>\nO motor principal está liberado.")
        self.lbl_aviso_saas.setStyleSheet("color: #28a745; margin-bottom: 5px;")
        self.vbox_ia.addWidget(self.lbl_aviso_saas)

        # --- OPÇÃO 1: GOOGLE GEMINI ---
        self.chk_gemini = QCheckBox("🔵 Usar Google Gemini (Padrão)")
        self.chk_gemini.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.vbox_ia.addWidget(self.chk_gemini)
        
        self.container_gemini = QWidget()
        vbox_gem = QVBoxLayout(self.container_gemini)
        vbox_gem.setContentsMargins(15, 0, 0, 10)
        
        self.wrapper_keys_gemini = QWidget()
        lay_keys_gem = QVBoxLayout(self.wrapper_keys_gemini)
        lay_keys_gem.setContentsMargins(0, 0, 0, 0)
        self.lbl_key_gemini = QLabel("Chave de API Gemini (BYOK):")
        lay_keys_gem.addWidget(self.lbl_key_gemini)
        self.txt_api_key = QLineEdit(self.config.get("api_key", ""))
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        lay_keys_gem.addWidget(self.txt_api_key)
        vbox_gem.addWidget(self.wrapper_keys_gemini)
        
        hbox_mod_gem = QHBoxLayout()
        self.combo_model = QComboBox()
        
        modelo_salvo = self.config.get("model", "")
        if modelo_salvo:
            self.combo_model.addItem(modelo_salvo)
        else:
            self.combo_model.addItem("Busque um modelo...")
            
        self.btn_load_models = QPushButton("🔄 Buscar Modelos")
        self.btn_load_models.clicked.connect(self.load_gemini_models_live)
        self.lbl_mod_gem = QLabel("Modelo:")
        hbox_mod_gem.addWidget(self.lbl_mod_gem)
        hbox_mod_gem.addWidget(self.combo_model, 1)
        hbox_mod_gem.addWidget(self.btn_load_models)
        vbox_gem.addLayout(hbox_mod_gem)
        self.vbox_ia.addWidget(self.container_gemini)

        # --- OPÇÃO 2: CLOUDFLARE WORKERS AI ---
        hbox_cf_title = QHBoxLayout()
        self.chk_cloudflare = QCheckBox("🟠 Usar Cloudflare Workers AI")
        self.chk_cloudflare.setStyleSheet("font-weight: bold; font-size: 13px;")
        hbox_cf_title.addWidget(self.chk_cloudflare)
        
        self.btn_upgrade_elite = QPushButton("⭐ Upgrade ELITE")
        self.btn_upgrade_elite.setStyleSheet("background-color: #ffc107; color: black; font-weight: bold; padding: 2px 8px; border-radius: 4px;")
        self.btn_upgrade_elite.setCursor(Qt.PointingHandCursor)
        self.btn_upgrade_elite.clicked.connect(self.abrir_loja_upgrade)
        self.btn_upgrade_elite.hide()
        
        hbox_cf_title.addWidget(self.btn_upgrade_elite)
        hbox_cf_title.addStretch()
        self.vbox_ia.addLayout(hbox_cf_title)
        
        self.container_cf = QWidget()
        vbox_cf = QVBoxLayout(self.container_cf)
        vbox_cf.setContentsMargins(15, 0, 0, 10)
        
        self.wrapper_keys_cf = QWidget()
        lay_keys_cf = QVBoxLayout(self.wrapper_keys_cf)
        lay_keys_cf.setContentsMargins(0, 0, 0, 0)
        self.lbl_acc_cf = QLabel("Cloudflare Account ID (BYOK):")
        lay_keys_cf.addWidget(self.lbl_acc_cf)
        self.txt_cf_account = QLineEdit(self.config.get("cf_account_id", ""))
        lay_keys_cf.addWidget(self.txt_cf_account)
        self.lbl_tok_cf = QLabel("Cloudflare API Token (BYOK):")
        lay_keys_cf.addWidget(self.lbl_tok_cf)
        self.txt_cf_token = QLineEdit(self.config.get("cf_api_token", ""))
        self.txt_cf_token.setEchoMode(QLineEdit.Password)
        lay_keys_cf.addWidget(self.txt_cf_token)
        vbox_cf.addWidget(self.wrapper_keys_cf)
        
        hbox_mod_cf = QHBoxLayout()
        self.combo_cf_model = QComboBox()
        self.combo_cf_model.addItem(self.config.get("cf_model", "@cf/meta/llama-3-8b-instruct"))
        self.btn_load_cf = QPushButton("🔄 Carregar CF")
        self.btn_load_cf.clicked.connect(self.load_cf_models_live)
        self.lbl_mod_cf = QLabel("Modelo:")
        hbox_mod_cf.addWidget(self.lbl_mod_cf)
        hbox_mod_cf.addWidget(self.combo_cf_model, 1)
        hbox_mod_cf.addWidget(self.btn_load_cf)
        vbox_cf.addLayout(hbox_mod_cf)
        self.vbox_ia.addWidget(self.container_cf)
        self.vbox_ia.addStretch()

        # --- Aba 3: Aparência ---
        self.tab_visual = QWidget()
        vbox_vis = QVBoxLayout(self.tab_visual)
        
        self.lbl_idioma = QLabel()
        vbox_vis.addWidget(self.lbl_idioma)
        self.combo_idioma = QComboBox()
        self.combo_idioma.addItem("Português", "pt")
        self.combo_idioma.addItem("English", "en")
        idx_idioma = self.combo_idioma.findData(self.config.get("idioma", "pt"))
        if idx_idioma >= 0: self.combo_idioma.setCurrentIndex(idx_idioma)
        self.combo_idioma.currentIndexChanged.connect(self.mudar_idioma_ao_vivo)
        vbox_vis.addWidget(self.combo_idioma)

        self.lbl_tema = QLabel()
        self.lbl_tema.setStyleSheet("margin-top: 10px;")
        vbox_vis.addWidget(self.lbl_tema)
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("Escuro", "Escuro")
        self.combo_theme.addItem("Claro", "Claro")
        idx_tema = self.combo_theme.findData(self.config.get("theme", "Escuro"))
        if idx_tema >= 0: self.combo_theme.setCurrentIndex(idx_tema)
        vbox_vis.addWidget(self.combo_theme)
        
        self.lbl_zoom = QLabel()
        self.lbl_zoom.setStyleSheet("margin-top: 10px;")
        vbox_vis.addWidget(self.lbl_zoom)
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(0, 150)
        self.slider_zoom.setValue(self.config.get("zoom", 100))
        self.lbl_zoom_val = QLabel(f"{self.slider_zoom.value()}%")
        self.slider_zoom.valueChanged.connect(self.aplicar_zoom_ao_vivo)
        
        hbox_zoom = QHBoxLayout()
        hbox_zoom.addWidget(self.slider_zoom)
        hbox_zoom.addWidget(self.lbl_zoom_val)
        vbox_vis.addLayout(hbox_zoom)
        vbox_vis.addStretch()

        # --- Aba 4: Editor Padrão ---
        self.tab_editor = QWidget()
        vbox_editor = QVBoxLayout(self.tab_editor)
        
        import idiomas
        self.lbl_editor = QLabel(idiomas.tr("lbl_editor"))
        vbox_editor.addWidget(self.lbl_editor)
        
        self.combo_editor = QComboBox()
        
        # O Detetive: vasculha o PC atrás de editores usando caminhos absolutos
        editores_encontrados = []
        if os.name == 'nt':
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\powerpnt.exe")
                path, _ = winreg.QueryValueEx(key, "")
                if os.path.exists(path): editores_encontrados.append("Microsoft PowerPoint")
            except: pass
            
            for path in [r"C:\Program Files\LibreOffice\program\simpress.exe", r"C:\Program Files (x86)\LibreOffice\program\simpress.exe"]:
                if os.path.exists(path):
                    editores_encontrados.append("LibreOffice Impress")
                    break
                    
        if not editores_encontrados:
            self.lbl_editor.setText(idiomas.tr("editor_detect_none"))
            self.combo_editor.addItem(idiomas.tr("editor_opt_none"))
        else:
            self.lbl_editor.setText(idiomas.tr("editor_detect_found"))
            self.combo_editor.addItem(idiomas.tr("editor_opt_system"))
            self.combo_editor.addItems(editores_encontrados)
            self.combo_editor.addItem(idiomas.tr("editor_opt_none"))

        editor_salvo = self.config.get("app_editor", "")
        idx = self.combo_editor.findText(editor_salvo)
        
        # Se achou o texto exato, maravilha. Se não, tenta deduzir caso o usuário tenha trocado o idioma
        if idx >= 0:
            self.combo_editor.setCurrentIndex(idx)
        else:
            if "Nenhum" in editor_salvo or "None" in editor_salvo:
                self.combo_editor.setCurrentIndex(self.combo_editor.count() - 1)
            elif "Sistema" in editor_salvo or "System" in editor_salvo:
                self.combo_editor.setCurrentIndex(0)
            
        vbox_editor.addWidget(self.combo_editor)
        vbox_editor.addStretch()

        # Aba 5: Minha Conta integrada
        self.tab_perfil = QWidget()
        lay_tab_perfil = QVBoxLayout(self.tab_perfil)
        btn_abrir_perfil_modal = QPushButton(idiomas.tr("cfg_btn_abrir_perfil"))
        btn_abrir_perfil_modal.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold; padding: 10px; font-size: 13px;")
        btn_abrir_perfil_modal.setCursor(Qt.PointingHandCursor)
        btn_abrir_perfil_modal.clicked.connect(lambda: PerfilUsuarioDialog(self).exec())
        lay_tab_perfil.addWidget(btn_abrir_perfil_modal)
        lay_tab_perfil.addStretch()

        self.tabs.addTab(self.tab_licenca, idiomas.tr("cfg_tab_lic"))
        self.tabs.addTab(self.tab_ia, idiomas.tr("cfg_tab_ia"))
        self.tabs.addTab(self.tab_visual, idiomas.tr("cfg_tab_vis"))
        self.tabs.addTab(self.tab_editor, idiomas.tr("cfg_tab_editor"))
        self.tabs.addTab(self.tab_perfil, idiomas.tr("cfg_tab_perfil"))
        layout.addWidget(self.tabs)

        self.btn_salvar = QPushButton()
        self.btn_salvar.setStyleSheet("background-color: #0078d7; color: white; padding: 10px; font-weight: bold;")
        self.btn_salvar.clicked.connect(self.save_and_close)
        layout.addWidget(self.btn_salvar)

        self.chk_gemini.toggled.connect(lambda checked: self.alternar_provedor("gemini", checked))
        self.chk_cloudflare.toggled.connect(lambda checked: self.alternar_provedor("cloudflare", checked))

        prov_atual = self.config.get("provedor", "gemini")
        if prov_atual == "cloudflare":
            self.chk_cloudflare.setChecked(True)
        else:
            self.chk_gemini.setChecked(True)
            
        self.update_ia_tab_visibility(self.combo_licenca.currentText())
        self.atualizar_textos_ui()
        
    def mudar_idioma_ao_vivo(self):
        import idiomas
        idiomas.set_idioma(self.combo_idioma.currentData())
        self.atualizar_textos_ui()
        if self.parent() and hasattr(self.parent(), 'atualizar_textos_ui'):
            self.parent().atualizar_textos_ui()

    def atualizar_textos_ui(self):
        import idiomas
        self.setWindowTitle(idiomas.tr("cfg_title"))
        self.lbl_explicacao_licenca.setText(idiomas.tr("cfg_lbl_lic"))
        self.lbl_status_lic.setText(idiomas.tr("cfg_status_lic"))
        self.lbl_idioma.setText(idiomas.tr("cfg_lbl_idioma"))
        self.lbl_tema.setText(idiomas.tr("cfg_lbl_tema"))
        self.lbl_zoom.setText(idiomas.tr("cfg_lbl_zoom"))
        self.btn_salvar.setText(idiomas.tr("cfg_btn_salvar"))
        self.tabs.setTabText(0, idiomas.tr("cfg_tab_lic"))
        self.tabs.setTabText(1, idiomas.tr("cfg_tab_ia"))
        self.tabs.setTabText(2, idiomas.tr("cfg_tab_vis"))
        self.tabs.setTabText(3, idiomas.tr("cfg_tab_editor"))
        self.tabs.setTabText(4, idiomas.tr("cfg_tab_perfil"))
        if hasattr(self, 'tab_perfil'):
            btn_perfil = self.tab_perfil.findChild(QPushButton)
            if btn_perfil:
                btn_perfil.setText(idiomas.tr("cfg_btn_abrir_perfil"))
        self.btn_load_models.setText(idiomas.tr("cfg_btn_buscar"))
        self.btn_load_cf.setText(idiomas.tr("cfg_btn_load_cf"))
        self.combo_licenca.setItemText(0, idiomas.tr("lic_free"))
        self.combo_licenca.setItemText(1, idiomas.tr("lic_byok"))
        self.combo_licenca.setItemText(2, idiomas.tr("lic_saas"))
        
        self.combo_theme.setItemText(0, idiomas.tr("tema_escuro"))
        self.combo_theme.setItemText(1, idiomas.tr("tema_claro"))

        self.lbl_aviso_saas.setText(idiomas.tr("cfg_aviso_saas"))
        self.chk_gemini.setText(idiomas.tr("cfg_chk_gemini"))
        self.chk_cloudflare.setText(idiomas.tr("cfg_chk_cf"))
        self.btn_upgrade_elite.setText(idiomas.tr("cfg_btn_upgrade"))
        self.lbl_key_gemini.setText(idiomas.tr("cfg_lbl_key_gemini"))
        self.lbl_mod_gem.setText(idiomas.tr("cfg_lbl_modelo"))
        self.lbl_acc_cf.setText(idiomas.tr("cfg_lbl_acc_cf"))
        self.lbl_tok_cf.setText(idiomas.tr("cfg_lbl_tok_cf"))
        self.lbl_mod_cf.setText(idiomas.tr("cfg_lbl_modelo"))
        
        # --- TRADUÇÃO AO VIVO DA ABA EDITOR ---
        if hasattr(self, 'lbl_editor'):
            # Se tem só 1 item, é porque não achou nenhum programa
            if self.combo_editor.count() == 1:
                self.lbl_editor.setText(idiomas.tr("editor_detect_none"))
                self.combo_editor.setItemText(0, idiomas.tr("editor_opt_none"))
            else:
                self.lbl_editor.setText(idiomas.tr("editor_detect_found"))
                self.combo_editor.setItemText(0, idiomas.tr("editor_opt_system"))
                self.combo_editor.setItemText(self.combo_editor.count() - 1, idiomas.tr("editor_opt_none"))

    def aplicar_zoom_ao_vivo(self, v):
        self.lbl_zoom_val.setText(f"{v}%")
        # Puxa o cordão da janela Pai e aplica o zoom na hora que deslizar!
        if self.parent() and hasattr(self.parent(), 'apply_zoom'):
            self.parent().apply_zoom(v)

    def update_ia_tab_visibility(self, licensa):
        if "SAAS" in licensa:
            self.lbl_aviso_saas.show()
            self.wrapper_keys_gemini.hide()
            self.wrapper_keys_cf.hide()
            self.tabs.setTabEnabled(1, True)
            
            if not self.config.get("saas_elite_ativo"):
                self.chk_cloudflare.setEnabled(False)
                self.btn_upgrade_elite.show()
                if hasattr(self, 'chk_cloudflare') and self.chk_cloudflare.isChecked():
                    self.chk_gemini.setChecked(True)
            else:
                self.chk_cloudflare.setEnabled(True)
                self.btn_upgrade_elite.hide()
                
        elif "BYOK" in licensa:
            self.lbl_aviso_saas.hide()
            self.wrapper_keys_gemini.show()
            self.wrapper_keys_cf.show()
            self.tabs.setTabEnabled(1, True)
            if hasattr(self, 'chk_cloudflare'):
                self.chk_cloudflare.setEnabled(True)
                self.btn_upgrade_elite.hide()
        else:
            self.tabs.setTabEnabled(1, False) 

    def abrir_loja_upgrade(self):
        if not self.config.get("token_master"):
            QMessageBox.warning(self, "Aviso", "Autenticação necessária. Salve as configurações primeiro para fazer login.")
            return
            
        # AQUI ESTÁ A CORREÇÃO: Manda abrir a loja passando "ELITE" no filtro
        loja = LojaDialog(self.config.get("token_master"), "ELITE", self)
        if loja.exec() == QDialog.Accepted:
            self.config["token_master"] = loja.token_cliente
            if loja.plano_comprado:
                pulseira = str(PLANOS_MANIFESTO.get(loja.plano_comprado.upper(), {}).get("nivel", "1")).upper()
                if pulseira == "3":
                    self.config["saas_elite_ativo"] = True
                    self.config["saas_padrao_ativo"] = False
                    QMessageBox.information(self, "Bem-vindo ao Elite!", "Poder Multi-IA liberado com sucesso!")
                    self.update_ia_tab_visibility("SAAS (Chave Embutida)")

    def alternar_provedor(self, origem, checked):
        if not checked:
            if origem == "gemini" and not self.chk_cloudflare.isChecked():
                self.chk_gemini.blockSignals(True)
                self.chk_gemini.setChecked(True)
                self.chk_gemini.blockSignals(False)
            elif origem == "cloudflare" and not self.chk_gemini.isChecked():
                self.chk_cloudflare.blockSignals(True)
                self.chk_cloudflare.setChecked(True)
                self.chk_cloudflare.blockSignals(False)
            return

        if origem == "gemini":
            self.chk_cloudflare.blockSignals(True)
            self.chk_cloudflare.setChecked(False)
            self.chk_cloudflare.blockSignals(False)
            self.container_gemini.setEnabled(True)
            self.container_cf.setEnabled(False) 
        else:
            self.chk_gemini.blockSignals(True)
            self.chk_gemini.setChecked(False)
            self.chk_gemini.blockSignals(False)
            self.container_cf.setEnabled(True)
            self.container_gemini.setEnabled(False)

    def load_gemini_models_live(self):
        licensa = self.combo_licenca.currentText()
        chave = self.txt_api_key.text().strip() if licensa == "BYOK (Sua Chave)" else None
        
        if licensa == "BYOK (Sua Chave)" and not chave:
            QMessageBox.warning(self, "Aviso", "Digite a chave BYOK para consultar modelos.")
            return
            
        self.btn_load_models.setText("⏳ Buscando...")
        QApplication.processEvents()
        
        modelos, erro = motor_ia.listar_modelos_gemini(chave)
        self.combo_model.clear()
        if modelos: 
            self.combo_model.addItem("--- Escolha um Modelo ---") # Força a pessoa a decidir
            self.combo_model.addItems(modelos)
            self.combo_model.setCurrentIndex(0) # Trava o botão no texto de aviso
        else: 
            QMessageBox.critical(self, "Erro na API Gemini", f"A API do Google recusou a conexão.\n\nDetalhe do erro:\n{erro}")
        self.btn_load_models.setText("🔄 Buscar Modelos")

    def load_cf_models_live(self):
        acc = self.txt_cf_account.text().strip()
        tok = self.txt_cf_token.text().strip()
        self.btn_load_cf.setText("⏳ Carregando...")
        QApplication.processEvents()
        
        modelos, status = motor_ia.listar_modelos_cloudflare(acc, tok)
        self.combo_cf_model.clear()
        
        if modelos:
            self.combo_cf_model.addItems(modelos)
        else:
            QMessageBox.critical(self, "Erro na API Cloudflare", f"Não foi possível carregar os modelos.\n\nDetalhe:\n{status}")
            
        self.btn_load_cf.setText("🔄 Carregar CF")

    def save_and_close(self):
        licenca_escolhida = self.combo_licenca.currentData()
        licenca_salva = self.config.get("license", "FREE")
        
        # 1. Barreira do BYOK (Com Reversão Automática Anti-Bypass)
        if licenca_escolhida == "BYOK (Sua Chave)":
            if not self.config.get("byok_ativo"): 
                if not self.config.get("token_master"):
                    dialog_auth = LoginCadastroDialog(self)
                    if dialog_auth.exec() == QDialog.Accepted:
                        self.config["token_master"] = dialog_auth.token_recebido
                    else: 
                        self.combo_licenca.setCurrentText(licenca_salva)
                        return
                
                loja = LojaDialog(self.config.get("token_master"), "BYOK", self)
                if loja.exec() == QDialog.Accepted:
                    self.config["token_master"] = loja.token_cliente
                    self.config["byok_ativo"] = True
                else: 
                    self.combo_licenca.setCurrentText(licenca_salva)
                    return

        # 2. Barreira do SAAS (Com Reversão Automática Anti-Bypass)
        elif licenca_escolhida == "SAAS (Chave Embutida)":
            if not self.config.get("saas_padrao_ativo") and not self.config.get("saas_elite_ativo"):
                if not self.config.get("token_master"):
                    dialog_auth = LoginCadastroDialog(self)
                    if dialog_auth.exec() == QDialog.Accepted:
                        self.config["token_master"] = dialog_auth.token_recebido
                    else: 
                        self.combo_licenca.setCurrentText(licenca_salva)
                        return
                
                loja = LojaDialog(self.config.get("token_master"), "SAAS", self)
                if loja.exec() == QDialog.Accepted:
                    self.config["token_master"] = loja.token_cliente
                    if loja.plano_comprado:
                        pulseira = str(PLANOS_MANIFESTO.get(loja.plano_comprado.upper(), {}).get("nivel", "1")).upper()
                        if pulseira == "3":
                            self.config["saas_elite_ativo"] = True
                            self.config["saas_padrao_ativo"] = False
                        else:
                            self.config["saas_padrao_ativo"] = True
                            self.config["saas_elite_ativo"] = False
                else: 
                    self.combo_licenca.setCurrentText(licenca_salva)
                    return

        # Se passou e pagou (ou já tinha pago), salva limpo
        self.config["license"] = licenca_escolhida
        self.config["theme"] = self.combo_theme.currentData()
        self.config["zoom"] = self.slider_zoom.value()
        self.config["idioma"] = self.combo_idioma.currentData()
        
        self.config["provedor"] = "gemini" if self.chk_gemini.isChecked() else "cloudflare"
        self.config["api_key"] = self.txt_api_key.text().strip()
        self.config["model"] = self.combo_model.currentText()
        
        self.config["cf_account_id"] = self.txt_cf_account.text().strip()
        self.config["cf_api_token"] = self.txt_cf_token.text().strip()
        self.config["cf_model"] = self.combo_cf_model.currentText()
        
        self.config["app_editor"] = self.combo_editor.currentText()
        
        # Garante a gravação permanente das chaves de ativação na memória
        self.config["saas_elite_ativo"] = self.config.get("saas_elite_ativo", False)
        self.config["saas_padrao_ativo"] = self.config.get("saas_padrao_ativo", False)
        self.config["byok_ativo"] = self.config.get("byok_ativo", False)

        self.accept()        
class WorkerIAGerador(QThread):
    progresso = Signal(int, str)
    concluido = Signal()

    def __init__(self, tema, config_ia, roteiro_carregado=None):
        super().__init__()
        self.tema = tema
        self.config_ia = config_ia
        self.roteiro_carregado = roteiro_carregado
        self.roteiro = None
        self.slide_images_dict = {}
        self.erro_msg = None

    def run(self):
        try:
            if self.roteiro_carregado:
                self.roteiro = self.roteiro_carregado
            else:
                self.progresso.emit(5, "Conectando ao motor de IA...")
                sucesso, roteiro_ou_erro = motor_ia.gerar_roteiro_slides(self.tema, self.config_ia)
                
                if self.isInterruptionRequested(): return
                
                if not sucesso:
                    self.erro_msg = roteiro_ou_erro
                    return
                    
                self.roteiro = roteiro_ou_erro

            # 2. Baixando as Imagens
            total_slides = len(self.roteiro)
            self.progresso.emit(20, "Estrutura pronta! Buscando imagens...")
            
            for i, slide_data in enumerate(self.roteiro):
                if self.isInterruptionRequested(): return
                palavra_chave = slide_data.get("palavra_chave_imagem", "")
                if palavra_chave:
                    self.progresso.emit(20 + int(((i + 1) / total_slides) * 65), f"Baixando opções para o slide {i + 1} de {total_slides}...")
                    paths = motor_ia.baixar_imagem_pexels(palavra_chave, i)
                    if paths:
                        self.slide_images_dict[i] = paths

            self.progresso.emit(90, "Abrindo painel de escolhas...")
        except Exception as e:
            import traceback
            self.erro_msg = f"Erro no Worker:\n{str(e)}\n\n{traceback.format_exc()}"
        finally:
            self.concluido.emit()
            
# --- JANELA COM ROLAGEM PARA NOVIDADES ---
class NovidadesDialog(QDialog):
    def __init__(self, versao, texto, zoom_atual=100, parent=None):
        super().__init__(parent)
        import idiomas
        self.setWindowTitle(idiomas.tr("nov_janela").format(versao))
        
        # MÁGICA: Tela de Desktop de verdade (Paisagem) e expansível
        nova_largura = int(850 * (zoom_atual / 100.0))
        nova_altura = int(550 * (zoom_atual / 100.0))
        self.resize(nova_largura, nova_altura)
        self.setMinimumSize(600, 400) # Impede o usuário de esmagar demais
        
        # ACESSIBILIDADE: Herda a fonte com zoom do app pai e aplica em tudo dentro da janela
        if parent:
            self.setFont(parent.font())
            
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel(idiomas.tr("nov_header").format(versao))
        lbl_titulo.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl_titulo)
        
        # Cria a área de rolagem
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # <-- DESTRÓI A BARRA HORIZONTAL
        scroll.setStyleSheet("QScrollArea { border: 1px solid gray; border-radius: 5px; }")
        
        conteudo = QWidget()
        lay_conteudo = QVBoxLayout(conteudo)
        
        lbl_texto = QLabel(texto)
        lbl_texto.setWordWrap(True)
        lbl_texto.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        lay_conteudo.addWidget(lbl_texto)
        lay_conteudo.addStretch() # Empurra o texto para o topo
        
        scroll.setWidget(conteudo)
        layout.addWidget(scroll)
        
        btn_ok = QPushButton(idiomas.tr("nov_btn_ok"))
        btn_ok.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

# --- JANELA DO QUADRO DE AVISOS (MEGAFONE) ---
class AvisosDialog(QDialog):
    def __init__(self, avisos, zoom_atual=100, parent=None):
        super().__init__(parent)
        self.setWindowTitle(idiomas.tr("avisos_titulo"))
        
        # Formato widescreen elegante de Launcher de PC
        nova_largura = int(850 * (zoom_atual / 100.0))
        nova_altura = int(550 * (zoom_atual / 100.0))
        self.resize(nova_largura, nova_altura)
        self.setMinimumSize(600, 400)
        
        # ACESSIBILIDADE: Herda a fonte com zoom do app pai e aplica em tudo dentro da janela
        if parent:
            self.setFont(parent.font())
            
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel(f"<b>{idiomas.tr('avisos_header')}</b>")
        lbl_titulo.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl_titulo)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: 1px solid gray; border-radius: 5px; }")
        
        conteudo = QWidget()
        lay_conteudo = QVBoxLayout(conteudo)
        
        if not avisos:
            lbl_vazio = QLabel(idiomas.tr("avisos_vazio"))
            lbl_vazio.setAlignment(Qt.AlignCenter)
            lbl_vazio.setStyleSheet("color: gray; font-style: italic;")
            lay_conteudo.addWidget(lbl_vazio)
        else:
            # Exibe apenas os últimos 10 para não lotar a memória
            for aviso in avisos[:10]:
                card = QFrame()
                tipo = aviso.get("tipo", "info")
                
                # Cores inspiradas no seu painel Admin do Master!
                cor_borda = "#0078d7" if tipo == "info" else "#ffc107" if tipo == "warning" else "#dc3545" if tipo == "erro" else "#28a745"
                
                card.setStyleSheet(f"background-color: #242424; border: 1px solid {cor_borda}; border-left: 5px solid {cor_borda}; border-radius: 6px; margin-bottom: 5px;")
                lay_card = QVBoxLayout(card)
                
                lbl_tit = QLabel(f"<b>{aviso.get('titulo', 'Aviso')}</b>")
                lbl_tit.setStyleSheet("font-size: 14px; border: none; color: white;")
                lbl_tit.setWordWrap(True)
                
                lbl_msg = QLabel(aviso.get('mensagem', ''))
                lbl_msg.setStyleSheet("font-size: 13px; color: #ccc; border: none;")
                lbl_msg.setWordWrap(True)
                
                lay_card.addWidget(lbl_tit)
                lay_card.addWidget(lbl_msg)
                lay_conteudo.addWidget(card)
                
        lay_conteudo.addStretch()
        scroll.setWidget(conteudo)
        layout.addWidget(scroll)
        
        btn_ok = QPushButton(idiomas.tr("avisos_btn_fechar"))
        btn_ok.setStyleSheet("background-color: #555; color: white; font-weight: bold; padding: 10px;")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

# --- O MOTOR DO TUTORIAL (OVERLAY DE DESFOQUE) ---
class TutorialOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.passos = []
        self.passo_atual = 0
        
        # CRUCIAL: Bloqueia cliques para a interface, e permite transparência verdadeira
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.hide()

        self.lbl_titulo = QLabel(self)
        self.lbl_titulo.setStyleSheet("color: #ffc107; font-weight: 900; font-size: 24px; background-color: transparent;")
        
        self.lbl_texto = QLabel(self)
        self.lbl_texto.setStyleSheet("color: white; font-size: 16px; font-weight: 500; background-color: transparent;")
        self.lbl_texto.setWordWrap(True)

        self.btn_next = QPushButton(self)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.avancar)

        self.btn_close = QPushButton(self)
        self.btn_close.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 10px 20px; border-radius: 6px; font-size: 14px; border: 2px solid white;")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.encerrar)

    def iniciar(self, passos):
        import idiomas
        self.btn_close.setText(idiomas.tr("tut_btn_sair"))
        self.passos = passos
        self.passo_atual = 0
        self.setGeometry(0, 0, self.parentWidget().width(), self.parentWidget().height())
        self.show()
        self.raise_() # Joga por cima de TUDO
        self.atualizar_passo()

    def avancar(self):
        self.passo_atual += 1
        if self.passo_atual >= len(self.passos):
            self.encerrar()
        else:
            self.atualizar_passo()

    def encerrar(self):
        self.hide()

    def atualizar_passo(self):
        alvo, titulo, texto = self.passos[self.passo_atual]
        
        import idiomas
        self.lbl_titulo.setText(titulo)
        self.lbl_texto.setText(texto)
        self.btn_next.setText(idiomas.tr("tut_btn_fim") if self.passo_atual == len(self.passos) - 1 else idiomas.tr("tut_btn_prox"))
        self.btn_next.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px 20px; border-radius: 6px; font-size: 14px; border: 2px solid white;" if self.passo_atual == len(self.passos) - 1 else "background-color: #0078d7; color: white; font-weight: bold; padding: 10px 20px; border-radius: 6px; font-size: 14px; border: 2px solid white;")

        if alvo:
            # A MÁGICA 1: Rola a tela até o alvo sozinho!
            scroll = self.parentWidget().scroll_principal
            scroll.ensureWidgetVisible(alvo, 50, 50)
            QApplication.processEvents() # Dá tempo pro PySide6 calcular a barra de rolagem

        self.posicionar_ui()
        self.update() # Força o paintEvent (recorte do buraco)

    def posicionar_ui(self):
        self.lbl_texto.setFixedWidth(400)
        self.lbl_titulo.adjustSize()
        self.lbl_texto.adjustSize()
        self.btn_next.adjustSize()
        self.btn_close.adjustSize()

        alvo = self.passos[self.passo_atual][0]
        
        y_caixa = 80
        if alvo:
            pos_global = alvo.mapToGlobal(QPoint(0, 0))
            pos_alvo = self.mapFromGlobal(pos_global)
            # Se o alvo tá do meio pra cima, jogamos a explicação pra baixo. Vice-versa.
            if pos_alvo.y() < self.height() / 2:
                y_caixa = self.height() - self.lbl_texto.height() - 120
            else:
                y_caixa = 80

        cx = (self.width() - 400) // 2
        self.lbl_titulo.move(cx, y_caixa)
        self.lbl_texto.move(cx, y_caixa + self.lbl_titulo.height() + 15)
        
        y_botoes = self.lbl_texto.y() + self.lbl_texto.height() + 25
        self.btn_close.move(cx, y_botoes)
        self.btn_next.move(cx + self.btn_close.width() + 15, y_botoes)

    def paintEvent(self, event):
        from PySide6.QtGui import QPainterPath
        from PySide6.QtCore import Qt, QPoint, QRect
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        alvo = self.passos[self.passo_atual][0]
        rect = None

        if alvo:
            # Cálculo ABSOLUTO para ignorar o bug do scroll
            pos_global = alvo.mapToGlobal(QPoint(0, 0))
            pos = self.mapFromGlobal(pos_global)
            rect = QRect(pos, alvo.size())
            rect.adjust(-10, -10, 10, 10) # Margem de respiro pro widget brilhar

        # A MÁGICA DEFINITIVA: QPainterPath com regra OddEven
        path = QPainterPath()
        path.addRect(self.rect()) # Adiciona a tela toda
        if rect:
            path.addRoundedRect(rect, 8, 8) # Adiciona o buraco dentro

        # Preenche tudo com preto 85%, exceto o buraco!
        painter.fillPath(path, QColor(0, 0, 0, 220))

        # Desenha a borda neon por cima
        if rect:
            pen = QPen(QColor("#ffc107"), 3, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRoundedRect(rect, 8, 8)

# --- APLICATIVO PRINCIPAL ---

# --- ASSISTENTE DE CRIAÇÃO PASSO A PASSO ---
class AssistenteIADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        import idiomas
        self.setWindowTitle(idiomas.tr("ast_title"))
        self.setFixedSize(500, 400)
        self.prompt_final = ""
        self.init_ui()

    def init_ui(self):
        import idiomas
        layout_principal = QVBoxLayout(self)
        
        self.stack = QStackedWidget()
        layout_principal.addWidget(self.stack)

        # -- PÁGINA 0: Boas Vindas --
        page0 = QWidget()
        vbox0 = QVBoxLayout(page0)
        lbl_tit0 = QLabel(f"<h2>{idiomas.tr('ast_p0_tit')}</h2>")
        lbl_tit0.setAlignment(Qt.AlignCenter)
        lbl_msg0 = QLabel(idiomas.tr("ast_p0_msg"))
        lbl_msg0.setWordWrap(True)
        lbl_msg0.setAlignment(Qt.AlignCenter)
        lbl_msg0.setStyleSheet("font-size: 14px;")
        vbox0.addStretch()
        vbox0.addWidget(lbl_tit0)
        vbox0.addWidget(lbl_msg0)
        vbox0.addStretch()
        self.stack.addWidget(page0)

        # -- PÁGINA 1: Quantidade de Slides --
        page1 = QWidget()
        vbox1 = QVBoxLayout(page1)
        lbl_tit1 = QLabel(f"<h3>{idiomas.tr('ast_p1_tit')}</h3>")
        lbl_msg1 = QLabel(idiomas.tr("ast_p1_msg"))
        lbl_msg1.setWordWrap(True)
        self.combo_qtd = QComboBox()
        self.combo_qtd.addItems([str(i) for i in range(1, 21)]) # 1 a 20 slides
        self.combo_qtd.setCurrentIndex(9) # Padrão em 10
        self.combo_qtd.setStyleSheet("font-size: 16px; padding: 5px;")
        vbox1.addStretch()
        vbox1.addWidget(lbl_tit1)
        vbox1.addWidget(lbl_msg1)
        vbox1.addWidget(self.combo_qtd)
        vbox1.addStretch()
        self.stack.addWidget(page1)

        # -- PÁGINA 2: Tema --
        page2 = QWidget()
        vbox2 = QVBoxLayout(page2)
        lbl_tit2 = QLabel(f"<h3>{idiomas.tr('ast_p2_tit')}</h3>")
        lbl_msg2 = QLabel(idiomas.tr("ast_p2_msg"))
        lbl_msg2.setWordWrap(True)
        self.txt_tema_ast = QTextEdit()
        self.txt_tema_ast.setPlaceholderText("...")
        vbox2.addWidget(lbl_tit2)
        vbox2.addWidget(lbl_msg2)
        vbox2.addWidget(self.txt_tema_ast)
        self.stack.addWidget(page2)

        # -- PÁGINA 3: Imagens --
        page3 = QWidget()
        vbox3 = QVBoxLayout(page3)
        lbl_tit3 = QLabel(f"<h3>{idiomas.tr('ast_p3_tit')}</h3>")
        lbl_msg3 = QLabel(idiomas.tr("ast_p3_msg"))
        lbl_msg3.setWordWrap(True)
        self.combo_img = QComboBox()
        self.combo_img.setStyleSheet("font-size: 16px; padding: 5px;")
        vbox3.addStretch()
        vbox3.addWidget(lbl_tit3)
        vbox3.addWidget(lbl_msg3)
        vbox3.addWidget(self.combo_img)
        vbox3.addStretch()
        self.stack.addWidget(page3)

        # -- PÁGINA 4: Resumo --
        page4 = QWidget()
        vbox4 = QVBoxLayout(page4)
        lbl_tit4 = QLabel(f"<h2>{idiomas.tr('ast_p4_tit')}</h2>")
        lbl_tit4.setAlignment(Qt.AlignCenter)
        self.lbl_resumo = QLabel()
        self.lbl_resumo.setWordWrap(True)
        self.lbl_resumo.setAlignment(Qt.AlignCenter)
        self.lbl_resumo.setStyleSheet("font-size: 14px; background-color: rgba(0, 120, 215, 0.1); padding: 15px; border-radius: 8px;")
        vbox4.addStretch()
        vbox4.addWidget(lbl_tit4)
        vbox4.addWidget(self.lbl_resumo)
        vbox4.addStretch()
        self.stack.addWidget(page4)

        # -- CONTROLES DE NAVEGAÇÃO --
        hbox_botoes = QHBoxLayout()
        self.btn_voltar = QPushButton(idiomas.tr("ast_btn_voltar"))
        self.btn_voltar.clicked.connect(self.voltar)
        self.btn_voltar.hide() # Esconde na primeira tela
        
        self.btn_avancar = QPushButton(idiomas.tr("ast_btn_avancar"))
        self.btn_avancar.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold;")
        self.btn_avancar.clicked.connect(self.avancar)
        
        hbox_botoes.addWidget(self.btn_voltar)
        hbox_botoes.addStretch()
        hbox_botoes.addWidget(self.btn_avancar)
        layout_principal.addLayout(hbox_botoes)

    def atualizar_combo_imagens(self):
        import idiomas
        self.combo_img.clear()
        qtd_slides = int(self.combo_qtd.currentText())
        self.combo_img.addItem(idiomas.tr("ast_p3_opt_todos"), "todos")
        for i in range(1, qtd_slides + 1):
            self.combo_img.addItem(f"{i} slide(s)", str(i))
        self.combo_img.addItem(idiomas.tr("ast_p3_opt_nenhum"), "0")

    def voltar(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self.atualizar_botoes()

    def avancar(self):
        import idiomas
        idx = self.stack.currentIndex()
        
        # Validação do Tema
        if idx == 2 and not self.txt_tema_ast.toPlainText().strip():
            QMessageBox.warning(self, idiomas.tr("msg_aviso"), "Por favor, digite o tema da apresentação para continuar.")
            return

        if idx == 1:
            self.atualizar_combo_imagens()
            
        if idx == 2:
            pass # Avança normal

        if idx == 3:
            # Prepara o resumo antes de mostrar a última tela
            qtd = self.combo_qtd.currentText()
            tema = self.txt_tema_ast.toPlainText().strip()
            imgs = self.combo_img.currentText()
            self.lbl_resumo.setText(idiomas.tr("ast_p4_resumo").format(qtd, tema, imgs))
            self.stack.setCurrentIndex(idx + 1)
            self.atualizar_botoes()
            return

        if idx == 4:
            # FINALIZAR! Monta o prompt formatado
            qtd = self.combo_qtd.currentText()
            tema = self.txt_tema_ast.toPlainText().strip()
            img_val = self.combo_img.currentData()
            
            txt_regra_img = ""
            if img_val == "0":
                txt_regra_img = "NÃO inclua sugestões de imagens em nenhum slide."
            elif img_val == "todos":
                txt_regra_img = "Inclua sugestões de imagens em TODOS os slides."
            else:
                txt_regra_img = f"Inclua sugestões de imagens em exatamente {img_val} slides."

            self.prompt_final = f"Tema Principal: {tema}\n\n[Regras do Assistente - STRICT]:\n- Crie exatamente {qtd} slides.\n- {txt_regra_img}"
            self.accept()
            return

        self.stack.setCurrentIndex(idx + 1)
        self.atualizar_botoes()

    def atualizar_botoes(self):
        import idiomas
        idx = self.stack.currentIndex()
        self.btn_voltar.setVisible(idx > 0)
        
        if idx == 4:
            self.btn_avancar.setText(idiomas.tr("ast_btn_gerar"))
            self.btn_avancar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        else:
            self.btn_avancar.setText(idiomas.tr("ast_btn_avancar"))
            self.btn_avancar.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 5px;")


def aplicar_toggle_senha(line_edit: QLineEdit):
    """Insere o botão nativo de visualização de senha no próprio QLineEdit sem alterar o layout."""
    action = line_edit.addAction(QIcon(), QLineEdit.TrailingPosition)
    action.setText("👁️")
    action.setToolTip("Mostrar/Ocultar Senha")
    
    def alternar():
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            action.setText("🙈")
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            action.setText("👁️")
            
    action.triggered.connect(alternar)


class CortadorFotoDialog(QDialog):
    """Janela com recorte circular interativo e preview antes de salvar a foto de perfil."""
    def __init__(self, imagem_origem, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustar Foto de Perfil")
        self.setFixedSize(380, 440)
        self.pix_original = QPixmap(imagem_origem)
        self.resultado_circular = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        lbl_instrucao = QLabel("<b>Ajuste a visualização do seu avatar:</b>")
        lbl_instrucao.setStyleSheet("color: white; font-size: 13px;")
        lbl_instrucao.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_instrucao)

        self.lbl_preview = QLabel()
        self.lbl_preview.setFixedSize(220, 220)
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_preview, alignment=Qt.AlignCenter)

        # Slider para dar zoom/enquadrar a foto dentro do círculo
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(100, 300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(self.atualizar_recorte)
        layout.addWidget(self.slider_zoom)

        hbox_btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Confirmar Foto")
        btn_save.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        btn_save.clicked.connect(self.accept)

        hbox_btns.addWidget(btn_cancel)
        hbox_btns.addWidget(btn_save)
        layout.addLayout(hbox_btns)

        self.atualizar_recorte()

    def atualizar_recorte(self):
        if self.pix_original.isNull():
            return
        fator = self.slider_zoom.value() / 100.0
        w_alvo = int(220 * fator)
        h_alvo = int(220 * fator)

        scaled = self.pix_original.scaled(w_alvo, h_alvo, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # Recorta do centro exato
        x = max(0, (scaled.width() - 220) // 2)
        y = max(0, (scaled.height() - 220) // 2)
        cropped_square = scaled.copy(x, y, 220, 220)

        # Cria a máscara do círculo perfeito
        out_pix = QPixmap(220, 220)
        out_pix.fill(Qt.transparent)

        from PySide6.QtGui import QPainterPath
        painter = QPainter(out_pix)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 220, 220)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, cropped_square)
        painter.end()

        self.resultado_circular = out_pix
        self.lbl_preview.setPixmap(out_pix)


class PerfilUsuarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Minha Conta - VegaTech")
        self.setMinimumSize(440, 620)
        self.resize(440, 640)
        self.avatar_cache_path = os.path.join(user_data_dir, "avatar_perfil.png")
        self.token = ""
        if parent and hasattr(parent, 'config'):
            self.token = parent.config.get("token_master", "")
        self.init_ui()
        self.carregar_dados_servidor()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        vbox_avatar = QVBoxLayout()
        vbox_avatar.setAlignment(Qt.AlignCenter)
        vbox_avatar.setSpacing(8)

        self.lbl_avatar = QLabel()
        self.lbl_avatar.setFixedSize(96, 96)
        self.lbl_avatar.setAlignment(Qt.AlignCenter)
        self.carregar_avatar_visual()

        btn_trocar_foto = QPushButton("Alterar Foto")
        btn_trocar_foto.setCursor(Qt.PointingHandCursor)
        btn_trocar_foto.setStyleSheet("background: #2b5c8f; color: white; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: bold;")
        btn_trocar_foto.clicked.connect(self.escolher_foto)

        vbox_avatar.addWidget(self.lbl_avatar)
        vbox_avatar.addWidget(btn_trocar_foto)
        layout.addLayout(vbox_avatar)

        # Card de Informações
        card_info = QFrame()
        card_info.setStyleSheet("QFrame#CardInfo { background-color: #222; border: 1px solid #444; border-radius: 8px; }")
        card_info.setObjectName("CardInfo")
        lay_info = QVBoxLayout(card_info)
        lay_info.setContentsMargins(16, 14, 16, 14)
        lay_info.setSpacing(8)

        lbl_tit_dados = QLabel("<b>DADOS DA CONTA</b>")
        lbl_tit_dados.setStyleSheet("color: #0078d7; font-size: 13px; letter-spacing: 1px;")

        self.lbl_nome = QLabel("Nome: Carregando...")
        self.lbl_nome.setStyleSheet("color: white; font-size: 13px;")
        self.lbl_nome.setWordWrap(True)

        self.lbl_email = QLabel("E-mail: Carregando...")
        self.lbl_email.setStyleSheet("color: #ccc; font-size: 13px;")
        self.lbl_email.setWordWrap(True)

        self.lbl_cpf = QLabel("CPF/CNPJ: -")
        self.lbl_cpf.setStyleSheet("color: #aaa; font-size: 13px;")

        self.lbl_criado_em = QLabel("Membro desde: -")
        self.lbl_criado_em.setStyleSheet("color: #888; font-size: 12px;")

        self.lbl_licenca = QLabel("Plano: Consultando...")
        self.lbl_licenca.setStyleSheet("color: #28a745; font-size: 13px; font-weight: bold;")

        lay_info.addWidget(lbl_tit_dados)
        lay_info.addWidget(self.lbl_nome)
        lay_info.addWidget(self.lbl_email)
        lay_info.addWidget(self.lbl_cpf)
        lay_info.addWidget(self.lbl_criado_em)
        lay_info.addWidget(self.lbl_licenca)
        layout.addWidget(card_info)

        card_senha = QFrame()
        card_senha.setStyleSheet("QFrame#CardSenha { background-color: #222; border: 1px solid #444; border-radius: 8px; }")
        card_senha.setObjectName("CardSenha")
        lay_senha = QVBoxLayout(card_senha)
        lay_senha.setContentsMargins(16, 14, 16, 14)
        lay_senha.setSpacing(10)

        lbl_tit_senha = QLabel("<b>SEGURANÇA</b>")
        lbl_tit_senha.setStyleSheet("color: #aaa; font-size: 12px; letter-spacing: 1px;")
        lay_senha.addWidget(lbl_tit_senha)

        btn_alterar_senha = QPushButton("Trocar Minha Senha")
        btn_alterar_senha.setCursor(Qt.PointingHandCursor)
        btn_alterar_senha.setStyleSheet("background: #333; color: white; border: 1px solid #555; padding: 10px; border-radius: 4px; font-weight: bold; font-size: 13px;")
        btn_alterar_senha.clicked.connect(self.abrir_recuperacao_interna)
        lay_senha.addWidget(btn_alterar_senha)
        layout.addWidget(card_senha)

        layout.addStretch()

        hbox_rodape = QHBoxLayout()
        btn_logout = QPushButton("Sair da Conta")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("background-color: #a8201a; color: white; padding: 10px 18px; font-weight: bold; border-radius: 4px; font-size: 13px;")
        btn_logout.clicked.connect(self.realizar_logout)

        btn_fechar = QPushButton("Concluído")
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setStyleSheet("background-color: #0078d7; color: white; padding: 10px 22px; font-weight: bold; border-radius: 4px; font-size: 13px;")
        btn_fechar.clicked.connect(self.accept)

        hbox_rodape.addWidget(btn_logout)
        hbox_rodape.addStretch()
        hbox_rodape.addWidget(btn_fechar)
        layout.addLayout(hbox_rodape)

    def carregar_dados_servidor(self):
        if not self.token:
            self.lbl_nome.setText("<b>Nome:</b> Não autenticado")
            self.lbl_email.setText("<b>E-mail:</b> -")
            self.lbl_licenca.setText("<b>Plano:</b> Gratuito (FREE)")
            return

        url = "https://vegap-masterapp.hf.space/auth/app/perfil"
        sucesso = False
        dados = {}
        try:
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            if resp.status_code == 200:
                dados = resp.json()
                sucesso = True
        except Exception:
            sucesso = False

        if sucesso:
            nome_res = dados.get("nome", "-")
            email_res = dados.get("email", "-")
            doc_res = dados.get("documento", "-")
            criado_res = dados.get("criado_em", "-")
            plano_res = dados.get("plano", "FREE")
            foto_b64 = dados.get("foto")

            self.lbl_nome.setText(f"<b>Nome:</b> {nome_res}")
            self.lbl_email.setText(f"<b>E-mail:</b> {email_res}")
            self.lbl_cpf.setText(f"<b>CPF/CNPJ:</b> {doc_res}")
            self.lbl_criado_em.setText(f"<b>Membro desde:</b> {criado_res}")
            self.lbl_licenca.setText(f"<b>Plano:</b> {plano_res}")

            # Se veio foto do banco e não existe localmente, salva e exibe
            if foto_b64:
                try:
                    import base64
                    img_bytes = base64.b64decode(foto_b64)
                    with open(self.avatar_cache_path, "wb") as f_out:
                        f_out.write(img_bytes)
                    self.carregar_avatar_visual()
                except Exception:
                    pass

            pai = self.parent()
            if pai and hasattr(pai, 'config'):
                if plano_res in ["PRO", "SAAS", "ELITE"] or dados.get("is_vip"):
                    pai.config["saas_padrao_ativo"] = True
                    pai.config["license"] = "SAAS (Chave Embutida)"
                    if hasattr(pai, 'update_main_ui_lock'):
                        pai.update_main_ui_lock()
        else:
            self.lbl_nome.setText("<b>Nome:</b> Sessão local ativa")
            self.lbl_email.setText("<b>E-mail:</b> Não sincronizado")
            self.lbl_licenca.setText("<b>Plano:</b> Gratuito (FREE)")

    def carregar_avatar_visual(self):
        if os.path.exists(self.avatar_cache_path):
            pix = QPixmap(self.avatar_cache_path)
            if not pix.isNull():
                tamanho = 96
                # Escala cortando para preencher um quadrado perfeito
                scaled = pix.scaled(tamanho, tamanho, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x = (scaled.width() - tamanho) // 2
                y = (scaled.height() - tamanho) // 2
                quadrado = scaled.copy(x, y, tamanho, tamanho)

                # Máscara redonda com antialiasing
                redondo = QPixmap(tamanho, tamanho)
                redondo.fill(Qt.transparent)

                from PySide6.QtGui import QPainterPath
                painter = QPainter(redondo)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, tamanho, tamanho)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, quadrado)

                # Borda neon VegaTech azul ao redor do círculo
                pen = QPen(QColor("#0078d7"), 2)
                painter.setPen(pen)
                painter.drawEllipse(1, 1, tamanho - 2, tamanho - 2)
                painter.end()

                self.lbl_avatar.setPixmap(redondo)
                self.lbl_avatar.setStyleSheet("border: none; background: transparent;")
                return

        self.lbl_avatar.setText("👤")
        self.lbl_avatar.setStyleSheet("font-size: 42px; background-color: #333; border: 2px solid #555; border-radius: 48px; color: #aaa;")

    def escolher_foto(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto de Perfil", "", "Imagens (*.png *.jpg *.jpeg)")
        if not path:
            return

        dialog_cortador = CortadorFotoDialog(path, self)
        if dialog_cortador.exec() == QDialog.Accepted and dialog_cortador.resultado_circular:
            try:
                # Salva o círculo recortado no cache local offline-first
                dialog_cortador.resultado_circular.save(self.avatar_cache_path, "PNG")
                self.carregar_avatar_visual()

                # Sincronização com o backend (Hugging Face)
                if self.token:
                    import base64
                    with open(self.avatar_cache_path, "rb") as f_img:
                        b64_foto = base64.b64encode(f_img.read()).decode("utf-8")

                    try:
                        requests.post(
                            "https://vegap-masterapp.hf.space/auth/app/foto",
                            headers={"Authorization": f"Bearer {self.token}"},
                            json={"foto": b64_foto},
                            timeout=10
                        )
                    except Exception:
                        pass # Continua normalmente se o servidor oscilar, pois já está no cache local

                QMessageBox.information(self, "Sucesso", "Foto de perfil atualizada e recortada com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar avatar: {str(e)}")

    def abrir_recuperacao_interna(self):
        dialog = RecuperarSenhaDialog(parent=self)
        dialog.exec()

    def realizar_logout(self):
        resp = QMessageBox.question(
            self,
            "Confirmar Saída",
            "Deseja realmente sair da sua conta VegaTech?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            pai = self.parent()
            if pai and hasattr(pai, 'config'):
                pai.config["token_master"] = ""
                pai.config["byok_ativo"] = False
                pai.config["saas_padrao_ativo"] = False
                pai.config["saas_elite_ativo"] = False
                pai.config["license"] = "FREE"
                if hasattr(pai, 'save_config'):
                    pai.save_config()
                if hasattr(pai, 'update_main_ui_lock'):
                    pai.update_main_ui_lock()
            
            if os.path.exists(self.avatar_cache_path):
                try:
                    os.remove(self.avatar_cache_path)
                except:
                    pass

            QMessageBox.information(self, "Logout", "Você saiu da sua conta.")
            self.accept()

    def abrir_recuperacao_interna(self):
        dialog = RecuperarSenhaDialog(parent=self)
        dialog.exec()

    def realizar_logout(self):
        resp = QMessageBox.question(
            self,
            "Confirmar Saída",
            "Deseja realmente sair da sua conta VegaTech?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            pai = self.parent()
            if pai and hasattr(pai, 'config'):
                pai.config["token_master"] = ""
                pai.config["byok_ativo"] = False
                pai.config["saas_padrao_ativo"] = False
                pai.config["saas_elite_ativo"] = False
                pai.config["license"] = "FREE"
                if hasattr(pai, 'save_config'):
                    pai.save_config()
                if hasattr(pai, 'update_main_ui_lock'):
                    pai.update_main_ui_lock()
            
            if os.path.exists(self.avatar_cache_path):
                try:
                    os.remove(self.avatar_cache_path)
                except:
                    pass

            QMessageBox.information(self, "Logout", "Você saiu da sua conta.")
            self.accept()
            
class PromptSizeGrip(QSizeGrip):
    """Grip com indicador visual clássico de 3 estrias diagonais no canto inferior direito."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(18, 18)
        self._hover = False
        self.setCursor(Qt.SizeVerCursor)

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cor = QColor("#0078d7") if self._hover else QColor("#888888")
        pen = QPen(cor, 1.8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Três linhas diagonais no canto inferior direito
        w, h = self.width(), self.height()
        painter.drawLine(w - 4, h - 12, w - 12, h - 4)
        painter.drawLine(w - 4, h - 8, w - 8, h - 4)
        painter.drawLine(w - 4, h - 4, w - 4, h - 4)


class ResizablePromptEdit(QTextEdit):
    """Campo de texto com alça visível de redimensionamento no canto inferior direito."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(65)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._resizing = False
        self._drag_start_y = 0
        self._start_height = 65

        # Pega visual com estrias no canto inferior direito
        self.grip = PromptSizeGrip(self)
        self.grip.installEventFilter(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.grip.move(self.width() - self.grip.width() - 2, self.height() - self.grip.height() - 2)

    def eventFilter(self, obj, event):
        if obj == self.grip:
            if event.type() == QEvent.MouseButtonPress:
                self._resizing = True
                self._drag_start_y = event.globalPosition().toPoint().y()
                self._start_height = self.height()
                self.grip._hover = True
                self.grip.update()
                return True
            elif event.type() == QEvent.MouseMove and self._resizing:
                delta_y = event.globalPosition().toPoint().y() - self._drag_start_y
                nova_altura = max(65, self._start_height + delta_y)
                self.setFixedHeight(nova_altura)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self._resizing = False
                self.grip._hover = False
                self.grip.update()
                return True
        return super().eventFilter(obj, event)


class AppPaiVega(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{NOME_APP_MASTER} {VERSAO_ATUAL}")
        self.resize(650, 650)
        
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
        self.is_manual_pptx = False # <-- TRAVA ANTI-CONFLITO
        self.last_saved_pptx = None # Guarda o último editado para o conversor de PDF
        self.bg_path = None
        self.text_color_title = None # <-- COR SEPARADA DO TÍTULO
        self.text_color_body = None  # <-- COR SEPARADA DO CORPO
        self.fill_color = None

        # A MÁGICA ACONTECE AQUI: Aplica o zoom e o tema ANTES de desenhar a interface!
        self.apply_zoom(self.config.get("zoom", 100))
        self.apply_theme()
        
        import idiomas
        idiomas.set_idioma(self.config.get("idioma", "pt"))
        
        self.init_ui() # Agora todos os textos e botões já nascem do tamanho salvo!
        self.atualizar_textos_ui() # Aciona a tradução pela primeira vez
        
        # Instancia o buraco negro invisível por cima da UI
        self.overlay_tutorial = TutorialOverlay(self)
        
        # Verifica se o atualizador deixou algum recado de novidades
        self.checar_notas_atualizacao()
        
        # O Radar do Megafone (Quadro de Avisos)
        self.checar_avisos_startup()

    def load_config(self):
        import base64
        import json
        default_config = {
            "license": "FREE", 
            "api_key": "", 
            "model": "", 
            "theme": "Escuro", 
            "zoom": 100,
            "idioma": "pt",
            "saas_elite_ativo": False,
            "saas_padrao_ativo": False,
            "byok_ativo": False,
            "app_editor": "Sistema (Padrão)"
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                    
                if conteudo.startswith("{"): 
                    dados = json.loads(conteudo)
                    if dados.get("license") == "SAAS (Chave Embutida)" and not dados.get("token_master"):
                        dados["license"] = "FREE" 
                    # Garante que os campos de ativação venham preenchidos se existirem
                    for k, v in default_config.items():
                        if k not in dados: dados[k] = v
                    return dados
                else:
                    texto_reverso = conteudo[::-1]
                    json_str = base64.b64decode(texto_reverso.encode('utf-8')).decode('utf-8')
                    dados = json.loads(json_str)
                    for k, v in default_config.items():
                        if k not in dados: dados[k] = v
                    return dados
            except: pass
            
        return default_config

    def save_config(self):
        import base64
        import json
        self.config["last_dir"] = self.last_dir
        try:
            json_str = json.dumps(self.config)
            
            # GOLPE VEGATECH: Aplica Base64 e inverte a string pra confundir xeretas
            b64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            texto_ofuscado = b64_str[::-1]
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(texto_ofuscado)
        except Exception as e:
            print(f"Erro na blindagem do config: {e}")

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
            # Cores Clássicas do Tema Escuro
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
            # Tema CLARO - Contraste Absoluto e Legível
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
            palette.setColor(QPalette.Link, QColor(0, 102, 204))
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
        app.setPalette(palette)
        
        # Injeta um estilo blindado para que os Checkboxes fiquem sempre desenhados e visíveis
        estilo_checkbox = """
            QCheckBox::indicator {
                width: 16px; height: 16px; border: 2px solid #777; border-radius: 3px; background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d7; border-color: #0078d7;
            }
        """
        app.setStyleSheet(estilo_checkbox)

        # Aplica a paleta apenas no TopLevel para não estragar a herança interna dos botões
        for w in app.topLevelWidgets():
            w.setPalette(palette)
            w.update()

    def apply_zoom(self, val):
        # 1. Fonte: Começa em 11 e aumenta conforme o slider
        base_size = 11
        # O slider vai de 0 a 100 (ou mais). 0 = 100% do tamanho, 50 = 150% do tamanho
        fator = 1.0 + (val / 100.0) 
        new_size = int(base_size * fator)
        
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(new_size)
        app.setFont(font)
        self.setFont(font)
        
        # 2. Janela: Base de 650px, aumenta conforme o slider
        nova_largura = int(650 * fator)
        self.setMinimumWidth(nova_largura)
        self.resize(nova_largura, self.height())

        # Ajusta os botões de ícone do topo proporcionalmente ao zoom
        if hasattr(self, 'btn_config'):
            tam_w = int(48 * fator)
            tam_h = int(40 * fator)
            font_size = int(20 * fator)
            for btn in [self.btn_config, self.btn_tutorial, self.btn_novidades, self.btn_avisos]:
                btn.setFixedSize(tam_w, tam_h)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2a2a2a;
                        color: #ffffff;
                        font-size: {font_size}px;
                        border: 1px solid #4a4a4a;
                        border-radius: {int(6 * fator)}px;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: #3a3a3a;
                        border: 1px solid #0078d7;
                    }}
                    QPushButton:pressed {{
                        background-color: #1a1a1a;
                    }}
                """)
        
        # Garante que qualquer outra janela filha atualize na mesma hora
        for w in app.topLevelWidgets():
            w.setFont(font)
            w.update()

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
        hbox_top.setSpacing(6)
        hbox_top.addStretch()

        # Base ampliada: botões encorpados com ícones grandes e legíveis
        estilo_icone = """
            QPushButton {
                background-color: #2a2a2a;
                color: #ffffff;
                font-size: 26px;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #0078d7;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """

        self.btn_config = QPushButton("⚙️")
        self.btn_config.setFixedSize(52, 44)
        self.btn_config.setToolTip("Configurações e Conta")
        self.btn_config.setStyleSheet(estilo_icone)
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.clicked.connect(self.open_config)
        hbox_top.addWidget(self.btn_config)

        self.btn_tutorial = QPushButton("📚")
        self.btn_tutorial.setFixedSize(52, 44)
        self.btn_tutorial.setToolTip("Como Usar (Tutorial)")
        self.btn_tutorial.setStyleSheet(estilo_icone)
        self.btn_tutorial.setCursor(Qt.PointingHandCursor)
        self.btn_tutorial.clicked.connect(self.abrir_tutorial)
        hbox_top.addWidget(self.btn_tutorial)

        self.btn_novidades = QPushButton("📋")
        self.btn_novidades.setFixedSize(52, 44)
        self.btn_novidades.setToolTip("Novidades da Versão")
        self.btn_novidades.setStyleSheet(estilo_icone)
        self.btn_novidades.setCursor(Qt.PointingHandCursor)
        self.btn_novidades.clicked.connect(self.abrir_novidades)
        hbox_top.addWidget(self.btn_novidades)

        self.btn_avisos = QPushButton("📢")
        self.btn_avisos.setFixedSize(52, 44)
        self.btn_avisos.setToolTip("Quadro de Avisos")
        self.btn_avisos.setStyleSheet(estilo_icone)
        self.btn_avisos.setCursor(Qt.PointingHandCursor)
        self.btn_avisos.clicked.connect(self.abrir_avisos)
        hbox_top.addWidget(self.btn_avisos)

        self.main_layout.addLayout(hbox_top)

        self.btn_load = QPushButton("1. Carregar Apresentação Pronta (.pptx)")
        self.btn_load.clicked.connect(self.load_pptx)
        self.lbl_pptx = QLabel("Nenhum arquivo selecionado")
        self.lbl_pptx.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 15px;") # Vermelho, gordo e grande

        self.main_layout.addWidget(self.btn_load)
        self.main_layout.addWidget(self.lbl_pptx)

        from PySide6.QtWidgets import QSizePolicy
        from PySide6.QtCore import QEvent

        hbox_ia = QHBoxLayout()
        
        # TÍTULO DA SEÇÃO DE CRIAÇÃO
        self.lbl_titulo_ia = QLabel()
        self.lbl_titulo_ia.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        self.main_layout.addWidget(self.lbl_titulo_ia)

        # CAMPO DE PROMPT COM ALÇA DE REDIMENSIONAMENTO NO CANTO INFERIOR DIREITO
        self.txt_tema = ResizablePromptEdit()
        self.txt_tema.setPlaceholderText("Digite o tema para a IA criar a apresentação...")
        self.txt_tema.viewport().installEventFilter(self)
        self.txt_tema.textChanged.connect(self.checar_atalho_forma)
        self.main_layout.addWidget(self.txt_tema)

        # Painel com os 4 botões logo abaixo do prompt
        container_botoes_ia = QWidget()
        lay_botoes_ia = QVBoxLayout(container_botoes_ia)
        lay_botoes_ia.setContentsMargins(0, 4, 0, 0)
        lay_botoes_ia.setSpacing(6)

        estilo_base = "color: white; font-weight: bold; font-size: 13px; border-radius: 5px;"

        # FILEIRA 1: AÇÕES DE GERAR (DIVIDIDAS 50% / 50%)
        hbox_geracao = QHBoxLayout()
        hbox_geracao.setSpacing(8)

        self.btn_gerar_ia = QPushButton("🚀 Criar Apresentação Automática (IA)")
        self.btn_gerar_ia.setFixedHeight(42)
        self.btn_gerar_ia.setStyleSheet(f"background-color: #2b5c8f; {estilo_base}")
        self.btn_gerar_ia.setCursor(Qt.PointingHandCursor)
        self.btn_gerar_ia.clicked.connect(self.gerar_com_ia)

        self.btn_assistente = QPushButton("✨ Criação Guiada")
        self.btn_assistente.setFixedHeight(42)
        self.btn_assistente.setStyleSheet(f"background-color: #17a2b8; {estilo_base}")
        self.btn_assistente.setCursor(Qt.PointingHandCursor)
        self.btn_assistente.clicked.connect(self.abrir_dialogo_assistente)

        hbox_geracao.addWidget(self.btn_gerar_ia, 1)
        hbox_geracao.addWidget(self.btn_assistente, 1)
        lay_botoes_ia.addLayout(hbox_geracao)

        # FILEIRA 2: SMARTART E RECUPERAR SALVO (DIVIDIDAS 50% / 50%)
        hbox_apoio = QHBoxLayout()
        hbox_apoio.setSpacing(8)

        self.btn_forma = QPushButton("➕ Inserir SmartArt (/forma)")
        self.btn_forma.setFixedHeight(42)
        self.btn_forma.setStyleSheet(f"background-color: #6f42c1; {estilo_base}")
        self.btn_forma.setCursor(Qt.PointingHandCursor)
        self.btn_forma.clicked.connect(self.abrir_seletor_forma)

        self.btn_historico = QPushButton("🕒 Recuperar Salvo (Reabrir)")
        self.btn_historico.setFixedHeight(42)
        self.btn_historico.setStyleSheet(f"background-color: #4a5568; {estilo_base}")
        self.btn_historico.setCursor(Qt.PointingHandCursor)
        self.btn_historico.clicked.connect(self.abrir_historico)

        hbox_apoio.addWidget(self.btn_forma, 1)
        hbox_apoio.addWidget(self.btn_historico, 1)
        lay_botoes_ia.addLayout(hbox_apoio)

        self.main_layout.addWidget(container_botoes_ia)
        
        # --- DROPDOWN DE PRESETS (ITEM 5) ---
        hbox_preset = QHBoxLayout()
        self.combo_presets = QComboBox()
        self.combo_presets.addItem("Personalizado (Manual)")
        self.combo_presets.addItem("Corporativo Azul")
        self.combo_presets.addItem("Dark Mode Clássico")
        self.combo_presets.addItem("Minimalista Clean")
        self.combo_presets.currentIndexChanged.connect(self.aplicar_preset)
        self.combo_presets.setCursor(Qt.PointingHandCursor)
        self.combo_presets.setStyleSheet("padding: 4px;") # Arrancado o font-size fixo!
        
        self.lbl_presets = QLabel()
        hbox_preset.addWidget(self.lbl_presets)
        hbox_preset.addWidget(self.combo_presets)
        hbox_preset.addStretch()
        self.main_layout.addLayout(hbox_preset)

        # --- 2. SELEÇÃO DE COR DE TEXTO SEPARADA (ITEM 3) ---
        hbox_color_title = QHBoxLayout()
        self.btn_color_title = QPushButton("🎨 Cor dos Títulos")
        self.btn_color_title.setCursor(Qt.PointingHandCursor)
        self.btn_color_title.clicked.connect(self.choose_title_color)
        self.lbl_color_title_indicator = self.create_color_indicator()
        
        self.lbl_cor_titulos = QLabel()
        hbox_color_title.addWidget(self.lbl_cor_titulos)
        hbox_color_title.addWidget(self.btn_color_title)
        hbox_color_title.addWidget(self.lbl_color_title_indicator)
        hbox_color_title.addStretch()
        self.main_layout.addLayout(hbox_color_title)

        hbox_color_body = QHBoxLayout()
        self.btn_color_body = QPushButton()
        self.btn_color_body.setCursor(Qt.PointingHandCursor)
        self.btn_color_body.clicked.connect(self.choose_body_color)
        self.lbl_color_body_indicator = self.create_color_indicator()
        
        self.lbl_cor_textos = QLabel()
        hbox_color_body.addWidget(self.lbl_cor_textos)
        hbox_color_body.addWidget(self.btn_color_body)
        hbox_color_body.addWidget(self.lbl_color_body_indicator)
        hbox_color_body.addStretch()
        self.main_layout.addLayout(hbox_color_body)
        
        # --- SELEÇÃO DE FONTE COM PREVIEW (SUGESTÃO 4) ---
        # --- SELEÇÃO DE FONTES (ITEM 2) ---
        fontes_comuns = ["Padrão do Tema", "Arial", "Calibri", "Century Gothic", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"]
        
        # FONTE DOS TÍTULOS
        hbox_font_title = QHBoxLayout()
        self.combo_font_title = QComboBox()
        for i, nome_fonte in enumerate(fontes_comuns):
            self.combo_font_title.addItem(nome_fonte, nome_fonte)
            if i > 0: # 0 é o Padrão
                self.combo_font_title.setItemData(i, QFont(nome_fonte), Qt.FontRole)
        self.combo_font_title.setCursor(Qt.PointingHandCursor)

        self.lbl_font_title_preview = QLabel("Aa Título")
        self.lbl_font_title_preview.setStyleSheet("font-size: 18px; color: gray; font-weight: bold;")
        self.combo_font_title.currentIndexChanged.connect(
            lambda idx: self.lbl_font_title_preview.setStyleSheet(f"font-size: 18px; font-family: '{self.combo_font_title.itemData(idx)}'; font-weight: bold; color: #0078d7;") if idx != 0 else self.lbl_font_title_preview.setStyleSheet("font-size: 18px; color: gray; font-weight: bold;")
        )
        
        self.btn_add_font = QPushButton("➕ Nova Fonte")
        self.btn_add_font.setCursor(Qt.PointingHandCursor)
        self.btn_add_font.clicked.connect(self.adicionar_fonte_customizada)
        self.btn_add_font.setStyleSheet("padding: 4px; font-weight: bold;")

        self.lbl_fonte_titulos = QLabel()
        hbox_font_title.addWidget(self.lbl_fonte_titulos)
        hbox_font_title.addWidget(self.combo_font_title)
        hbox_font_title.addWidget(self.btn_add_font)
        hbox_font_title.addWidget(self.lbl_font_title_preview)
        hbox_font_title.addStretch()
        self.main_layout.addLayout(hbox_font_title)

        # FONTE DOS TEXTOS (CORPO)
        hbox_font_body = QHBoxLayout()
        self.combo_font_body = QComboBox()
        for i, nome_fonte in enumerate(fontes_comuns):
            self.combo_font_body.addItem(nome_fonte, nome_fonte)
            if i > 0:
                self.combo_font_body.setItemData(i, QFont(nome_fonte), Qt.FontRole)
        self.combo_font_body.setCursor(Qt.PointingHandCursor)
                
        # Avisa o mini-slide quando o usuário trocar as fontes
        self.combo_font_title.currentIndexChanged.connect(self.atualizar_preview_real)
        self.combo_font_body.currentIndexChanged.connect(self.atualizar_preview_real)

        self.lbl_font_body_preview = QLabel("Aa Corpo")
        self.lbl_font_body_preview.setStyleSheet("font-size: 14px; color: gray;")
        self.combo_font_body.currentIndexChanged.connect(
            lambda idx: self.lbl_font_body_preview.setStyleSheet(f"font-size: 14px; font-family: '{self.combo_font_body.itemData(idx)}'; color: #0078d7;") if idx != 0 else self.lbl_font_body_preview.setStyleSheet("font-size: 14px; color: gray;")
        )
        
        self.lbl_fonte_textos = QLabel()
        hbox_font_body.addWidget(self.lbl_fonte_textos)
        hbox_font_body.addWidget(self.combo_font_body)
        hbox_font_body.addWidget(self.lbl_font_body_preview)
        hbox_font_body.addStretch()
        self.main_layout.addLayout(hbox_font_body)

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

        # --- 5. ESCALA DE IMAGENS COM SLIDER (DIMINUI E AUMENTA - ITEM 2) ---
        hbox_scale = QHBoxLayout()
        self.chk_scale = QCheckBox("5. Escala das imagens:")
        self.slider_scale = QSlider(Qt.Horizontal)
        self.slider_scale.setRange(10, 200) # 10% até 200% do tamanho
        self.slider_scale.setValue(100) # 100% é o tamanho original exacto
        self.slider_scale.setEnabled(False)
        self.lbl_scale_val = QLabel("100%")
        self.lbl_scale_val.setStyleSheet("font-weight: bold;")
        
        self.chk_scale.toggled.connect(self.slider_scale.setEnabled)
        self.slider_scale.valueChanged.connect(lambda v: self.lbl_scale_val.setText(f"{v}%"))
        
        hbox_scale.addWidget(self.chk_scale)
        hbox_scale.addWidget(self.slider_scale)
        hbox_scale.addWidget(self.lbl_scale_val)
        self.main_layout.addLayout(hbox_scale)

        # --- 5.1. AUMENTO DE TEXTOS COM SLIDER ---
        hbox_text_scale = QHBoxLayout()
        self.chk_text_scale = QCheckBox("5.1. Aumentar textos em:")
        self.slider_text_scale = QSlider(Qt.Horizontal)
        self.slider_text_scale.setRange(1, 150)
        self.slider_text_scale.setValue(20)
        self.slider_text_scale.setEnabled(False)
        self.lbl_text_scale_val = QLabel("20%")
        self.lbl_text_scale_val.setStyleSheet("font-weight: bold;")
        
        self.chk_text_scale.toggled.connect(self.slider_text_scale.setEnabled)
        self.slider_text_scale.valueChanged.connect(lambda v: self.lbl_text_scale_val.setText(f"{v}%"))
        
        hbox_text_scale.addWidget(self.chk_text_scale)
        hbox_text_scale.addWidget(self.slider_text_scale)
        hbox_text_scale.addWidget(self.lbl_text_scale_val)
        self.main_layout.addLayout(hbox_text_scale)

        # --- PREVISÃO AO VIVO (MINI-SLIDE) ---
        hbox_preview = QHBoxLayout()
        self.frame_preview = QFrame()
        self.frame_preview.setFixedSize(320, 180) # Formato 16:9 perfeito
        self.frame_preview.setStyleSheet("background-color: white; border: 2px solid #ccc; border-radius: 8px;")
        
        # Barra lateral azul do mini-slide
        self.barra_preview_lateral = QFrame(self.frame_preview)
        self.barra_preview_lateral.setGeometry(0, 0, 8, 180)
        self.barra_preview_lateral.setStyleSheet("background-color: #2b5c8f; border-top-left-radius: 6px; border-bottom-left-radius: 6px; border: none;")

        # Elementos posicionados de forma absoluta no slide virtual
        self.lbl_preview_text = QLabel("Título Exemplo\n\nEste é o corpo do texto.\nVeja como ele cresce.", self.frame_preview)
        self.lbl_preview_text.setGeometry(16, 10, 174, 160)
        self.lbl_preview_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.lbl_preview_text.setStyleSheet("color: #333; border: none; font-size: 10px;")

        self.lbl_preview_img = QLabel(idiomas.tr("lbl_preview_placeholder_img"), self.frame_preview)
        self.lbl_preview_img.setAlignment(Qt.AlignCenter)
        self.lbl_preview_img.setStyleSheet("""
            background-color: #2b5c8f;
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            border-radius: 6px;
            border: 1px dashed rgba(255, 255, 255, 0.6);
        """)
        self.lbl_preview_img.setGeometry(195, 40, 100, 100)

        hbox_preview.addStretch()
        hbox_preview.addWidget(self.frame_preview)
        hbox_preview.addStretch()
        self.main_layout.addLayout(hbox_preview)
        
        # Liga os gatilhos dos sliders e checkboxes ao método da classe
        self.chk_scale.toggled.connect(self.atualizar_preview_real)
        self.slider_scale.valueChanged.connect(self.atualizar_preview_real)
        self.chk_text_scale.toggled.connect(self.atualizar_preview_real)
        self.slider_text_scale.valueChanged.connect(self.atualizar_preview_real)
        
        self.atualizar_preview_real() # Força o primeiro desenho

        # Liga os gatilhos dos sliders e checkboxes à função de animação
        self.chk_scale.toggled.connect(self.atualizar_preview_real)
        self.slider_scale.valueChanged.connect(self.atualizar_preview_real)
        self.chk_text_scale.toggled.connect(self.atualizar_preview_real)
        self.slider_text_scale.valueChanged.connect(self.atualizar_preview_real)
        
        self.atualizar_preview_real() # Força o primeiro desenho # Força o primeiro desenho
        
        # --- CHAVE PARA LIGAR/DESLIGAR AS ANOTAÇÕES (SUGESTÃO 2) ---
        hbox_notes = QHBoxLayout()
        self.chk_notes = QCheckBox("5.2. Inserir Roteiro do Apresentador nas anotações nativas")
        self.chk_notes.setChecked(True) # Deixamos ativo por padrão, o usuário desmarca se quiser
        
        self.chk_barra_lateral = QCheckBox("5.3. Exibir barra azul lateral")
        self.chk_barra_lateral.setChecked(True)
        self.chk_barra_lateral.toggled.connect(self.atualizar_preview_real)
        
        hbox_notes.addWidget(self.chk_notes)
        hbox_notes.addWidget(self.chk_barra_lateral)
        hbox_notes.addStretch()
        self.main_layout.addLayout(hbox_notes)

        self.btn_save = QPushButton("6. Processar Apresentação e Salvar")
        self.btn_save.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.btn_save.setStyleSheet("background-color: #a8201a; color: white; font-weight: bold; padding: 10px;")
        self.btn_save.clicked.connect(self.process_and_save)
        self.main_layout.addWidget(self.btn_save)

        # --- 7. BOTAO CONVERTER PARA PDF ---
        self.btn_pdf = QPushButton("7. Converter apresentação atual para PDF")
        self.btn_pdf.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.btn_pdf.setStyleSheet("background-color: #333; color: white; font-weight: bold; padding: 10px;")
        self.btn_pdf.clicked.connect(self.export_to_pdf)
        self.main_layout.addWidget(self.btn_pdf)

        # =========================================================
        # MÁGICA RESPONSIVA: Barra de Rolagem Inteligente
        # =========================================================
        from PySide6.QtWidgets import QScrollArea
        
        self.scroll_principal = QScrollArea()
        self.scroll_principal.setWidgetResizable(True) 
        self.scroll_principal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # <-- ASSASSINA A BARRA HORIZONTAL
        self.scroll_principal.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.scroll_principal.setWidget(self.main_container)
        
        # Agora o widget central da tela é a área de rolagem, que guarda todo o resto dentro dela
        self.setCentralWidget(self.scroll_principal)
        
        self.update_main_ui_lock()   

    def atualizar_textos_ui(self):
        # Garante que os botões do topo exibam estritamente seus ícones fixos e o texto apenas no ToolTip
        self.btn_config.setText("⚙️")
        self.btn_config.setToolTip(idiomas.tr("btn_config"))
        self.btn_tutorial.setText("📚")
        self.btn_tutorial.setToolTip(idiomas.tr("btn_tutorial"))
        self.btn_novidades.setText("📋")
        self.btn_novidades.setToolTip(idiomas.tr("btn_novidades"))
        if hasattr(self, 'btn_avisos'):
            self.btn_avisos.setText("📢")
            self.btn_avisos.setToolTip(idiomas.tr("btn_avisos"))

        self.btn_load.setText(idiomas.tr("btn_load"))
        if not self.pptx_path:
            self.lbl_pptx.setText(idiomas.tr("lbl_pptx_vazio"))
        if hasattr(self, 'lbl_preview_img') and not getattr(self, 'bg_path', None):
            self.lbl_preview_img.setText(idiomas.tr("lbl_preview_placeholder_img"))
        self.lbl_titulo_ia.setText(idiomas.tr("lbl_titulo_ia"))
        self.btn_gerar_ia.setText(idiomas.tr("btn_ia_completo"))
        self.btn_assistente.setText(idiomas.tr("btn_guiado_completo"))
        self.btn_forma.setText(idiomas.tr("btn_smartart_completo"))
        self.btn_historico.setText(idiomas.tr("btn_recuperar_completo"))
        self.lbl_presets.setText(idiomas.tr("lbl_presets"))
        self.lbl_cor_titulos.setText(idiomas.tr("lbl_cor_titulos"))
        self.btn_color_title.setText(idiomas.tr("btn_cor_titulos_btn"))
        self.lbl_cor_textos.setText(idiomas.tr("lbl_cor_textos"))
        self.btn_color_body.setText(idiomas.tr("btn_cor_textos_btn"))
        self.btn_add_font.setText(idiomas.tr("btn_add_font"))
        self.lbl_fonte_titulos.setText(idiomas.tr("lbl_fonte_titulos"))
        self.lbl_fonte_textos.setText(idiomas.tr("lbl_fonte_textos"))
        self.btn_fill_color.setText(idiomas.tr("btn_fill_color"))
        self.btn_bg.setText(idiomas.tr("btn_bg"))
        if not self.bg_path:
            self.lbl_bg_preview.setText(idiomas.tr("lbl_bg_preview"))
        self.chk_scale.setText(idiomas.tr("chk_scale"))
        self.chk_text_scale.setText(idiomas.tr("chk_text_scale"))
        self.chk_notes.setText(idiomas.tr("chk_notes"))
        self.chk_barra_lateral.setText(idiomas.tr("chk_barra_lateral"))
        self.btn_save.setText(idiomas.tr("btn_save"))
        self.btn_pdf.setText(idiomas.tr("btn_pdf"))
        
        # Traduz as opções do ComboBox de Presets
        self.combo_presets.setItemText(0, idiomas.tr("preset_manual"))
        self.combo_presets.setItemText(1, idiomas.tr("preset_corp"))
        self.combo_presets.setItemText(2, idiomas.tr("preset_dark"))
        self.combo_presets.setItemText(3, idiomas.tr("preset_clean"))

        # Traduz a opção "Padrão do Tema" nos dois ComboBoxes de Fonte
        self.combo_font_title.setItemText(0, idiomas.tr("font_default"))
        self.combo_font_body.setItemText(0, idiomas.tr("font_default"))

        self.update_main_ui_lock()
        self.atualizar_preview_real()

    def update_main_ui_lock(self):
        import idiomas
        if "FREE" in self.config.get("license", "FREE"):
            self.txt_tema.setReadOnly(True)
            self.txt_tema.setPlaceholderText(idiomas.tr("txt_tema_lock"))
            self.txt_tema.setStyleSheet("background-color: #444; color: #888; border: 1px solid #333;")
            
            self.btn_gerar_ia.setEnabled(False)
            self.btn_gerar_ia.setStyleSheet("background-color: #555; color: #888; font-weight: bold; padding: 10px;")
            self.btn_assistente.setEnabled(False)
            self.btn_assistente.setStyleSheet("background-color: #555; color: #888; font-weight: bold; padding: 10px;")
        else:
            self.txt_tema.setReadOnly(False)
            self.txt_tema.setPlaceholderText(idiomas.tr("txt_tema_placeholder"))
            self.txt_tema.setStyleSheet("") 
            
            self.btn_gerar_ia.setEnabled(True)
            self.btn_gerar_ia.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold; padding: 10px;")
            self.btn_assistente.setEnabled(True)
            self.btn_assistente.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; padding: 10px;")

    # --- O DETETIVE DE CLIQUES (AVISO PARA CONVERSÃO DE CLIENTE) ---
    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        # Agora ele verifica se o clique aconteceu na área interna (viewport) do campo de texto
        if obj == self.txt_tema.viewport() and event.type() == QEvent.MouseButtonPress:
            if "FREE" in self.config.get("license", "FREE"):
                QMessageBox.warning(
                    self, 
                    "Recurso Premium Bloqueado", 
                    "A geração de apresentações por Inteligência Artificial é um recurso VIP!\n\n"
                    "Clique no botão '⚙️ Configurações / Licença' no topo da tela, escolha um dos nossos planos na Loja e libere a IA para trabalhar por você."
                )
                return True # Consome o evento e não deixa o clique entrar na caixa de texto
        return super().eventFilter(obj, event)
            
    def atualizar_preview_real(self, *args):
        if hasattr(self, 'barra_preview_lateral'):
            visivel = self.chk_barra_lateral.isChecked() if hasattr(self, 'chk_barra_lateral') else True
            self.barra_preview_lateral.setVisible(visivel)
        # --- 1. CAPTURAR AS FONTES E CORES ATUAIS ---
        fonte_titulo = self.combo_font_title.currentData()
        fonte_corpo = self.combo_font_body.currentData()
        
        fam_titulo = f"font-family: '{fonte_titulo}';" if self.combo_font_title.currentIndex() != 0 else ""
        fam_corpo = f"font-family: '{fonte_corpo}';" if self.combo_font_body.currentIndex() != 0 else ""
        
        # --- 1. CAPTURAR AS CORES SEPARADAS (ITEM 3) ---
        cor_titulo = f"color: {self.text_color_title.name()};" if self.text_color_title else "color: #1e3c5a;"
        cor_corpo = f"color: {self.text_color_body.name()};" if self.text_color_body else "color: #333;"
        
        # --- 2. ESCALA DO TEXTO ---
        base_px = 10
        if self.chk_text_scale.isChecked():
            new_px = int(base_px * (1 + (self.slider_text_scale.value() / 100.0)))
        else:
            new_px = base_px
            
        import idiomas
        # O truque sujo: Usar HTML no widget nativo para separar Título do Corpo perfeitamente
        html_texto = f"""
        <div style="{fam_titulo} font-size: {new_px + 4}px; font-weight: bold; {cor_titulo} margin-bottom: 5px;">
            {idiomas.tr("lbl_preview_text_title")}
        </div>
        <div style="{fam_corpo} font-size: {new_px}px; {cor_corpo}">
            {idiomas.tr("lbl_preview_text_body")}
        </div>
        """
        self.lbl_preview_text.setText(html_texto)
        self.lbl_preview_text.setStyleSheet("background-color: transparent; border: none;")

        # --- 3. FUNDO DO SLIDE (IMAGEM OU BRANCO) ---
        self.frame_preview.setObjectName("PreviewSlide") # Nomeia o frame para a imagem não bugar
        if self.bg_path:
            bg_limpo = self.bg_path.replace("\\", "/")
            # Usamos border-image com o ID (#PreviewSlide) para esticar a foto no 16:9 perfeito
            self.frame_preview.setStyleSheet(f"#PreviewSlide {{ border-image: url('{bg_limpo}'); border: 2px solid #ccc; border-radius: 8px; }}")
        else:
            self.frame_preview.setStyleSheet("#PreviewSlide { background-color: white; border: 2px solid #ccc; border-radius: 8px; }")

        # --- 4. COR E ESCALA DO CARD/IMAGEM (O QUADRADO) ---
        cor_fundo = self.fill_color.name() if self.fill_color else "#2b5c8f"
        self.lbl_preview_img.setStyleSheet(f"background-color: {cor_fundo}; border-radius: 5px; border: none;")
        
        if self.chk_scale.isChecked():
            base_w, base_h = 100, 100
            fator = self.slider_scale.value() / 100.0 # <--- 0.5 encolhe pela metade, 1.5 cresce 50%
            new_w, new_h = int(base_w * fator), int(base_h * fator)
            centro_x, centro_y = 240, 90 
            self.lbl_preview_img.setGeometry(centro_x - (new_w // 2), centro_y - (new_h // 2), new_w, new_h)
        else:
            self.lbl_preview_img.setGeometry(190, 40, 100, 100)

    def load_pptx(self):
        # --- TRAVA REVERSA (Impede o cara de jogar a IA no lixo sem querer) ---
        if self.pptx_path and not getattr(self, 'is_manual_pptx', True):
            resp = QMessageBox.critical(
                self, 
                "⚠️ ALERTA: Apresentação da IA já carregada!", 
                "VOCÊ JÁ GEROU UMA APRESENTAÇÃO COM A INTELIGÊNCIA ARTIFICIAL!\n\nSe você carregar um arquivo antigo do seu computador agora, VAI APAGAR a apresentação nova que a IA acabou de fazer.\n\nTem CERTEZA ABSOLUTA que quer jogar a da IA no lixo e carregar outro arquivo?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return # Aborta e salva a vida do usuário
        
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar PPTX", self.last_dir, "PowerPoint (*.pptx)")
        if path:
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.pptx_path = path
            self.is_manual_pptx = True # <-- ACIONA O ALARME DE CONFLITO
            self.lbl_pptx.setText(os.path.basename(path))

    def choose_title_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color_title = color
            self.lbl_color_title_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray; border-radius: 12px;")
            self.atualizar_preview_real()

    def choose_body_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color_body = color
            self.lbl_color_body_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray; border-radius: 12px;")
            self.atualizar_preview_real()

    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.lbl_fill_color_indicator.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray; border-radius: 12px;")
            self.atualizar_preview_real() # Avisa o mini-slide imediatamente
            
    def load_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem de Fundo", self.last_dir, "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.bg_path = path
            pixmap = QPixmap(path)
            self.lbl_bg_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_bg_preview.setStyleSheet("border: 1px solid gray;") 
            self.atualizar_preview_real() # Avisa o mini-slide imediatamente
            
    def aplicar_preset(self):
        idx = self.combo_presets.currentIndex()
        if idx == 0: return # Personalizado
            
        if idx == 1: # Corporativo Azul
            self.text_color_title = QColor(30, 60, 90)
            self.text_color_body = QColor(40, 50, 60)
            self.fill_color = QColor(240, 248, 255)
        elif idx == 2: # Dark Mode Clássico
            self.text_color_title = QColor(255, 255, 255)
            self.text_color_body = QColor(220, 220, 220)
            self.fill_color = QColor(45, 45, 45)
        elif idx == 3: # Minimalista Clean
            self.text_color_title = QColor(0, 0, 0)
            self.text_color_body = QColor(50, 50, 50)
            self.fill_color = QColor(255, 255, 255)
            
        self.lbl_color_title_indicator.setStyleSheet(f"background-color: {self.text_color_title.name()}; border: 1px solid gray; border-radius: 12px;")
        self.lbl_color_body_indicator.setStyleSheet(f"background-color: {self.text_color_body.name()}; border: 1px solid gray; border-radius: 12px;")
        self.lbl_fill_color_indicator.setStyleSheet(f"background-color: {self.fill_color.name()}; border: 1px solid gray; border-radius: 12px;")
        self.atualizar_preview_real()
            
    def adicionar_fonte_customizada(self):
        ok, font = QFontDialog.getFont(self)
        if ok:
            nome_fonte = font.family()
            # Adiciona a fonte escolhida nos DOIS dropdowns de uma vez
            for combo in [self.combo_font_title, self.combo_font_body]:
                index = combo.findText(nome_fonte)
                if index == -1:
                    combo.addItem(nome_fonte)
                    novo_index = combo.count() - 1
                    combo.setItemData(novo_index, QFont(nome_fonte), Qt.FontRole)
                    combo.setCurrentIndex(novo_index)
                else:
                    combo.setCurrentIndex(index)

    def gerar_com_ia(self):
        # --- PROTEÇÃO ANTI-CONFLITO DE ARQUIVOS ---
        if self.pptx_path and getattr(self, 'is_manual_pptx', False):
            resp = QMessageBox.warning(
                self, 
                "Atenção: Substituir Arquivo?", 
                "Você já carregou uma apresentação pronta no aplicativo (Botão 1).\n\nSe você usar a IA agora, a apresentação que você carregou será descartada e substituída por uma nova.\n\nDeseja descartar a apresentação atual e continuar com a IA?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return # Aborta e deixa o cara quieto com o arquivo dele
            else:
                # Limpa a trava e a tela para a IA trabalhar do zero
                self.pptx_path = None
                self.is_manual_pptx = False
                self.lbl_pptx.setText("Nenhum arquivo selecionado")
                
        licensa = self.config.get("license", "FREE")
        
        if licensa == "FREE":
            QMessageBox.warning(self, "Recurso Premium", "A geração por IA é um recurso Premium.")
            return

        tema = self.txt_tema.toPlainText().strip()
        if not tema:
            QMessageBox.warning(self, "Aviso", "Por favor, introduza o tema primeiro!")
            return
        
        # Faxina automática: esvazia o lixo da sessão anterior antes de começar a nova
        self.limpar_cache_sessao_antigo()
            
        # O GOLPE DO IDIOMA: Injeta uma regra absoluta sem sujar a variável "tema" que vai pro histórico
        tema_para_ia = f"{tema}\n\n[CRITICAL RULE: You MUST generate the entire presentation, all text, and the speaker script strictly in the EXACT SAME LANGUAGE as the topic requested above.]"
        
        api_key_usuario = self.config.get("api_key") if licensa == "BYOK (Sua Chave)" else None
        modelo = self.config.get("model", "")
        
        if not modelo or "Busque" in modelo:
            QMessageBox.warning(self, "Aviso", "Nenhum modelo de IA configurado! Vá em 'Configurações', clique em 'Buscar Modelos' e selecione um da lista antes de gerar a apresentação.")
            return
            
        sucesso_check, msg_check = motor_ia.testar_conectividade(api_key_usuario)
        if not sucesso_check:
            QMessageBox.critical(self, "Bloqueio na IA", f"Conexão recusada:\n\n{msg_check}")
            return
            
        from PySide6.QtCore import QEventLoop

        try:
            progress = QProgressDialog("Inicializando Motor...", "Cancelar", 0, 100, self)
            progress.setWindowTitle("Gerando Apresentação")
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # Trava os botões para ele não clicar duas vezes sem querer
            self.btn_gerar_ia.setEnabled(False)
            self.btn_historico.setEnabled(False)

            # Inicia o Trabalho Paralelo entregando o tema blindado com a regra de idioma
            worker = WorkerIAGerador(tema_para_ia, self.config)
            # Liga o progresso da thread direto na barra da tela
            worker.progresso.connect(lambda v, t: (progress.setValue(v), progress.setLabelText(t)))
            progress.canceled.connect(worker.requestInterruption)
            
            loop = QEventLoop()
            worker.concluido.connect(loop.quit)
            worker.start()
            
            # A MÁGICA: A UI não congela mais, e o código espera o Worker terminar aqui!
            loop.exec() 
            
            self.btn_gerar_ia.setEnabled(True)
            self.btn_historico.setEnabled(True)
            progress.close()

            if worker.isInterruptionRequested(): return
                
            if worker.erro_msg:
                QMessageBox.critical(self, "Falha na IA", f"Erro:\n\n{worker.erro_msg}")
                return
                
            roteiro = worker.roteiro
            slide_images_dict = worker.slide_images_dict

            # Salva o roteiro em cache para você poder testar sem gastar API
            try:
                with open(CACHE_ROTEIRO_FILE, "w", encoding="utf-8") as f_cache:
                    json.dump({"roteiro": roteiro, "slide_images": slide_images_dict, "tema": tema}, f_cache, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erro ao salvar cache: {e}")

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
                
            # Garante que se o usuário pediu [FORMA: ...] mas a IA gerou sem ela, convertemos o slide adequado
            import re
            match_forma = re.search(r"\[FORMA:\s*(\w+)\s*\|\s*ITENS:\s*(\d+)\]", tema)
            if match_forma and not any("smartart" in s for s in roteiro):
                tipo_f = match_forma.group(1)
                qtd_f = int(match_forma.group(2))
                for sl in roteiro:
                    if sl.get("tipo_layout") in ["smartart", "cards", "padrao"] or "topicos" in sl:
                        sl["tipo_layout"] = "smartart"
                        topicos_existentes = [t.get("titulo", "") for t in sl.get("topicos", [])]
                        while len(topicos_existentes) < qtd_f:
                            topicos_existentes.append(f"Item {len(topicos_existentes) + 1}")
                        sl["smartart"] = {
                            "tipo": tipo_f,
                            "centro": sl.get("titulo", "NÚCLEO"),
                            "itens": topicos_existentes[:qtd_f]
                        }
                        break

            # --- MODAL 2: REVISÃO GRANULAR DE CARDS E FORMAS ---
            dialog_revisor = RevisorElementosDialog(roteiro, self)
            if dialog_revisor.elementos:
                dialog_revisor.exec()

            prs = Presentation()
            prs.slide_width = 12192000
            prs.slide_height = 6858000

            for i, slide_data in enumerate(roteiro):
                slide = prs.slides.add_slide(prs.slide_layouts[6]) 
                
                barra_lateral = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, int(prs.slide_width * 0.02), prs.slide_height)
                barra_lateral.fill.solid()
                barra_lateral.fill.fore_color.rgb = RGBColor(43, 92, 143) 
                barra_lateral.line.fill.background() 
                
                barra_lateral.name = "BarraLateral_Vega" # ETIQUETA PARA CONTROLE DE LIGA/DESLIGA

                # --- LÓGICA DINÂMICA DE LARGURA (ITEM 3) ---
                # --- LEITURA DO DESIGN DA IA ---
                tipo_layout = slide_data.get("tipo_layout", "padrao")
                # Se for cards, destaque ou SmartArt, não coloca foto para não esmagar o desenho
                tem_smartart = "smartart" in slide_data
                tem_imagem = i in selected_images and selected_images[i] != "NONE" and tipo_layout == "padrao" and not tem_smartart
                largura_texto = int(prs.slide_width * 0.45) if tem_imagem else int(prs.slide_width * 0.88)

                # --- CAIXA DE TÍTULO (ITEM 4 - Esticado no slide) ---
                largura_titulo = int(prs.slide_width * 0.88) # Ignora a lateral e abraça 88% do topo
                top_titulo = int(prs.slide_height * 0.35) if tipo_layout == "destaque" else int(prs.slide_height * 0.06)
                altura_titulo = int(prs.slide_height * 0.30) if tipo_layout == "destaque" else int(prs.slide_height * 0.15)
                
                title_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), top_titulo, largura_titulo, altura_titulo)
                title_box.name = "TitleBox_Vega"
                tf_title = title_box.text_frame
                tf_title.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP # ALINHA NO TETO
                tf_title.word_wrap = True
                tf_title.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE 
                
                p_title = tf_title.paragraphs[0]
                p_title.text = slide_data.get("titulo", "").upper()
                p_title.font.bold = True
                p_title.font.size = Pt(50) if tipo_layout == "destaque" else Pt(28)
                p_title.font.color.rgb = RGBColor(30, 60, 90)

                # --- O MOTOR DE LAYOUTS ---
                # 1. SMARTART TEM PRIORIDADE TOTAL SOBRE QUALQUER OUTRO LAYOUT
                if "smartart" in slide_data:
                    cor_forma_primaria = RGBColor(43, 92, 143)
                    cor_forma_secundaria = RGBColor(245, 247, 250)
                    MotorFormasVega.desenhar_forma(slide, prs, slide_data["smartart"], cor_forma_primaria, cor_forma_secundaria)

                elif tipo_layout == "cards" and "topicos" in slide_data:
                    num_cards = min(len(slide_data["topicos"]), 3)
                    if num_cards > 0:
                        largura_card = int(largura_texto / num_cards) - int(prs.slide_width * 0.02)
                        altura_card = int(prs.slide_height * 0.55)
                        top_card = int(prs.slide_height * 0.24)
                        left_inicial = int(prs.slide_width * 0.06)

                        for j, topico in enumerate(slide_data["topicos"][:num_cards]):
                            card_left = left_inicial + (j * (largura_card + int(prs.slide_width * 0.02)))
                            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, top_card, largura_card, altura_card)
                            shape.fill.solid()
                            shape.fill.fore_color.rgb = RGBColor(245, 247, 250)
                            shape.line.color.rgb = RGBColor(200, 210, 220)

                            tf_card = shape.text_frame
                            tf_card.word_wrap = True
                            tf_card.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                            
                            p_card = tf_card.paragraphs[0]
                            icone = topico.get("icone", "📌")
                            p_card.text = f"{icone} {topico.get('titulo', '')}"
                            p_card.font.bold = True
                            p_card.font.size = Pt(20)
                            p_card.font.color.rgb = RGBColor(43, 92, 143)

                            # AQUI: Aplica a escala definida no Revisor pelo usuário
                            escala_card = topico.get("escala_texto", 0)
                            fator_card = 1.0 + (escala_card / 100.0)
                            tam_fonte_corpo = max(8, int(14 * fator_card))

                            p_card_texto = tf_card.add_paragraph()
                            p_card_texto.text = topico.get("texto", "")
                            p_card_texto.font.size = Pt(tam_fonte_corpo)
                            p_card_texto.font.color.rgb = RGBColor(60, 60, 60)
                            p_card_texto.space_before = Pt(10)
                            
                elif tipo_layout == "grafico" and "dados_grafico" in slide_data:
                    dados = slide_data.get("dados_grafico", {})
                    categorias = dados.get("categorias", [])
                    valores = dados.get("valores", [])
                    nome_serie_raw = dados.get("nome_serie", "Dados")
                    if isinstance(nome_serie_raw, list):
                        nome_serie = str(nome_serie_raw[0]) if nome_serie_raw else "Dados"
                    else:
                        nome_serie = str(nome_serie_raw)

                    if categorias and valores and len(categorias) == len(valores):
                        chart_data = CategoryChartData()
                        chart_data.categories = categorias
                        chart_data.add_series(nome_serie, valores)

                        x, y = int(prs.slide_width * 0.06), int(prs.slide_height * 0.24)
                        cx, cy = int(prs.slide_width * 0.88), int(prs.slide_height * 0.60)
                        
                        slide.shapes.add_chart(
                            XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
                        )

                elif tipo_layout != "destaque":
                    # Layout Padrão (Agora com suporte a Bullet Points e Ícones da IA)
                    body_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.24), largura_texto, int(prs.slide_height * 0.60))
                    body_box.name = "BodyBox_Vega" # Etiqueta invisível do corpo
                    tf_body = body_box.text_frame
                    tf_body.word_wrap = True
                    tf_body.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE 

                    texto_base = slide_data.get("texto", "").strip()
                    if texto_base:
                        p_body = tf_body.paragraphs[0]
                        p_body.text = texto_base
                        p_body.font.size = Pt(18)
                        p_body.space_after = Pt(14)

                    if "topicos" in slide_data:
                        for idx, topico in enumerate(slide_data["topicos"]):
                            p_topic = tf_body.add_paragraph() if texto_base else (tf_body.paragraphs[0] if idx == 0 else tf_body.add_paragraph())
                            icone = topico.get("icone", "•")
                            p_topic.text = f"{icone} {topico.get('titulo', '')}: {topico.get('texto', '')}"
                            p_topic.font.size = Pt(16)
                            p_topic.level = 0
                            p_topic.space_after = Pt(10)

                # --- INSERÇÃO DA IMAGEM ---
                if tem_imagem:
                    try:
                        img_left = int(prs.slide_width * 0.54)
                        img_top = int(prs.slide_height * 0.24) # Desceu de 0.1 para 0.22 para fugir do título
                        img_max_w = int(prs.slide_width * 0.42)
                        img_max_h = int(prs.slide_height * 0.68)

                        pic = slide.shapes.add_picture(selected_images[i], img_left, img_top)
                        ratio = min(img_max_w / pic.width, img_max_h / pic.height)

                        pic.width = int(pic.width * ratio)
                        pic.height = int(pic.height * ratio)
                        pic.left = img_left + int((img_max_w - pic.width) / 2)
                        pic.top = img_top + int((img_max_h - pic.height) / 2)
                    except: pass
                    
                # --- ANOTAÇÕES DO APRESENTADOR (SUGESTÃO 2 com trava) ---
                if self.chk_notes.isChecked():
                    notas_palestrante = slide_data.get("roteiro_apresentador", "").strip()
                    if notas_palestrante:
                        notes_slide = slide.notes_slide
                        text_frame = notes_slide.notes_text_frame
                        text_frame.text = f"📢 ROTEIRO DO APRESENTADOR:\n\n{notas_palestrante}"

            temp_path = TEMP_PPTX_FILE
            prs.save(temp_path)
            
            # --- SALVANDO O PPTX FÍSICO NO HISTÓRICO ---
            try:
                import shutil
                from datetime import datetime
                if not os.path.exists(PASTA_HISTORICO_PPTX):
                    os.makedirs(PASTA_HISTORICO_PPTX)
                
                # Cria um nome limpo e seguro pro arquivo
                tema_limpo = "".join([c for c in tema if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:30]
                data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arq = f"{data_str}_{tema_limpo.replace(' ', '_')}.pptx"
                caminho_salvo = os.path.join(PASTA_HISTORICO_PPTX, nome_arq)
                
                shutil.copy2(temp_path, caminho_salvo)
                
                # Salva a referência no JSON blindado
                historico = []
                if os.path.exists(HISTORICO_JSON_FILE):
                    with open(HISTORICO_JSON_FILE, "r", encoding="utf-8") as f:
                        historico = json.load(f)
                        
                # Guarda também o roteiro e fotos em arquivo JSON correspondente para permitir re-edição offline completa
                caminho_dados_json = caminho_salvo.replace(".pptx", "_dados.json")
                try:
                    with open(caminho_dados_json, "w", encoding="utf-8") as f_d:
                        json.dump({"roteiro": roteiro, "slide_images": slide_images_dict, "tema": tema}, f_d, ensure_ascii=False, indent=2)
                except:
                    caminho_dados_json = None

                historico.append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "tema": tema,
                    "caminho": caminho_salvo,
                    "dados_json": caminho_dados_json
                })
                
                # MANTÉM APENAS OS 5 ÚLTIMOS E FAZ A FAXINA FÍSICA NO HD
                while len(historico) > 5:
                    removido = historico.pop(0)
                    try:
                        if os.path.exists(removido["caminho"]):
                            os.remove(removido["caminho"])
                    except: pass
                    
                with open(HISTORICO_JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(historico, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Erro no backup do PPTX: {e}")
            
            try:
                for caminhos in slide_images_dict.values():
                    for c in caminhos:
                        if os.path.exists(c): os.remove(c)
            except: pass

            self.pptx_path = temp_path
            self.lbl_pptx.setText("✨ Apresentação carregada e pronta para edição final!")
            
            try:
                import idiomas
                editor = self.config.get("app_editor", idiomas.tr("editor_opt_system"))
                caminho_absoluto = os.path.abspath(temp_path)
                
                if editor == idiomas.tr("editor_opt_none") or "Nenhum" in editor or "None" in editor:
                    if os.name == 'nt':
                        subprocess.Popen(f'explorer /select,"{caminho_absoluto}"')
                    else:
                        subprocess.Popen(['open', '-R', caminho_absoluto] if sys.platform == 'darwin' else ['xdg-open', os.path.dirname(caminho_absoluto)])
                elif editor == "Microsoft PowerPoint":
                    subprocess.Popen(["powerpnt", caminho_absoluto], shell=True)
                elif editor == "LibreOffice Impress":
                    subprocess.Popen(["soffice", "--impress", caminho_absoluto], shell=True)
                else:
                    try:
                        if os.name == 'nt': os.startfile(caminho_absoluto)
                        else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', caminho_absoluto])
                    except Exception:
                        # Se o Windows não souber o que é PPTX, não fazemos feio, abrimos a pasta.
                        if os.name == 'nt':
                            subprocess.Popen(f'explorer /select,"{caminho_absoluto}"')
                        else:
                            subprocess.Popen(['open', '-R', caminho_absoluto] if sys.platform == 'darwin' else ['xdg-open', os.path.dirname(caminho_absoluto)])
                        
                        import idiomas
                        QMessageBox.information(self, idiomas.tr("msg_sys_editor_fail_tit"), idiomas.tr("msg_sys_editor_fail_msg"))
            except: pass

        except Exception as e:
            progress.close()
            erro_msg = traceback.format_exc()
            
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"ERRO CRÍTICO NA IA:\n{erro_msg}")
            
            QMessageBox.critical(self, "Falha Fatal", f"O aplicativo encontrou um erro e gerou um log.\n\nSalvo em:\n{LOG_FILE}\n\nErro: {str(e)}")
            
    def limpar_cache_sessao_antigo(self):
        """Limpa a pasta temporária de imagens para nunca acumular lixo no computador do cliente."""
        try:
            if os.path.exists(PASTA_CACHE_SESSAO):
                for arq in os.listdir(PASTA_CACHE_SESSAO):
                    caminho_arq = os.path.join(PASTA_CACHE_SESSAO, arq)
                    if os.path.isfile(caminho_arq):
                        os.remove(caminho_arq)
        except Exception as e:
            print(f"Aviso de limpeza de sessão: {e}")

    def retestar_ultimo_roteiro(self):
        """Carrega o último roteiro gerado do HD sem chamar nenhuma API de IA."""
        if not os.path.exists(CACHE_ROTEIRO_FILE):
            QMessageBox.warning(self, "Sem Cache", "Nenhum roteiro recente em cache. Gere uma apresentação com a IA primeiro.")
            return

        try:
            with open(CACHE_ROTEIRO_FILE, "r", encoding="utf-8") as f_cache:
                dados_cache = json.load(f_cache)
            roteiro = dados_cache.get("roteiro", [])
            slide_images = dados_cache.get("slide_images", {})
            slide_images_dict = {int(k): v for k, v in slide_images.items()}
            tema = dados_cache.get("tema", self.txt_tema.toPlainText())

            if not roteiro:
                QMessageBox.warning(self, "Cache Vazio", "O arquivo de cache não contém slides.")
                return

            # Se as imagens foram limpas ou apagadas, baixa o conjunto daquela rodada
            fotos_faltando = False
            for s_idx, caminhos in slide_images_dict.items():
                if not any(os.path.exists(c) for c in caminhos):
                    fotos_faltando = True
                    break

            if fotos_faltando:
                for s_idx, slide_data in enumerate(roteiro):
                    kw = slide_data.get("palavra_chave_imagem", "")
                    if kw:
                        novos_caminhos = motor_ia.baixar_imagem_pexels(kw, s_idx)
                        if novos_caminhos:
                            slide_images_dict[s_idx] = novos_caminhos

            self._processar_roteiro_para_pptx(roteiro, slide_images_dict, tema)
        except Exception as e:
            QMessageBox.critical(self, "Erro no Teste", f"Falha ao carregar cache:\n{str(e)}")

    def _processar_roteiro_para_pptx(self, roteiro, slide_images_dict, tema):
        """Abre os modais e compila os slides sem encavalar formas ou ignorar fotos."""
        selected_images = {}
        if slide_images_dict:
            dialog = ImageSelectionDialog(slide_images_dict, roteiro, self)
            if dialog.exec() == QDialog.Accepted:
                selected_images = dialog.selected_images
            else:
                return

        # 1. Injeção estrita da forma pedida (APENAS se o usuário digitou a tag e a IA esqueceu)
        import re
        match_forma = re.search(r"\[FORMA:\s*(\w+)\s*\|\s*ITENS:\s*(\d+)\]", tema)
        if match_forma and not any("smartart" in s for s in roteiro):
            tipo_f = match_forma.group(1)
            qtd_f = int(match_forma.group(2))
            for sl in roteiro:
                if sl.get("tipo_layout") in ["smartart", "cards", "padrao"] or "topicos" in sl:
                    sl["tipo_layout"] = "smartart"
                    topicos = [t.get("titulo", "") for t in sl.get("topicos", [])]
                    while len(topicos) < qtd_f:
                        topicos.append(f"Item {len(topicos) + 1}")
                    sl["smartart"] = {
                        "tipo": tipo_f,
                        "centro": sl.get("titulo", "NÚCLEO"),
                        "itens": topicos[:qtd_f]
                    }
                    break

        # 2. Modal de Revisão
        dialog_revisor = RevisorElementosDialog(roteiro, self)
        if dialog_revisor.elementos:
            dialog_revisor.exec()

        # 3. Montagem do PPTX
        prs = Presentation()
        prs.slide_width = 12192000
        prs.slide_height = 6858000

        for i, slide_data in enumerate(roteiro):
            slide = prs.slides.add_slide(prs.slide_layouts[6])

            barra_lateral = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, int(prs.slide_width * 0.02), prs.slide_height)
            barra_lateral.fill.solid()
            barra_lateral.fill.fore_color.rgb = RGBColor(43, 92, 143)
            barra_lateral.line.fill.background()
            barra_lateral.name = "BarraLateral_Vega"

            tipo_layout = slide_data.get("tipo_layout", "padrao")
            tem_smartart = ("smartart" in slide_data) and bool(slide_data["smartart"].get("itens"))
            # SÓ TEM IMAGEM SE O SLIDE FOR PADRÃO E NÃO TIVER SMARTART
            tem_imagem = (i in selected_images) and (selected_images[i] != "NONE") and (tipo_layout == "padrao") and (not tem_smartart)
            largura_texto = int(prs.slide_width * 0.45) if tem_imagem else int(prs.slide_width * 0.88)

            # Título do Slide
            largura_titulo = int(prs.slide_width * 0.88)
            top_titulo = int(prs.slide_height * 0.35) if tipo_layout == "destaque" else int(prs.slide_height * 0.06)
            altura_titulo = int(prs.slide_height * 0.30) if tipo_layout == "destaque" else int(prs.slide_height * 0.15)

            title_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), top_titulo, largura_titulo, altura_titulo)
            title_box.name = "TitleBox_Vega"
            tf_title = title_box.text_frame
            tf_title.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
            tf_title.word_wrap = True
            tf_title.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            p_title = tf_title.paragraphs[0]
            p_title.text = slide_data.get("titulo", "").upper()
            p_title.font.bold = True
            p_title.font.size = Pt(50) if tipo_layout == "destaque" else Pt(28)
            p_title.font.color.rgb = RGBColor(30, 60, 90)

            # DESENHO DOS CORPOS / LAYOUTS
            if tem_smartart:
                # 1. FORMA REAL (SÓ DESENHA SE REALMENTE EXISTIR SMARTART COM ITENS)
                cor_forma_primaria = RGBColor(43, 92, 143)
                cor_forma_secundaria = RGBColor(245, 247, 250)
                MotorFormasVega.desenhar_forma(slide, prs, slide_data["smartart"], cor_forma_primaria, cor_forma_secundaria)

            elif tipo_layout == "cards" and "topicos" in slide_data:
                num_cards = min(len(slide_data["topicos"]), 3)
                if num_cards > 0:
                    largura_card = int(largura_texto / num_cards) - int(prs.slide_width * 0.02)
                    altura_card = int(prs.slide_height * 0.55)
                    top_card = int(prs.slide_height * 0.24)
                    left_inicial = int(prs.slide_width * 0.06)

                    for j, topico in enumerate(slide_data["topicos"][:num_cards]):
                        card_left = left_inicial + (j * (largura_card + int(prs.slide_width * 0.02)))
                        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, top_card, largura_card, altura_card)
                        shape.fill.solid()
                        shape.fill.fore_color.rgb = RGBColor(245, 247, 250)
                        shape.line.color.rgb = RGBColor(200, 210, 220)

                        tf_card = shape.text_frame
                        tf_card.word_wrap = True
                        tf_card.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                        p_card = tf_card.paragraphs[0]
                        icone = topico.get("icone", "📌")
                        p_card.text = f"{icone} {topico.get('titulo', '')}"
                        p_card.font.bold = True
                        p_card.font.size = Pt(20)
                        p_card.font.color.rgb = RGBColor(43, 92, 143)

                        escala_card = topico.get("escala_texto", 0)
                        fator_card = 1.0 + (escala_card / 100.0)
                        tam_fonte_corpo = max(8, int(14 * fator_card))

                        p_card_texto = tf_card.add_paragraph()
                        p_card_texto.text = topico.get("texto", "")
                        p_card_texto.font.size = Pt(tam_fonte_corpo)
                        p_card_texto.font.color.rgb = RGBColor(60, 60, 60)
                        p_card_texto.space_before = Pt(10)

            elif tipo_layout == "grafico" and "dados_grafico" in slide_data:
                dados = slide_data.get("dados_grafico", {})
                categorias = dados.get("categorias", [])
                valores = dados.get("valores", [])
                nome_serie_raw = dados.get("nome_serie", "Dados")
                nome_serie = str(nome_serie_raw[0]) if isinstance(nome_serie_raw, list) else str(nome_serie_raw)

                if categorias and valores and len(categorias) == len(valores):
                    chart_data = CategoryChartData()
                    chart_data.categories = categorias
                    chart_data.add_series(nome_serie, valores)
                    x, y = int(prs.slide_width * 0.06), int(prs.slide_height * 0.24)
                    cx, cy = int(prs.slide_width * 0.88), int(prs.slide_height * 0.60)
                    slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data)

            elif tipo_layout != "destaque":
                # Layout Padrão de Texto
                body_box = slide.shapes.add_textbox(int(prs.slide_width * 0.06), int(prs.slide_height * 0.24), largura_texto, int(prs.slide_height * 0.60))
                body_box.name = "BodyBox_Vega"
                tf_body = body_box.text_frame
                tf_body.word_wrap = True
                tf_body.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

                texto_base = slide_data.get("texto", "").strip()
                if texto_base:
                    p_body = tf_body.paragraphs[0]
                    p_body.text = texto_base
                    p_body.font.size = Pt(18)
                    p_body.space_after = Pt(14)

                if "topicos" in slide_data:
                    for idx, topico in enumerate(slide_data["topicos"]):
                        p_topic = tf_body.add_paragraph() if texto_base else (tf_body.paragraphs[0] if idx == 0 else tf_body.add_paragraph())
                        icone = topico.get("icone", "•")
                        p_topic.text = f"{icone} {topico.get('titulo', '')}: {topico.get('texto', '')}"
                        p_topic.font.size = Pt(16)
                        p_topic.level = 0
                        p_topic.space_after = Pt(10)

            # Inserção da Imagem no Slide Padrão
            if tem_imagem:
                try:
                    img_left = int(prs.slide_width * 0.54)
                    img_top = int(prs.slide_height * 0.24)
                    img_max_w = int(prs.slide_width * 0.42)
                    img_max_h = int(prs.slide_height * 0.68)
                    pic = slide.shapes.add_picture(selected_images[i], img_left, img_top)
                    ratio = min(img_max_w / pic.width, img_max_h / pic.height)
                    pic.width = int(pic.width * ratio)
                    pic.height = int(pic.height * ratio)
                    pic.left = img_left + int((img_max_w - pic.width) / 2)
                    pic.top = img_top + int((img_max_h - pic.height) / 2)
                except Exception as e:
                    print(f"Erro ao inserir imagem: {e}")

            # Anotações do Apresentador
            if self.chk_notes.isChecked():
                notas = slide_data.get("roteiro_apresentador", "").strip()
                if notas:
                    slide.notes_slide.notes_text_frame.text = f"📢 ROTEIRO DO APRESENTADOR:\n\n{notas}"

        temp_path = TEMP_PPTX_FILE
        prs.save(temp_path)
        self.pptx_path = temp_path
        self.lbl_pptx.setText("✨ Apresentação carregada e pronta para edição final!")

        # Abre no editor configurado
        try:
            import idiomas
            editor = self.config.get("app_editor", idiomas.tr("editor_opt_system"))
            caminho_absoluto = os.path.abspath(temp_path)
            if editor == "Microsoft PowerPoint":
                subprocess.Popen(["powerpnt", caminho_absoluto], shell=True)
            else:
                os.startfile(caminho_absoluto) if os.name == 'nt' else subprocess.Popen(['xdg-open', caminho_absoluto])
        except Exception:
            pass
            
    def checar_atalho_forma(self):
        texto = self.txt_tema.toPlainText()
        if "/forma" in texto:
            # Remove o gatilho "/forma" da caixa sem disparar loop de eventos
            self.txt_tema.blockSignals(True)
            novo_texto = texto.replace("/forma", "").strip()
            self.txt_tema.setPlainText(novo_texto)
            self.txt_tema.blockSignals(False)
            
            # Abre o seletor visual na mesma hora
            self.abrir_seletor_forma()

    def abrir_seletor_forma(self):
        dialog = DialogSeletorForma(self)
        if dialog.exec() == QDialog.Accepted and dialog.forma_selecionada:
            texto_atual = self.txt_tema.toPlainText().strip()
            espaco = " " if texto_atual else ""
            self.txt_tema.setText(f"{texto_atual}{espaco}{dialog.forma_selecionada}")
            from PySide6.QtGui import QTextCursor
            cursor = self.txt_tema.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.txt_tema.setTextCursor(cursor)
            
    def abrir_dialogo_assistente(self):
            licensa = self.config.get("license", "FREE")
            if licensa == "FREE":
                QMessageBox.warning(self, "Recurso Premium", "O Assistente de IA é um recurso Premium.")
                return
    
            dialog = AssistenteIADialog(self)
            if dialog.exec() == QDialog.Accepted:
                # 1. Joga o texto perfeitamente estruturado na caixa para o usuário ver e aprender
                self.txt_tema.setText(dialog.prompt_final)
                
                # 2. Já engatilha o processo automático para ele não precisar clicar em nada mais
                self.gerar_com_ia()
            
    def abrir_historico(self):
        if not os.path.exists(HISTORICO_JSON_FILE):
            QMessageBox.information(self, "Histórico Vazio", "Você ainda não tem apresentações salvas localmente.")
            return

        try:
            with open(HISTORICO_JSON_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except:
            historico = []

        historico_valido = []
        for h in historico:
            caminho_salvo = h.get("caminho", "")
            if not os.path.exists(caminho_salvo):
                nome_arquivo = os.path.basename(caminho_salvo)
                caminho_tentativa = os.path.join(PASTA_HISTORICO_PPTX, nome_arquivo)
                if os.path.exists(caminho_tentativa):
                    h["caminho"] = caminho_tentativa
                    caminho_salvo = caminho_tentativa

            if os.path.exists(caminho_salvo):
                historico_valido.append(h)

        historico_valido = historico_valido[-5:]
        if not historico_valido:
            QMessageBox.information(self, "Histórico Vazio", "Nenhuma apresentação física foi encontrada. Gere uma nova!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(idiomas.tr("recup_titulo"))
        dialog.setFixedSize(620, 380)

        lay = QVBoxLayout(dialog)
        lbl = QLabel(idiomas.tr("recup_instrucao"))
        lbl.setStyleSheet("font-size: 13px; color: white;")
        lay.addWidget(lbl)

        lista_ui = QListWidget()
        lista_ui.setStyleSheet("background-color: #222; border: 1px solid #444; border-radius: 6px; padding: 6px; font-size: 13px; color: #eee;")
        lista_ui.setWordWrap(True)

        itens_invertidos = list(reversed(historico_valido))
        for item in itens_invertidos:
            lista_ui.addItem(f"📅 {item['data']}\n📝 {item.get('tema', 'Tema Desconhecido')}\n")

        lista_ui.setCurrentRow(0)
        lista_ui.itemDoubleClicked.connect(dialog.accept)
        lay.addWidget(lista_ui)

        hbox_btn = QHBoxLayout()
        btn_cancel = QPushButton(idiomas.tr("recup_btn_cancelar"))
        btn_cancel.clicked.connect(dialog.reject)

        btn_ok = QPushButton(idiomas.tr("recup_btn_abrir"))
        btn_ok.setDefault(True)
        btn_ok.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        btn_ok.clicked.connect(dialog.accept)

        hbox_btn.addStretch()
        hbox_btn.addWidget(btn_cancel)
        hbox_btn.addWidget(btn_ok)
        lay.addLayout(hbox_btn)

        if dialog.exec() == QDialog.Accepted and lista_ui.currentRow() >= 0:
            item_escolhido = itens_invertidos[lista_ui.currentRow()]
            caminho_json = item_escolhido.get("dados_json")
            tema_recup = item_escolhido.get("tema", "")
            self.txt_tema.setPlainText(tema_recup)

            # 1. Tenta carregar o JSON específico arquivado ou o cache da última sessão
            dados = None
            if caminho_json and os.path.exists(caminho_json):
                try:
                    with open(caminho_json, "r", encoding="utf-8") as f_d:
                        dados = json.load(f_d)
                except Exception:
                    dados = None

            if not dados and os.path.exists(CACHE_ROTEIRO_FILE):
                try:
                    with open(CACHE_ROTEIRO_FILE, "r", encoding="utf-8") as f_c:
                        dados = json.load(f_c)
                except Exception:
                    dados = None

            # 2. Se achou os dados de roteiro, reabre o pipeline completo (Imagens + Revisor) sem IA
            if dados and dados.get("roteiro"):
                try:
                    roteiro = dados.get("roteiro", [])
                    raw_images = dados.get("slide_images", {})
                    slide_images_dict = {int(k): v for k, v in raw_images.items()}

                    # Garante que as imagens estejam baixadas no disco
                    for s_idx, slide_data in enumerate(roteiro):
                        kw = slide_data.get("palavra_chave_imagem", "")
                        caminhos = slide_images_dict.get(s_idx, [])
                        if kw and (not caminhos or not any(os.path.exists(c) for c in caminhos)):
                            novas = motor_ia.baixar_imagem_pexels(kw, s_idx)
                            if novas:
                                slide_images_dict[s_idx] = novas

                    self._processar_roteiro_para_pptx(roteiro, slide_images_dict, tema_recup)
                    return
                except Exception as e:
                    print(f"Erro ao reabrir modais: {e}")

            # 3. Fallback só se realmente não houver dado nenhum salvo
            caminho_pptx = item_escolhido.get("caminho", "")
            if caminho_pptx and os.path.exists(caminho_pptx):
                self.pptx_path = caminho_pptx
                self.lbl_pptx.setText(f"📁 Recuperado: {os.path.basename(caminho_pptx)}")

    def process_and_save(self):
        if not self.pptx_path:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma apresentação primeiro.")
            return

        tema_sugerido = self.txt_tema.toPlainText().strip()
        if tema_sugerido:
            nome_base = "".join([c for c in tema_sugerido if c.isalnum() or c in (' ', '_', '-')]).rstrip()[:30].replace(' ', '_')
            nome_arquivo_padrao = f"{nome_base}.pptx" if nome_base else "apresentacao_final.pptx"
        else:
            nome_arquivo_padrao = "apresentacao_final.pptx"

        pasta_padrao = self.last_dir if self.last_dir and os.path.exists(self.last_dir) else base_dir
        caminho_inicial = os.path.join(pasta_padrao, nome_arquivo_padrao)

        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Apresentação Como", caminho_inicial, "PowerPoint (*.pptx)")
        if not save_path:
            return
        
        self.last_dir = os.path.dirname(save_path)
        self.save_config()

        try:
            prs = Presentation(self.pptx_path)
            title_rgb = RGBColor(self.text_color_title.red(), self.text_color_title.green(), self.text_color_title.blue()) if self.text_color_title else None
            body_rgb = RGBColor(self.text_color_body.red(), self.text_color_body.green(), self.text_color_body.blue()) if self.text_color_body else None
            fill_rgb = RGBColor(self.fill_color.red(), self.fill_color.green(), self.fill_color.blue()) if self.fill_color else None

            for slide in prs.slides:
                # --- 1. CONTROLE DE LIGA/DESLIGA DA BARRA LATERAL (ITEM 1) ---
                shapes_para_remover = []
                for shape in slide.shapes:
                    # Identifica a barra tanto pela etiqueta nova quanto pelo formato antigo
                    is_barra = (shape.name == "BarraLateral_Vega") or (shape.left == 0 and shape.top == 0 and shape.width <= int(prs.slide_width * 0.03) and shape.height == prs.slide_height)
                    if not self.chk_barra_lateral.isChecked() and is_barra:
                        shapes_para_remover.append(shape)
                        
                for s_rem in shapes_para_remover:
                    slide.shapes._spTree.remove(s_rem._element)

                # --- 2. PROCESSAMENTO DAS OUTRAS FORMAS ---
                for shape in slide.shapes:
                    is_barra = (shape.name == "BarraLateral_Vega") or (shape.left == 0 and shape.top == 0 and shape.width <= int(prs.slide_width * 0.03) and shape.height == prs.slide_height)
                    if is_barra:
                        continue # Pula a barra lateral para não estragar a cor dela caso escolha cor de card!
                        
                    if self.chk_scale.isChecked() and shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                        scale = self.slider_scale.value() / 100.0 # <--- ESCALA BIDIRECIONAL (ITEM 2)
                        nw, nh = int(shape.width * scale), int(shape.height * scale)
                        shape.left += int((shape.width - nw) / 2)
                        shape.top += int((shape.height - nh) / 2)
                        shape.width, shape.height = nw, nh

                    if hasattr(shape, "fill") and fill_rgb:
                        try:
                            if shape.fill.type == MSO_FILL.SOLID: shape.fill.fore_color.rgb = fill_rgb
                        except: pass
                    
                    if shape.has_text_frame:
                        shape.text_frame.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                # Identifica quem é título e quem é corpo/card
                                is_title = (shape.name == "TitleBox_Vega")
                                if run.font.size:
                                    if run.font.size >= Pt(24): is_title = True
                                elif paragraph.font.size and paragraph.font.size >= Pt(24):
                                    is_title = True
                                    
                                # APLICA A COR SEPARADA (ITEM 3)
                                cor_rgb = title_rgb if is_title else body_rgb
                                if cor_rgb:
                                    run.font.color.rgb = cor_rgb
                                    
                                # APLICA A FONTE SEPARADA
                                fonte_escolhida = self.combo_font_title.currentText() if is_title else self.combo_font_body.currentText()
                                if fonte_escolhida != "Padrão do Tema":
                                    run.font.name = fonte_escolhida
                                
                                if self.chk_text_scale.isChecked():
                                    percentual = self.slider_text_scale.value()
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
                import idiomas
                editor = self.config.get("app_editor", idiomas.tr("editor_opt_system"))
                caminho_absoluto = os.path.abspath(save_path)
                
                if editor == idiomas.tr("editor_opt_none") or "Nenhum" in editor or "None" in editor:
                    if os.name == 'nt':
                        subprocess.Popen(f'explorer /select,"{caminho_absoluto}"')
                    else:
                        subprocess.Popen(['open', '-R', caminho_absoluto] if sys.platform == 'darwin' else ['xdg-open', os.path.dirname(caminho_absoluto)])
                elif editor == "Microsoft PowerPoint":
                    subprocess.Popen(["powerpnt", caminho_absoluto], shell=True)
                elif editor == "LibreOffice Impress":
                    subprocess.Popen(["soffice", "--impress", caminho_absoluto], shell=True)
                else:
                    try:
                        if os.name == 'nt': os.startfile(caminho_absoluto)
                        else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', caminho_absoluto])
                    except Exception:
                        if os.name == 'nt':
                            subprocess.Popen(f'explorer /select,"{caminho_absoluto}"')
                        else:
                            subprocess.Popen(['open', '-R', caminho_absoluto] if sys.platform == 'darwin' else ['xdg-open', os.path.dirname(caminho_absoluto)])
                        
                        import idiomas
                        QMessageBox.information(self, idiomas.tr("msg_sys_editor_fail_tit"), idiomas.tr("msg_sys_editor_fail_msg"))
            except: pass

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar arquivo:\n{str(e)}")
            
    def abrir_tutorial(self):
        import idiomas
        
        # Estrutura da Mágica Definitiva: (Widget Alvo, Título, Texto)
        passos = [
            (self.btn_config, idiomas.tr("tut_p1_tit"), idiomas.tr("tut_p1_txt")),
            (self.btn_config, idiomas.tr("tut_p1b_tit"), idiomas.tr("tut_p1b_txt")),
            (self.btn_novidades, idiomas.tr("tut_p2_tit"), idiomas.tr("tut_p2_txt")),
            (self.btn_load, idiomas.tr("tut_p3_tit"), idiomas.tr("tut_p3_txt")),
            (self.txt_tema, idiomas.tr("tut_p4_tit"), idiomas.tr("tut_p4_txt")),
            (self.btn_assistente, idiomas.tr("tut_p4b_tit"), idiomas.tr("tut_p4b_txt")),
            (None, idiomas.tr("tut_p5_tit"), idiomas.tr("tut_p5_txt")), # Janela de Imagens
            (self.btn_historico, idiomas.tr("tut_p6_tit"), idiomas.tr("tut_p6_txt")),
            (self.combo_presets, idiomas.tr("tut_p7_tit"), idiomas.tr("tut_p7_txt")),
            (self.btn_color_title, idiomas.tr("tut_p8_tit"), idiomas.tr("tut_p8_txt")),
            (self.combo_font_title, idiomas.tr("tut_p9_tit"), idiomas.tr("tut_p9_txt")),
            (self.btn_color_body, idiomas.tr("tut_p10_tit"), idiomas.tr("tut_p10_txt")),
            (self.combo_font_body, idiomas.tr("tut_p11_tit"), idiomas.tr("tut_p11_txt")),
            (self.btn_fill_color, idiomas.tr("tut_p12_tit"), idiomas.tr("tut_p12_txt")),
            (self.btn_bg, idiomas.tr("tut_p13_tit"), idiomas.tr("tut_p13_txt")),
            (self.chk_scale, idiomas.tr("tut_p14_tit"), idiomas.tr("tut_p14_txt")),
            (self.chk_text_scale, idiomas.tr("tut_p15_tit"), idiomas.tr("tut_p15_txt")),
            (self.frame_preview, idiomas.tr("tut_p16_tit"), idiomas.tr("tut_p16_txt")),
            (self.chk_notes, idiomas.tr("tut_p17_tit"), idiomas.tr("tut_p17_txt")),
            (self.btn_save, idiomas.tr("tut_p18_tit"), idiomas.tr("tut_p18_txt")),
            (self.btn_pdf, idiomas.tr("tut_p19_tit"), idiomas.tr("tut_p19_txt"))
        ]
        
        self.overlay_tutorial.iniciar(passos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Garante que o recorte cubra a tela toda se o cara redimensionar a janela durante o tutorial
        if hasattr(self, 'overlay_tutorial') and self.overlay_tutorial.isVisible():
            self.overlay_tutorial.setGeometry(0, 0, self.width(), self.height())
            self.overlay_tutorial.atualizar_passo()
            
    def checar_notas_atualizacao(self):
        # Olha no config.json se ele já viu as novidades
        ultima_vista = self.config.get("ultima_versao_vista", "")
        
        try:
            # Puxa a versão correta do servidor em vez do manifesto local desatualizado
            url = f"https://vegap-masterapp.hf.space/master/atualizacao/{PRODUTO_ID_MASTER}"
            resposta = requests.get(url, timeout=3)
            versao_real = resposta.json().get("versao_atual", VERSAO_ATUAL) if resposta.status_code == 200 else VERSAO_ATUAL
        except:
            versao_real = VERSAO_ATUAL
            
        if ultima_vista != versao_real:
            import idiomas
            msg = QMessageBox(self)
            msg.setWindowTitle(idiomas.tr("msg_update_titulo").format(versao_real))
            msg.setText(idiomas.tr("msg_update_texto").format(versao_real))
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
            self.config["ultima_versao_vista"] = versao_real
            self.save_config()
            
    def buscar_avisos_api(self):
        try:
            # Usa a variável global blindada do manifesto local
            url = f"https://vegap-masterapp.hf.space/master/publico/avisos/{NOME_APP_MASTER}"
            resposta = requests.get(url, timeout=5)
            if resposta.status_code == 200:
                return resposta.json()
        except:
            pass
        return []

    def checar_avisos_startup(self):
        avisos = self.buscar_avisos_api()
        if not avisos: return
        
        maior_id = max([a.get("id", 0) for a in avisos])
        ultimo_lido = self.config.get("ultimo_aviso_lido", 0)
        
        # Só pula na tela se tiver um ID maior que o último que ele leu
        if maior_id > ultimo_lido:
            self.config["ultimo_aviso_lido"] = maior_id
            self.save_config()
            
            zoom_atual = self.config.get("zoom", 100)
            dialog = AvisosDialog(avisos, zoom_atual, self)
            dialog.exec()

    def abrir_avisos(self):
        self.btn_avisos.setEnabled(False)
        self.btn_avisos.setToolTip(idiomas.tr("btn_buscando"))
        QApplication.processEvents()
        
        avisos = self.buscar_avisos_api()
        
        if avisos:
            maior_id = max([a.get("id", 0) for a in avisos])
            self.config["ultimo_aviso_lido"] = maior_id
            self.save_config()
            
        self.btn_avisos.setText("📢")
        self.btn_avisos.setToolTip(idiomas.tr("btn_avisos"))
        self.btn_avisos.setEnabled(True)
        
        zoom_atual = self.config.get("zoom", 100)
        dialog = AvisosDialog(avisos, zoom_atual, self)
        dialog.exec()

    def abrir_novidades(self):
        self.btn_novidades.setEnabled(False)
        self.btn_novidades.setToolTip(idiomas.tr("btn_buscando"))
        QApplication.processEvents()
        
        try:
            url = f"https://vegap-masterapp.hf.space/master/atualizacao/{PRODUTO_ID_MASTER}"
            resposta = requests.get(url, timeout=5)
            versao_nuvem = VERSAO_ATUAL
            if resposta.status_code == 200:
                dados = resposta.json()
                if idiomas._idioma_atual == "en":
                    notas = dados.get("notas_atualizacao_en", "")
                else:
                    notas = dados.get("notas_atualizacao", "")
                    
                notas = notas.strip() if notas else ""
                versao_nuvem = dados.get("versao_atual", VERSAO_ATUAL)
                if not notas:
                    notas = idiomas.tr("msg_update_vazio")
            else:
                notas = idiomas.tr("msg_update_erro_api")
        except Exception as e:
            notas = idiomas.tr("msg_update_erro_con").format(e)
        finally:
            self.btn_novidades.setText("📋")
            self.btn_novidades.setToolTip(idiomas.tr("btn_novidades"))
            self.btn_novidades.setEnabled(True)

        # ========================================================
        # FORMATADOR INTELIGENTE (Puxa do Banco e Quebra Linhas)
        # ========================================================
        notas_formatadas = notas.replace("\\n", "\n") # Desescapa possíveis quebras da API
        notas_formatadas = notas_formatadas.replace(" • ", "\n• ")
        
        # Dá um respiro antes de cada emoji de categoria
        for emj in ["🎨", "🛡️", "⚡", "🚀", "♿", "💡", "✨", "💳", "🔧", "🔥"]:
            notas_formatadas = notas_formatadas.replace(f" {emj}", f"\n\n{emj}")
            
        # Limpa as quebras de linha excessivas geradas pelo replace
        notas_formatadas = "\n".join([linha.strip() for linha in notas_formatadas.split("\n") if linha.strip()])

        zoom_atual = self.config.get("zoom", 100)
        # USA A VERSÃO DA NUVEM PARA A JANELA
        dialog = NovidadesDialog(versao_nuvem, notas_formatadas, zoom_atual, self)
        dialog.exec()

    def abrir_conta(self):
        token_atual = self.config.get("token_master", "")
        if token_atual:
            dialog = PerfilUsuarioDialog(self)
            dialog.exec()
        else:
            dialog_auth = LoginCadastroDialog(self)
            if dialog_auth.exec() == QDialog.Accepted:
                self.config["token_master"] = dialog_auth.token_recebido
                self.save_config()

    def export_to_pdf(self):
        # Tenta pegar o último que o usuário editou/salvou. Se não tiver, pega o que ele carregou no passo 1.
        alvo = self.last_saved_pptx if self.last_saved_pptx else self.pptx_path
        
        if not alvo or not os.path.exists(alvo):
            QMessageBox.warning(self, "Aviso", "Por favor, carregue ou salve uma apresentação primeiro.")
            return

        resp = QMessageBox.question(
            self,
            idiomas.tr("pdf_confirm_titulo"),
            idiomas.tr("pdf_confirm_msg"),
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if resp != QMessageBox.Ok:
            return
            
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", alvo.replace(".pptx", ".pdf"), "PDF (*.pdf)")
        if not pdf_path: return
        
        progress = QProgressDialog("Convertendo para PDF (Aguarde...)", "Cancelar", 0, 0, self)
        progress.setWindowTitle("Gerando PDF")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()
        
        try:
            caminho_absoluto = os.path.abspath(alvo)
            pdf_absoluto = os.path.abspath(pdf_path)
            sucesso = False
            
            # 1. Tentativa Independente: LibreOffice (Modo Invisível)
            libreoffice_path = None
            if os.name == 'nt':
                for path in [r"C:\Program Files\LibreOffice\program\soffice.exe", r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"]:
                    if os.path.exists(path):
                        libreoffice_path = path
                        break
                        
            if libreoffice_path:
                out_dir = os.path.abspath(os.path.dirname(pdf_absoluto))
                comando = f'"{libreoffice_path}" --headless --convert-to pdf --outdir "{out_dir}" "{caminho_absoluto}"'
                subprocess.run(comando, shell=True, check=True)
                
                # O LibreOffice salva com o nome original do pptx, então precisamos renomear caso o usuário tenha digitado um nome diferente
                nome_gerado = os.path.join(out_dir, os.path.splitext(os.path.basename(caminho_absoluto))[0] + ".pdf")
                if nome_gerado != pdf_absoluto and os.path.exists(nome_gerado):
                    import shutil
                    shutil.move(nome_gerado, pdf_absoluto)
                sucesso = True
                
            else:
                # 2. Fallback: Escravo da Microsoft apenas se não houver outra saída
                try:
                    import comtypes.client
                    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
                    deck = powerpoint.Presentations.Open(caminho_absoluto)
                    deck.SaveAs(pdf_absoluto, 32)
                    deck.Close()
                    powerpoint.Quit()
                    sucesso = True
                except Exception:
                    raise Exception(idiomas.tr("msg_pdf_independent_fail"))

            progress.close()
            if sucesso:
                QMessageBox.information(self, idiomas.tr("msg_sucesso"), idiomas.tr("msg_pdf_independent_success"))
                
                # Abre a pasta e seleciona o PDF pra mastigar e colocar na boca do cliente
                if os.name == 'nt':
                    subprocess.Popen(f'explorer /select,"{pdf_absoluto}"')
                else:
                    subprocess.Popen(['open', '-R', pdf_absoluto] if sys.platform == 'darwin' else ['xdg-open', os.path.dirname(pdf_absoluto)])
                    
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, idiomas.tr("msg_erro_pdf"), idiomas.tr("msg_pdf_fail_generic").format(str(e)))
            
if __name__ == "__main__":
    if splash: splash.atualizar(85, "Verificando radares e atualizações do sistema...")
    if checar_e_atualizar():
        os._exit(0)
        
    if splash: splash.atualizar(95, "Preparando interface gráfica e blindagens...")
    window = AppPaiVega()
    
    if splash:
        splash.atualizar(100, "Tudo pronto! Bem-vindo(a) ao palco.")
        time.sleep(0.5)
        splash.finish(window)
        
    window.show()
    sys.exit(app.exec())