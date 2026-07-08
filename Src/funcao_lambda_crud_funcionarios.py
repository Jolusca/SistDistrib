import json
import boto3
import uuid
import os
import decimal
import urllib.request
import urllib.error
import random
from datetime import datetime, timezone

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource("dynamodb")
tabela_funcionarios = dynamodb.Table(os.environ.get("DYNAMO_TABLE_FUNCIONARIOS", "Funcionarios"))
tabela_logs = dynamodb.Table('LogsAcesso')

COLECAO_QDRANT = "identidades_rostos"

# -------------------------------------------------------------------
# FUNÇÃO AUXILIAR: Qdrant via HTTP (Sem dependência de biblioteca externa)
# -------------------------------------------------------------------
def qdrant_request(endpoint, method="POST", data=None):
    url = f"{os.environ.get('QDRANT_URL', '').rstrip('/')}/collections/{COLECAO_QDRANT}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": os.environ.get("QDRANT_API_KEY", "")
    }
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode("utf-8")
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Qdrant Warning ({e.code}): {e.read().decode('utf-8')}")
        # Retorna None para não derrubar a API caso o Qdrant falhe momentaneamente
        return None 


def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Api-Key",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
    }

    try:
        http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
        route_key = event.get('requestContext', {}).get('routeKey', '')
        path_completo = event.get("path", "")

        if http_method == "OPTIONS":
            return {"statusCode": 200, "headers": headers, "body": ""}

        if "/faces" in path_completo:
            return {"statusCode": 200, "headers": headers, "body": json.dumps([])}

        path_parameters = event.get("pathParameters") or {}
        id_funcionario = path_parameters.get("id")
        
        if not id_funcionario:
            partes = path_completo.rstrip("/").split("/")
            if len(partes) > 0 and partes[-1].isdigit():
                id_funcionario = partes[-1]


        if route_key == 'GET /logs' or (http_method == 'GET' and 'logs' in path_completo):
            response = tabela_logs.scan()
            logs = response.get('Items', [])
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps(logs, cls=DecimalEncoder)}

        if http_method == "GET" and not 'logs' in event.get('path', ''):
            if id_funcionario:
                response = tabela_funcionarios.get_item(Key={"id_funcionarios": id_funcionario})
                item = response.get("Item")
                if not item:
                    return {"statusCode": 404, "headers": headers, "body": json.dumps({"message": "Funcionário não encontrado"})}
                
                item["id"] = item.pop("id_funcionarios")
                item["doors"] = item.get("doors", []) # PREVENÇÃO: Se não tiver portas, retorna []
                return {"statusCode": 200, "headers": headers, "body": json.dumps(item, cls=DecimalEncoder)}
            else:
                response = tabela_funcionarios.scan()
                items = response.get("Items", [])
                for item in items:
                    item["id"] = item.pop("id_funcionarios")
                    item["doors"] = item.get("doors", []) # PREVENÇÃO: Array vazio para os antigos
                    item["faceCount"] = item.get("faceCount", 0)

                return {"statusCode": 200, "headers": headers, "body": json.dumps(items, cls=DecimalEncoder)}

        elif http_method == "PUT":
            if not id_funcionario:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"message": "ID ausente"})}
            
            body = json.loads(event.get("body", "{}"))
            novo_nome = body.get("fullName", "")
            novas_portas = body.get("doors", [])
            
            response = tabela_funcionarios.update_item(
                Key={"id_funcionarios": id_funcionario},
                UpdateExpression="SET fullName = :fn, doors = :d, updatedAt = :u",
                ExpressionAttributeValues={
                    ":fn": novo_nome,
                    ":d": novas_portas,
                    ":u": datetime.now(timezone.utc).isoformat(),
                },
                ReturnValues="ALL_NEW",
            )
            item_atualizado = response.get("Attributes", {})
            
            id_filtro = int(id_funcionario) if id_funcionario.isdigit() else id_funcionario
            body_qdrant = {
                "payload": {"nome": novo_nome, "fullName": novo_nome},
                "filter": {"must": [{"key": "id_funcionario", "match": {"value": id_filtro}}]}
            }
            qdrant_request("points/payload", method="PUT", data=body_qdrant)
            
            item_atualizado["id"] = item_atualizado.pop("id_funcionarios")
            return {"statusCode": 200, "headers": headers, "body": json.dumps(item_atualizado, cls=DecimalEncoder)}


        # elif http_method == "POST":
        #     body = json.loads(event.get("body", "{}"))
        #     novo_id = str(random.randint(100000, 999999)) # ID numérico como string
            
        #     novo_nome = body.get("fullName", "")
        #     novas_portas = body.get("doors", [])
            
        #     # A. Salva no DynamoDB
        #     novo_item = {
        #         "id_funcionarios": novo_id,
        #         "fullName": novo_nome,
        #         "doors": novas_portas,
        #         "faceCount": 0,
        #         "createdAt": datetime.now(timezone.utc).isoformat(),
        #     }
        #     tabela_funcionarios.put_item(Item=novo_item)
            
        #     # B. Cria um "vetor de zeros" no Qdrant reservando o espaço
        #     body_qdrant = {
        #         "points": [{
        #             "id": str(uuid.uuid4()),
        #             "vector": [0.0] * 512,  
        #             "payload": {
        #                 "id_funcionario": int(novo_id),
        #                 "nome": novo_nome,
        #                 "fullName": novo_nome
        #             }
        #         }]
        #     }
        #     qdrant_request("points", method="PUT", data=body_qdrant)
            
        #     novo_item["id"] = novo_item.pop("id_funcionarios")
        #     return {"statusCode": 201, "headers": headers, "body": json.dumps(novo_item, cls=DecimalEncoder)}

        elif http_method == "DELETE":
            if not id_funcionario:
                return {"statusCode": 400, "headers": headers, "body": json.dumps({"message": "ID ausente"})}
                
            # A. Deleta no DynamoDB
            tabela_funcionarios.delete_item(Key={"id_funcionarios": id_funcionario})
            
            # B. Deleta todos os rostos do Qdrant baseados neste ID
            id_filtro = int(id_funcionario) if id_funcionario.isdigit() else id_funcionario
            body_qdrant = {
                "filter": {"must": [{"key": "id_funcionario", "match": {"value": id_filtro}}]}
            }
            qdrant_request("points/delete", method="POST", data=body_qdrant)
            
            return {"statusCode": 204, "headers": headers, "body": ""}

        return {"statusCode": 405, "headers": headers, "body": json.dumps({"message": "Método não permitido"})}

    except Exception as e:
        print(f"Erro Crítico na Lambda: {str(e)}")
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": str(e)})}