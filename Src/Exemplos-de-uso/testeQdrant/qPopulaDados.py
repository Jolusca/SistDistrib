import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv()
print("URL do Banco:", os.getenv("APIURL"))

# Conectar ao Qdrant Cloud
client = QdrantClient(
    url=os.getenv("APIURL"),
    api_key=os.getenv("APITESTE")
)

NOME_COLECAO = "identidades_rostos"

# Criar a coleção configurada para o ArcFace (512 dimensões)
if not client.collection_exists(collection_name=NOME_COLECAO):
    client.create_collection(
        collection_name=NOME_COLECAO,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE),
    )
    print(f"Coleção '{NOME_COLECAO}' criada com sucesso.")

# Caminho da pasta que contém as fotos
caminho_pasta = "/home/lucas/Downloads/frontal images A"
contador_id = 0
sucessos = 0

print("Iniciando a varredura da pasta, extração de embeddings e envio individual...")

# Percorrer todos os arquivos do diretório
for nome_arquivo in os.listdir(caminho_pasta):
    # Filtrar apenas arquivos de imagem comuns
    if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        
        try:
            print(f"Processando imagem: {nome_arquivo}")
            
            # Extrair o embedding com ArcFace localmente
            embedding_objs = DeepFace.represent(
                img_path=caminho_completo, 
                model_name="ArcFace",
                enforce_detection=True  # Dispara um erro se não achar um rosto na foto
            )
            
            # Recuperar a lista de 512 floats
            embedding = embedding_objs[0]["embedding"]
            
            # Montar a estrutura do ponto para o Qdrant
            point = PointStruct(
                id=contador_id,
                vector=embedding,  # Enviamos o vetor numérico gerado pelo ArcFace
                payload={
                    "titulo_foto": nome_arquivo,
                    "caminho_origem": caminho_completo
                }
            )
            
            # Enviar o ponto atual individualmente para o servidor Qdrant
            client.upsert(
                collection_name=NOME_COLECAO,
                points=[point],
            )
            
            print(f"Vetor de {nome_arquivo} enviado com sucesso (ID: {contador_id}).")
            contador_id += 1
            sucessos += 1
            
        except Exception as e:
            print(f"Não foi possível processar ou enviar {nome_arquivo}. Motivo: {str(e)}")

print(f"Processo finalizado. Total de imagens salvas no banco: {sucessos}")