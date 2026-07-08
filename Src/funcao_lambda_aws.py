import json
import datetime
import os
import boto3
import urllib.request
import base64
import uuid

# Inicializando os clientes da AWS 
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Pega o nome da tabela e do bucket a partir das variáveis de ambiente na AWS
NOME_TABELA_LOGS = os.environ.get('DYNAMO_TABLE_LOGS', 'LogsAcesso')
NOME_TABELA_FUNCIONARIOS = os.environ.get('DYNAMO_TABLE_FUNCIONARIOS', 'Funcionarios')
NOME_BUCKET_S3 = os.environ.get('S3_BUCKET_FOTOS', 'bucket-fotos-acesso')
tabela_logs = dynamodb.Table(NOME_TABELA_LOGS)
tabela_funcionarios = dynamodb.Table(NOME_TABELA_FUNCIONARIOS)

def lambda_handler(event, context):
    try:
        QDRANT_URL = os.environ.get('QDRANT_URL', '').rstrip('/')
        QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY', '')
        
        # Extrair dados da requisição
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        vetor = body.get('vetor')
        porta = body.get('porta', 'Porta Desconhecida')  
        foto_base64 = body.get('foto_base64')
        
        if not vetor or len(vetor) != 512:
            return {"statusCode": 400, "body": json.dumps({"erro": "Vetor inválido. Esperado 512 dimensões."})}
            
        timestamp_oficial = datetime.datetime.now(datetime.timezone.utc).isoformat()
        registro_id = str(uuid.uuid4()) # Gera um identificador único para essa tentativa
        
        # Salva a Foto no Amazon S3
        url_foto_s3 = "Sem foto"
        if foto_base64:
            try:
                # Transforma a string Base64 de volta para o arquivo de imagem
                foto_bytes = base64.b64decode(foto_base64)
                nome_arquivo_s3 = f"tentativas/{timestamp_oficial}_{registro_id}.jpg"
                
                # Faz o Upload para o Bucket S3
                s3.put_object(
                    Bucket=NOME_BUCKET_S3,
                    Key=nome_arquivo_s3,
                    Body=foto_bytes,
                    ContentType='image/jpeg'
                )
                # Gera o link público ou privado para visualizar a foto depois
                url_foto_s3 = f"https://{NOME_BUCKET_S3}.s3.amazonaws.com/{nome_arquivo_s3}"
            except Exception as e:
                print(f"Erro ao salvar foto no S3: {e}")
                url_foto_s3 = "Erro no upload"

        # Busca Vetorial no Qdrant
        url_busca = f"{QDRANT_URL}/collections/identidades_rostos/points/search"
        payload_qdrant = json.dumps({
            "vector": vetor,
            "limit": 1,
            "with_payload": True
        }).encode('utf-8')
        
        headers = {"Content-Type": "application/json", "Api-Key": QDRANT_API_KEY}
        
        try:
            req = urllib.request.Request(url_busca, data=payload_qdrant, headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                qdrant_response = json.loads(response.read().decode('utf-8'))
            resultados = qdrant_response.get('result', [])
        except urllib.error.HTTPError as e:
            if e.code == 404: # Se a coleção não existir, apenas considera que não achou resultados
                resultados = [] 
            else:
                raise e
        
        # Avaliar o Acesso
        if resultados and resultados[0]['score'] > 0.60:
            melhor_match = resultados[0]
            # O ID real do funcionario agora fica no payload, pois o 'id' do ponto é um UUID aleatório
            id_funcionario = str(melhor_match.get('payload', {}).get('id_funcionario', melhor_match['id']))
            # Puxa o nome da pessoa lá do banco Qdrant, se não tiver nome usa o ID
            nome_funcionario = melhor_match.get('payload', {}).get('nome', f"ID: {id_funcionario}")
            score = melhor_match['score']
            
            # Verificação de Autorização de Porta via DynamoDB
            tem_acesso = False
            try:
                resposta_db = tabela_funcionarios.get_item(Key={'id_funcionarios': id_funcionario})
                if 'Item' in resposta_db:
                    portas_autorizadas = resposta_db['Item'].get('doors', [])
                    if porta in portas_autorizadas:
                        tem_acesso = True
            except Exception as db_err:
                print(f"Erro ao consultar permissão no DynamoDB: {db_err}")
                
            if tem_acesso:
                status_acesso = "Acesso Liberado"
                status_code = 200
            else:
                status_acesso = f"Acesso Negado - Porta Não Autorizada"
                status_code = 403
        else:
            id_funcionario = "Desconhecido"
            nome_funcionario = "Funcionário Desconhecido"
            score = resultados[0]['score'] if resultados else 0.0
            status_acesso = "Acesso Negado"
            status_code = 403
            
        # Registra na tabela no DynamoDB o Log Completo
        tabela_logs.put_item(
            Item={
                'id_registro': registro_id,            # ID único da tentativa
                'timestamp': timestamp_oficial,        # Horário oficial
                'porta': porta,                        # Ex: "Catraca 01 - Portaria"
                'status': status_acesso,               # Liberado ou Negado
                'id_funcionario': id_funcionario,      # ID da pessoa ou "Desconhecido"
                'score_reconhecimento': str(score),    # Certeza da IA
                'link_foto': url_foto_s3               # O link exato para o S3
            }
        )
        
        # Retorno para o PC Local
        return {
            "statusCode": status_code,
            "body": json.dumps({
                "mensagem": status_acesso,
                "nome_funcionario": nome_funcionario,
                "porta": porta,
                "horario": timestamp_oficial
            })
        }
            
    except Exception as e:
        print(f"Erro Crítico na Lambda: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"erro": str(e)})}
