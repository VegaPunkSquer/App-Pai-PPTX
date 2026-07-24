import os
import sys
import json
import time
import requests
import traceback
import re  # <--- ADICIONADO AQUI
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
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")  # A sua chave embutida SAAS
CF_API_TOKEN = os.getenv("CF_API_TOKEN")    # A sua chave embutida SAAS

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

def gerar_roteiro_slides(assunto_apresentacao, config_ia):
    provedor = config_ia.get("provedor", "gemini")
    registrar_log_supremo(f"Roteador IA ativado. Provedor: {provedor.upper()}")

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

    if provedor == "cloudflare":
        return _gerar_cloudflare(prompt, config_ia)
    else:
        return _gerar_gemini(prompt, config_ia)

def _gerar_gemini(prompt, config_ia):
    api_key_usuario = config_ia.get("api_key")
    modelo_selecionado = config_ia.get("model", "gemini-2.5-flash")
    
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    if not chave_final:
        registrar_log_supremo("Execução parada: Chave de API não configurada.", erro=True)
        return False, "ERRO: Chave de API não configurada."

    try:
        client = genai.Client(api_key=chave_final)
    except Exception as e:
        registrar_log_supremo(f"Falha ao criar o cliente da API: {traceback.format_exc()}", erro=True)
        return False, f"Erro ao inicializar cliente do Gemini:\n{str(e)}"
    
    try:
        tentativas = 0
        max_tentativas = 3
        while tentativas < max_tentativas:
            try:
                aguardar_rate_limit()
                response = client.models.generate_content(model=modelo_selecionado, contents=prompt)
                break 
            except Exception as e_interno:
                tentativas += 1
                erro_str_interno = str(e_interno)
                if "RESOURCE_EXHAUSTED" in erro_str_interno or "429" in erro_str_interno:
                    tempo_backoff = (2 ** tentativas) * 2 
                    registrar_log_supremo(f"[BACKOFF] Tentativa {tentativas}/{max_tentativas}. Aguardando {tempo_backoff}s...", erro=True)
                    time.sleep(tempo_backoff)
                else:
                    raise e_interno
        else:
            return False, "Rate Limit ou Cota excedida no Google. Aguarde um minuto."

        json_puro = extrair_json_puro(response.text)
        if isinstance(json_puro, tuple):
            registrar_log_supremo(f"Gemini não retornou JSON. Falha: {json_puro[1]}", erro=True)
            return False, f"Formato inválido retornado pela IA."
            
        registrar_log_supremo("JSON (Gemini) validado com sucesso.")
        return True, json_puro
            
    except Exception as e:
        registrar_log_supremo(f"Explosão na API Gemini: {traceback.format_exc()}", erro=True)
        if "RESOURCE_EXHAUSTED" in str(e):
            return False, "Atenção: A cota desta chave foi atingida."
        return False, f"Erro inesperado na IA: {str(e)}"

def _gerar_cloudflare(prompt, config_ia):
    # Se ele digitou algo (BYOK), usa. Se estiver vazio (SAAS), usa as globais do seu .env
    account_id = config_ia.get("cf_account_id", "").strip() or CF_ACCOUNT_ID
    token = config_ia.get("cf_api_token", "").strip() or CF_API_TOKEN
    modelo = config_ia.get("cf_model", "@cf/meta/llama-3-8b-instruct")

    if not account_id or not token:
        registrar_log_supremo("Cloudflare: Chaves ausentes.", erro=True)
        return False, "Account ID ou API Token da Cloudflare não configurados."

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{modelo}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": "Você é um assistente que responde APENAS com JSON. Nenhuma explicação adicional."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        registrar_log_supremo(f"Atirando contra API da Cloudflare ({modelo})...")
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200:
            resultado = resp.json()
            texto_ia = resultado.get("result", {}).get("response", "")
            
            json_limpo = extrair_json_puro(texto_ia)
            if isinstance(json_limpo, tuple):
                registrar_log_supremo(f"Cloudflare tagarelou e quebrou o JSON: {json_limpo[1]}", erro=True)
                return False, json_limpo[1]
                
            registrar_log_supremo("JSON (Cloudflare) validado com sucesso.")
            return True, json_limpo
        else:
            registrar_log_supremo(f"Erro HTTP {resp.status_code}: {resp.text}", erro=True)
            return False, f"Erro na Cloudflare ({resp.status_code})"
    except Exception as e:
        registrar_log_supremo(f"Falha ao conectar na Cloudflare: {e}", erro=True)
        return False, f"Falha de conexão com a Cloudflare: {str(e)}"

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

# ==========================================
# 🛡️ BLINDAGEM ANTI-TAGARELICE (REGEX SHIELD)
# ==========================================
def extrair_json_puro(texto_resposta):
    texto = texto_resposta.strip()
    match_lista = re.search(r'\[.*\]', texto, re.DOTALL)
    if match_lista:
        try: return json.loads(match_lista.group(0))
        except: pass
            
    match_dic = re.search(r'\{.*\}', texto, re.DOTALL)
    if match_dic:
        try: return json.loads(match_dic.group(0))
        except: pass
            
    try:
        return json.loads(texto)
    except Exception as e:
        return None, f"Falha ao decodificar JSON. Resposta bruta:\n{texto[:300]}...\nErro: {e}"

# ==========================================
# 🔄 BUSCADORES DINÂMICOS
# ==========================================
def listar_modelos_gemini(api_key_usuario=None):
    registrar_log_supremo("Buscando lista de modelos Gemini...")
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    
    if not chave_final: 
        return [], "Chave de API não encontrada (Variável vazia)."
        
    try:
        client = genai.Client(api_key=chave_final)
        modelos = []
        
        for m in client.models.list():
            nome = m.name.replace('models/', '')
            # Filtro direto e limpo: pega os "gemini" e descarta os geradores de vetores
            if 'gemini' in nome.lower() and 'embed' not in nome.lower():
                modelos.append(nome)
                
        # Ordena alfabeticamente e inverte (pra jogar as versões mais novas pro topo)
        modelos.sort(reverse=True)
        return modelos, "OK"
        
    except Exception as e:
        registrar_log_supremo(f"Erro ao listar Gemini: {e}", erro=True)
        return [], str(e)

def listar_modelos_cloudflare(account_id, api_token):
    registrar_log_supremo("Buscando lista de modelos na Cloudflare via /ai/models/search...")
    
    chave_acc = account_id if account_id else CF_ACCOUNT_ID
    chave_tok = api_token if api_token else CF_API_TOKEN
    
    if not chave_acc or not chave_tok:
        registrar_log_supremo("Sem credenciais da Cloudflare configuradas.", erro=True)
        return [], "Account ID ou API Token da Cloudflare não configurados."
        
    # Rota corrigida exatamente conforme a documentação oficial da Cloudflare
    url = f"https://api.cloudflare.com/client/v4/accounts/{chave_acc}/ai/models/search"
    headers = {"Authorization": f"Bearer {chave_tok}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            dados = resp.json()
            modelos_texto = []
            
            for modelo in dados.get("result", []):
                tarefa = modelo.get("task", {}).get("name", "")
                if tarefa == "Text Generation":
                    nome_modelo = modelo.get("name")
                    if nome_modelo:
                        modelos_texto.append(nome_modelo)
            
            modelos_texto.sort()
            registrar_log_supremo(f"Encontrados {len(modelos_texto)} modelos de texto na Cloudflare.")
            return modelos_texto, "OK"
        else:
            erro_msg = f"Erro HTTP {resp.status_code}: {resp.text}"
            registrar_log_supremo(erro_msg, erro=True)
            return [], erro_msg
            
    except Exception as e:
        erro_msg = str(e)
        registrar_log_supremo(f"Falha de conexão com a Cloudflare: {erro_msg}", erro=True)
        return [], erro_msg

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