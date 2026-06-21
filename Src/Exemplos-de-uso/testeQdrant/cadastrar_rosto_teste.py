import os
import csv
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

url_api = os.getenv("API_AWS")

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

csv_path = "Src/embedding_rosto.csv"
if not os.path.exists(csv_path):
    print(f"\nErro: O arquivo {csv_path} com o vetor do rosto não foi encontrado.")
    exit(1)

# Lendo os 512 valores
vetor_real = []
with open(csv_path, "r") as f:
    reader = csv.reader(f)
    next(reader) # Pula a primeira linha (cabeçalho)
    for row in reader:
        vetor_real.append(float(row[1]))

print(f"\nVetor carregado do CSV com {len(vetor_real)} posições.")

# Mandando para o Qdrant via REST API
url_upsert = f"{qdrant_url}/collections/identidades_rostos/points"

payload = {
    "points": [
        {
            "id": 777, # Um ID numérico de teste
            "vector": vetor_real,
            "payload": {
                "nome": "Funcionário de Teste",
                "arquivo_origem": "imagemPerfil.jpeg"
            }
        }
    ]
}

data = json.dumps(payload).encode('utf-8')
headers = {
    "Content-Type": "application/json",
    "Api-Key": qdrant_api_key
}

print("Enviando para a nuvem...")

try:
    req = urllib.request.Request(url_upsert, data=data, headers=headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        print("\n Sucesso! O rosto de teste foi cadastrado no Qdrant!")
except Exception as e:
    print(f"\nErro na comunicação com o Qdrant: {str(e)}")
