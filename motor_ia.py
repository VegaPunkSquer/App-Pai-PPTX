import os
import sys
import json
import requests
from google import genai
from dotenv import load_dotenv

# Carrega o .env embutido no .exe
if getattr(sys, 'frozen', False):
    env_path = os.path.join(sys._MEIPASS, '.env')
else:
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))

load_dotenv(env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def gerar_roteiro_slides(tema, api_key_usuario=None, modelo_selecionado='gemini-2.5-flash'):
    """Gera o roteiro usando a chave do SaaS ou a chave BYOK do cliente."""
    
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    
    if not chave_final:
        return False, "ERRO: Chave de API não configurada. Ative sua licença ou insira sua chave (BYOK)."

    try:
        client = genai.Client(api_key=chave_final)
    except Exception as e:
        return False, f"Erro ao inicializar o cliente do Gemini:\n{str(e)}"
    
    prompt = f"""
    Atue como um especialista em conteúdo educacional. 
    Crie uma estrutura de apresentação baseada no seguinte pedido: "{tema}".
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
        response = client.models.generate_content(
            model=modelo_selecionado,
            contents=prompt
        )
        
        texto = response.text
        inicio = texto.find('[')
        fim = texto.rfind(']') + 1
        
        if inicio != -1 and fim != 0:
            return True, json.loads(texto[inicio:fim])
        else:
            return False, f"Formato inválido retornado pela IA. Resposta: {texto}"
            
    except Exception as e:
        erro_str = str(e)
        if "RESOURCE_EXHAUSTED" in erro_str:
            return False, (
                "Atenção: A cota desta chave foi atingida.\n\n"
                "1. Verifique seu projeto no Google AI Studio/Cloud.\n"
                "2. Confirme se a conta de faturamento está ativa no novo projeto.\n"
                "3. Se o erro persistir, gere uma nova chave no projeto de produção."
            )
        return False, f"Erro inesperado na IA: {erro_str}"

def baixar_imagem_pexels(palavra_chave, indice_slide):
    if not PEXELS_API_KEY: return []

    url = f"https://api.pexels.com/v1/search?query={palavra_chave}&per_page=3&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    
    caminhos_imagens = []
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("photos"):
                base_dir = os.path.dirname(os.path.abspath(__file__))
                for j, photo in enumerate(dados["photos"]):
                    url_imagem = photo["src"]["medium"]
                    img_data = requests.get(url_imagem).content
                    img_path = os.path.join(base_dir, f"temp_slide_{indice_slide}_opt_{j}.jpg")
                    
                    with open(img_path, 'wb') as handler:
                        handler.write(img_data)
                    caminhos_imagens.append(img_path)
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
    
    return caminhos_imagens

def listar_modelos(api_key_usuario=None):
    """Busca dinamicamente quais modelos de geração de texto esta chave tem acesso."""
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY
    if not chave_final: return ["gemini-2.5-flash"]
    try:
        client = genai.Client(api_key=chave_final)
        # Filtra apenas os modelos que fazem geração de conteúdo
        modelos = [m.name.replace('models/', '') for m in client.models.list() if 'generateContent' in m.supported_generation_methods]
        return modelos if modelos else ["gemini-2.5-flash"]
    except Exception:
        # Fallback de segurança se a chave estiver bloqueada
        return ["gemini-2.5-flash", "gemini-2.5-pro"]

def testar_conectividade(api_key_usuario=None):
    """Checa se a chave do Gemini está viva e com saldo ANTES de rodar a barra."""
    chave_final = api_key_usuario if api_key_usuario else GEMINI_API_KEY # <-- Corrigido aqui
    if not chave_final:
        return False, "Chave da API Gemini não configurada!"
    try:
        client = genai.Client(api_key=chave_final)
        # Pede apenas as informações do modelo (gasta 0 tokens e valida a cota na hora)
        client.models.get(model='gemini-2.5-flash')
        return True, "OK"
    except Exception as e:
        erro_str = str(e)
        if "RESOURCE_EXHAUSTED" in erro_str:
            return False, "O saldo desta chave se esgotou ou foi bloqueada (Erro 429)."
        elif "API_KEY" in erro_str.upper() or "400" in erro_str:
            return False, "Chave de API inválida ou incorreta."
        return False, f"Falha na conexão: {erro_str}"