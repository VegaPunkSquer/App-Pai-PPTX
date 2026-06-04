import os
import json
import requests
from google import genai # <-- SAI o import velho, ENTRA o novo
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# A função velha configurar_gemini() SAIU. Não precisamos mais dela.

def gerar_roteiro_slides(tema):
    """Pede ao Gemini para estruturar a apresentação e retornar sucesso e os dados."""
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Atue como um especialista em conteúdo educacional. 
    Crie uma estrutura de apresentação baseada no seguinte pedido: "{tema}".
    (Se o usuário não especificar a quantidade de slides, faça 5 por padrão).
    Retorne APENAS um array JSON válido. 
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
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        texto = response.text
        # Garante que vai pegar só a lista JSON, mesmo que a IA mande texto antes ou depois
        inicio = texto.find('[')
        fim = texto.rfind(']') + 1
        
        if inicio != -1 and fim != 0:
            texto_limpo = texto[inicio:fim]
            return True, json.loads(texto_limpo)
        else:
            return False, f"A IA não retornou um formato válido.\nResposta bruta:\n{texto}"
            
    except Exception as e:
        return False, f"Erro ao conectar com o Gemini:\n{str(e)}"

def baixar_imagem_pexels(palavra_chave, indice_slide):
    """Busca 3 imagens relacionadas no Pexels e baixa temporariamente na pasta raiz."""
    if not PEXELS_API_KEY or PEXELS_API_KEY == "SUA_CHAVE_PEXELS_AQUI":
        print("Chave do Pexels não configurada.")
        return []

    # Busca 3 fotos em formato paisagem
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
                    url_imagem = photo["src"]["medium"] # Medium carrega mais rápido pra escolha
                    img_data = requests.get(url_imagem).content
                    img_path = os.path.join(base_dir, f"temp_slide_{indice_slide}_opt_{j}.jpg")
                    
                    with open(img_path, 'wb') as handler:
                        handler.write(img_data)
                    caminhos_imagens.append(img_path)
    except Exception as e:
        print(f"Erro ao buscar/baixar imagem do Pexels: {e}")
    
    return caminhos_imagens