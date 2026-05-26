import json
import datetime
import os
from qdrant_client import QdrantClient


## exemplo de função Lambda para conectar a AWS ao Qdrant 


def lambda_handler(event, context):
    # 1. Configuração segura (a chave não está no código, mas em variáveis de ambiente)
    QDRANT_URL = os.environ['QDRANT_URL']
    QDRANT_API_KEY = os.environ['QDRANT_API_KEY']
    
    # 2. Recebe o dado do "Edge" (PC local)
    data = json.loads(event['body'])
    vetor = data.get('vetor')
    
    # 3. Validação de sanitização
    if not vetor or len(vetor) != 512:
        return {"statusCode": 400, "body": json.dumps({"erro": "Vetor inválido"})}
    
    # 4. Geração do Timestamp de autoridade (AWS)
    timestamp_oficial = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # 5. Consulta ao Qdrant (Camada de busca vetorial)
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    resultados = client.search(
        collection_name="funcionarios",
        query_vector=vetor,
        limit=1
    )
    
    if resultados and resultados[0].score > 0.8: # Threshold de precisão
        nome = resultados[0].payload.get('nome')
        
        # Aqui você chamaria o RDS para registrar o ponto com o timestamp_oficial
        return {
            "statusCode": 200,
            "body": json.dumps({
                "mensagem": f"Ponto registrado para {nome}",
                "horario": timestamp_oficial
            })
        }
    
    return {"statusCode": 404, "body": json.dumps({"erro": "Funcionário não identificado"})}