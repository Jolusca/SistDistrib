import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

url_api = os.getenv("API_AWS")

# Simulando o vetor que o ArcFace geraria (neste caso, de zeros, só para testar a conexão)
vetor_simulado = [0.0] * 512

dados = {
    "vetor": vetor_simulado
}

# Faz a requisição POST para a AWS
resposta = requests.post(url_api, json=dados)

print("Status HTTP:", resposta.status_code)
print("Resposta da AWS:", resposta.json())