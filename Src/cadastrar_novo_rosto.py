import os
import json
import urllib.request
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv()

caminho_imagem = "Src/imagensdeTeste/perfil_Joao_Lucas.jpeg".strip()
if not os.path.exists(caminho_imagem):
    print(f"\n❌ Erro: O arquivo {caminho_imagem} não foi encontrado.")
    exit(1)

nome_funcionario = "João Lucas".strip()
id_funcionario = "123456".strip()
qdrant_url = os.getenv("QDRANT_URL").strip().rstrip('/')
qdrant_api_key = os.getenv("QDRANT_API_KEY").strip()

try:
    resultado = DeepFace.represent(img_path=caminho_imagem, model_name="ArcFace", enforce_detection=False)
    vetor_real = resultado[0]["embedding"]
    print(f"Rosto analisado com sucesso! (Vetor de {len(vetor_real)} dimensões gerado)")
except Exception as e:
    print(f"\nErro ao extrair características do rosto: {str(e)}")
    exit(1)

# Mandando para o Qdrant
url_upsert = f"{qdrant_url}/collections/identidades_rostos/points"

payload = {
    "points": [
        {
            "id": int(id_funcionario),
            "vector": vetor_real,
            "payload": {
                "nome": nome_funcionario,
                "arquivo_origem": os.path.basename(caminho_imagem)
            }
        }
    ]
}

data = json.dumps(payload).encode('utf-8')
headers = {
    "Content-Type": "application/json",
    "Api-Key": qdrant_api_key
}

try:
    req = urllib.request.Request(url_upsert, data=data, headers=headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        print(f"\nSUCESSO! A pessoa '{nome_funcionario}' foi cadastrada no banco de dados!")
        print("A câmera agora já pode reconhecer essa pessoa e liberar o acesso.")
except Exception as e:
    print(f"\nErro na comunicação com o Qdrant: {str(e)}")
