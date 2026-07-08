import os
import json
import urllib.request
import uuid
import boto3
import datetime
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv()

caminho_imagem = "Src/imagensdeTeste/Joao-Nunes.jpeg".strip()
if not os.path.exists(caminho_imagem):
    print(f"\nErro: O arquivo {caminho_imagem} não foi encontrado.")
    exit(1)

nome_funcionario = "João Nunes".strip()
id_funcionario = "1".strip()
qdrant_url = os.getenv("QDRANT_URL").strip().rstrip('/')
qdrant_api_key = os.getenv("QDRANT_API_KEY").strip()

try:
    resultado = DeepFace.represent(img_path=caminho_imagem, model_name="ArcFace", enforce_detection=False)
    vetor_real = resultado[0]["embedding"]
    print(f"Rosto analisado com sucesso! (Vetor de {len(vetor_real)} dimensões gerado)")
except Exception as e:
    print(f"\nErro ao extrair características do rosto: {str(e)}")
    exit(1)

# Sincronização com DynamoDB
print("\nSincronizando dados com o DynamoDB...")
try:
    # Força a região sa-east-1 (São Paulo) para não dar o erro "You must specify a region"
    dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION', 'sa-east-1'))
    nome_tabela = os.getenv('DYNAMO_TABLE_FUNCIONARIOS', 'Funcionarios').strip()
    tabela = dynamodb.Table(nome_tabela)
    
    # Verifica se o funcionario ja existe
    resposta_db = tabela.get_item(Key={'id_funcionarios': id_funcionario})
    
    if 'Item' in resposta_db:
        # Já existe, então vamos apenas somar +1 na quantidade de fotos
        tabela.update_item(
            Key={'id_funcionarios': id_funcionario},
            UpdateExpression="SET faceCount = faceCount + :inc",
            ExpressionAttributeValues={':inc': 1}
        )
        novo_count = resposta_db['Item'].get('faceCount', 0) + 1
        print(f"Funcionário já existe no DynamoDB. Incrementando faceCount para {novo_count}.")
    else:
        # Novo funcionário, criando o registro
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tabela.put_item(
            Item={
                'id_funcionarios': id_funcionario,
                'createdAt': agora,
                'doors': ['Portaria Principal'], # Lista de acesso padrão
                'faceCount': 1,
                'fullName': nome_funcionario
            }
        )
        print("Novo funcionário registrado no DynamoDB com sucesso!")
except Exception as e:
    print(f"\nErro ao conectar/salvar no DynamoDB: {str(e)}")
    print("Aviso: O cadastro no DynamoDB falhou. Verifique se sua máquina possui credenciais da AWS configuradas (~/.aws/credentials).")

# Mandando para o Qdrant
url_upsert = f"{qdrant_url}/collections/identidades_rostos/points"

payload = {
    "points": [
        {
            "id": str(uuid.uuid4()),
            "vector": vetor_real,
            "payload": {
                "id_funcionario": int(id_funcionario),
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
