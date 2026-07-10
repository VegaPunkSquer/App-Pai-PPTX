import os
import sys
import json
import time
import requests
import traceback
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# --- RESOLUÇÃO DE CAMINHOS ABSOLUTOS (Regra de Ouro) ---
if getattr(sys, 'frozen', False):
    # Se estiver rodando como .exe
    base_dir = os.path.dirname(sys.executable)
    env_path = os.path.join(sys._MEIPASS, '.env')
else:
    # Se estiver rodando via código fonte
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')

# --- O LOG SUPREMO DO VEGA ---
def registrar_log_supremo(mensagem, erro=False):
    """Grava ABSOLUTAMENTE TUDO em um arquivo txt do lado do executável."""
    try:
        log_path = os.path.join(base_dir, "LOG_SUPREMO_VEGA.txt")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tipo = "[ERRO FATAL]" if erro else "[INFO]"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{agora} {tipo} -> {mensagem}\n")
    except Exception as e:
        print(f"Ironicamente, o log supremo falhou: {e}")

registrar_log_supremo("=== MOTOR IA INICIADO ===")

load_dotenv(env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# --- ENTRA AQUI: TRAVA DE SEGURANÇA E BACKOFF ANTI-SURTO DO GOOGLE ---
ULTIMA_REQUISICAO = 0.0
INTERVALO_MINIMO = 3.0  # Tempo mínimo em segundos entre uma requisição e outra (Evita disparos de metralhadora)

def aguardar_rate_limit():
    """Garante que o app não atire requisições mais rápido do que a API tolera."""
    global ULTIMA_REQUISICAO
    tempo_atual = time.time()
    tempo_passado = tempo_atual - ULTIMA_REQUISICAO
    if tempo_passado < INTERVALO_MINIMO:
        tempo_espera = INTERVALO_MINIMO - tempo_passado
        registrar_log_supremo(f"[TRAVA ANTI-SURTO] Aguardando {tempo_espera:.2f}s para proteger a API...")
        time.sleep(tempo_espera)
    ULTIMA_REQUISICAO = time.time()
# ---------------------------------------------------------------------

def gerar_roteiro_slides(assunto_apresentacao, api_key_usuario=None, modelo_selecionado='gemini-2.5-flash'):
    registrar_log_supremo(f"Iniciando gerar_roteiro_slides. Assunto: '{assunto_apresentacao}', Modelo: {modelo_selecionado}")
    
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    
    if not chave_final:
        registrar_log_supremo("Execução parada: Chave de API não configurada.", erro=True)
        return False, "ERRO: Chave de API não configurada. Ative sua licença ou insira sua chave (BYOK)."

    try:
        registrar_log_supremo("Inicializando cliente do Gemini genai.Client...")
        client = genai.Client(api_key=chave_final)
    except Exception as e:
        registrar_log_supremo(f"Falha ao criar o cliente da API: {traceback.format_exc()}", erro=True)
        return False, f"Erro ao inicializar o cliente do Gemini:\n{str(e)}"
    
    prompt = f"""
    Atue como um designer de apresentações corporativas nível sênior (estilo Gamma/Canva). 
    Crie uma estrutura de apresentação espetacular baseada no assunto: "{assunto_apresentacao}".
    Retorne APENAS um array JSON válido. Nada de markdown ou crases em volta, só o JSON cru.
    
    Regra de Ouro: Alterne os layouts. Escolha sabiamente entre estes 4 "tipo_layout":
    1. "padrao": Ideal para a maioria dos slides. Traz um texto base e pode ter imagem lateral.
    2. "cards": Separa a informação em até 3 blocos/tópicos (ótimo para "benefícios", "fases", etc).
    3. "destaque": Usado para frases de impacto ou quebra de seção. Fonte gigante, centralizado.
    4. "grafico": Use APENAS quando houver dados numéricos, estatísticas ou comparações claras para exibir um gráfico de colunas.

    Formato do JSON estritamente exigido:
    [
        {{
            "titulo": "Título do slide",
            "tipo_layout": "padrao", 
            "texto": "Parágrafo de explicação geral ou a frase de impacto.",
            "topicos": [
                {{"icone": "🚀", "titulo": "Ponto 1", "texto": "Breve descrição."}}
            ],
            "dados_grafico": {{
                "categorias": ["2023", "2024", "2025"],
                "valores": [10, 45, 80],
                "nome_serie": "Crescimento"
            }},
            "palavra_chave_imagem": "termo em ingles para o pexels (vazio se não for layout padrao)",
            "roteiro_apresentador": "Texto fluido e persuasivo com o que o palestrante DEVE FALAR em voz alta enquanto este slide estiver na tela."
        }}
    ]
    """
    
    try:
        registrar_log_supremo("Enviando prompt para a API do Google... (Aguardando resposta)")
        
        # --- ENTRA AQUI: SISTEMA DE BACKOFF EXPONENCIAL + TRAVA ---
        tentativas = 0
        max_tentativas = 3
        while tentativas < max_tentativas:
            try:
                aguardar_rate_limit()  # Aciona nosso amortecedor antes de atirar no Google
                response = client.models.generate_content(
                    model=modelo_selecionado,
                    contents=prompt
                )
                break  # Se deu certo, sai do loop imediatamente!
            except Exception as e_interno:
                tentativas += 1
                erro_str_interno = str(e_interno)
                # Se for erro de cota ou limite (429/Exhausted), espera um tempo exponencial e tenta de novo
                if "RESOURCE_EXHAUSTED" in erro_str_interno or "429" in erro_str_interno:
                    tempo_backoff = (2 ** tentativas) * 2  # Espera 4s, depois 8s, depois 16s...
                    registrar_log_supremo(f"[BACKOFF] API sobrecarregada ou limite de taxa. Tentativa {tentativas}/{max_tentativas}. Aguardando {tempo_backoff}s...", erro=True)
                    time.sleep(tempo_backoff)
                else:
                    raise e_interno  # Se for erro grave de código/chave, repassa o erro para explodir logo
        else:
            return False, "O sistema do Google rejeitou múltiplas tentativas seguidas (Rate Limit / Cota excedida). Aguarde um minuto."
        # -----------------------------------------------------------

        registrar_log_supremo("Resposta recebida do Google com sucesso! Processando texto...")
        
        texto = response.text
        inicio = texto.find('[')
        fim = texto.rfind(']') + 1
        
        if inicio != -1 and fim != 0:
            registrar_log_supremo("JSON encontrado e validado com sucesso. Retornando dados.")
            return True, json.loads(texto[inicio:fim])
        else:
            registrar_log_supremo(f"IA respondeu, mas não encontrei um array JSON. Texto puro: {texto}", erro=True)
            return False, f"Formato inválido retornado pela IA. Resposta: {texto}"
            
    except Exception as e:
        erro_str = str(e)
        registrar_log_supremo(f"Explosão ao tentar comunicar com a API: {traceback.format_exc()}", erro=True)
        
        if "RESOURCE_EXHAUSTED" in erro_str:
            return False, (
                "Atenção: A cota desta chave foi atingida.\n\n"
                "1. Verifique seu projeto no Google AI Studio/Cloud.\n"
                "2. Confirme se a conta de faturamento está ativa no novo projeto.\n"
                "3. Se o erro persistir, gere uma nova chave no projeto de produção."
            )
        return False, f"Erro inesperado na IA: {erro_str}"

def baixar_imagem_pexels(palavra_chave, indice_slide):
    registrar_log_supremo(f"Iniciando download de imagem Pexels. Palavra: '{palavra_chave}'")
    if not PEXELS_API_KEY: 
        registrar_log_supremo("Chave do Pexels não encontrada.", erro=True)
        return []

    url = f"https://api.pexels.com/v1/search?query={palavra_chave}&per_page=3&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    
    caminhos_imagens = []
    try:
        registrar_log_supremo("Buscando fotos na API do Pexels...")
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("photos"):
                registrar_log_supremo(f"Fotos encontradas! Baixando 3 opções para o slide {indice_slide}...")
                for j, photo in enumerate(dados["photos"]):
                    url_imagem = photo["src"]["medium"]
                    img_data = requests.get(url_imagem).content
                    img_path = os.path.join(base_dir, f"temp_slide_{indice_slide}_opt_{j}.jpg")
                    
                    with open(img_path, 'wb') as handler:
                        handler.write(img_data)
                    caminhos_imagens.append(img_path)
                registrar_log_supremo(f"Downloads concluídos para o slide {indice_slide}.")
        else:
            registrar_log_supremo(f"Pexels retornou status code anormal: {resposta.status_code}", erro=True)
    except Exception as e:
        registrar_log_supremo(f"Erro ao baixar imagem: {traceback.format_exc()}", erro=True)
    
    return caminhos_imagens

def listar_modelos(api_key_usuario=None):
    registrar_log_supremo("Buscando lista de modelos disponíveis...")
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    if not chave_final: return ["gemini-2.5-flash"]
    try:
        client = genai.Client(api_key=chave_final)
        modelos = [m.name.replace('models/', '') for m in client.models.list() if 'generateContent' in m.supported_generation_methods]
        registrar_log_supremo(f"Modelos encontrados: {modelos}")
        return modelos if modelos else ["gemini-2.5-flash"]
    except Exception as e:
        registrar_log_supremo(f"Erro ao listar modelos: {e}", erro=True)
        return ["gemini-2.5-flash", "gemini-2.5-pro"]

def testar_conectividade(api_key_usuario=None):
    registrar_log_supremo("Executando teste RÁPIDO de conectividade...")
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    if not chave_final:
        registrar_log_supremo("Teste recusado: Sem chave de API.", erro=True)
        return False, "Chave da API Gemini não configurada!"
    try:
        client = genai.Client(api_key=chave_final)
        client.models.get(model='gemini-2.5-flash')
        registrar_log_supremo("Teste de conectividade: SUCESSO. A chave está ativa.")
        return True, "OK"
    except Exception as e:
        erro_str = str(e)
        registrar_log_supremo(f"Teste falhou: {traceback.format_exc()}", erro=True)
        if "RESOURCE_EXHAUSTED" in erro_str:
            return False, "O saldo desta chave se esgotou ou foi bloqueada (Erro 429)."
        elif "API_KEY" in erro_str.upper() or "400" in erro_str:
            return False, "Chave de API inválida ou incorreta."
        return False, f"Falha na conexão: {erro_str}"