import os
import json
import requests
import google.generativeai as genai

# Coloque suas chaves aqui
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def configurar_gemini():
    genai.configure(api_key=GEMINI_API_KEY)

def gerar_roteiro_slides(tema, num_slides=5):
    """Pede ao Gemini para estruturar a apresentação e retornar um JSON."""
    configurar_gemini()
    
    # Utilizando o modelo 2.5 Flash para geração rápida e estruturada
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Atue como um especialista em conteúdo educacional. 
    Crie uma apresentação de {num_slides} slides sobre o tema: "{tema}".
    Retorne APENAS um JSON válido, sem formatação markdown ou textos extras. 
    O formato deve ser estritamente uma lista de dicionários com as chaves abaixo:
    [
        {{
            "titulo": "Título do slide",
            "texto": "Um parágrafo de explicação direta e clara para ir no corpo do slide.",
            "palavra_chave_imagem": "english keyword for pexels search"
        }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpa possível formatação markdown (```json ... ```) caso a IA devolva
        texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpo)
    except Exception as e:
        print(f"Erro ao gerar conteúdo com o Gemini: {e}")
        return []

def baixar_imagem_pexels(palavra_chave, indice_slide):
    """Busca uma imagem relacionada no Pexels e baixa temporariamente na pasta raiz."""
    if not PEXELS_API_KEY or PEXELS_API_KEY == "SUA_CHAVE_PEXELS_AQUI":
        print("Chave do Pexels não configurada.")
        return None

    # Busca 1 foto em formato paisagem
    url = f"https://api.pexels.com/v1/search?query={palavra_chave}&per_page=1&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("photos"):
                url_imagem = dados["photos"][0]["src"]["large"]
                
                img_data = requests.get(url_imagem).content
                
                # Aplicação da regra de caminho absoluto para arquivos 
                base_dir = os.path.dirname(os.path.abspath(__file__))
                img_path = os.path.join(base_dir, f"temp_slide_{indice_slide}.jpg")
                
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                
                return img_path
    except Exception as e:
        print(f"Erro ao buscar/baixar imagem do Pexels: {e}")
    
    return None