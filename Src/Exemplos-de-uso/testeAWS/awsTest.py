import requests
import json
import base64
import os
import csv
from dotenv import load_dotenv

load_dotenv()

url_api = os.getenv("API_AWS")

# Lê o vetor REAL que foi gerado
vetor_real = []
csv_path = "Src/embedding_rosto.csv"
if os.path.exists(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            vetor_real.append(float(row[1]))
else:
    print(f"Aviso: Arquivo {csv_path} não encontrado. Usando vetor zerado para teste.")
    vetor_real = [0.0] * 512

# Simular o envio de uma foto real lendo a imagem de teste
caminho_imagem = "Src/imagensdeTeste/imagemPerfil.jpeg"
foto_base64 = None

# Tenta ler a imagem e convertê-la para Base64
if os.path.exists(caminho_imagem):
    with open(caminho_imagem, "rb") as image_file:
        foto_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        print("Imagem de teste convertida para Base64 com sucesso!")
else:
    print(f"Aviso: Imagem não encontrada em {caminho_imagem}. O teste irá sem foto.")

# Montando o pacote de dados (Payload) atualizado com Porta e Foto
dados = {
    "vetor": vetor_real,
    "porta": "Catraca 01 - Entrada Principal",
    "foto_base64": foto_base64
}

# Faz a requisição POST para a AWS
resposta = requests.post(url_api, json=dados)

print("\nStatus HTTP:", resposta.status_code)
try:
    print("Resposta da AWS:")
    print(json.dumps(resposta.json(), indent=4, ensure_ascii=False))
except Exception:
    print("Resposta bruta da AWS:", resposta.text)