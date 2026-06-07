import os
import sys
import json
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
    Atue como um especialista em conteúdo educacional. 
    Crie uma estrutura de apresentação baseada no seguinte pedido: "{assunto_apresentacao}".
    Retorne APENAS um array JSON válido. 
    [
        {{
            "titulo": "Título do slide",
            "texto": "Um parágrafo de explicação.",
            "palavra_chave_imagem": "english keyword for pexels search"
        }}
    ]
    """
    
    try:
        registrar_log_supremo("Enviando prompt para a API do Google... (Aguardando resposta)")
        response = client.models.generate_content(
            model=modelo_selecionado,
            contents=prompt
        )
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