import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

# Pegando as variáveis do seu arquivo .env
QDRANT_URL = os.getenv("APIURL")
QDRANT_API_KEY = os.getenv("APITESTE")

print(f"Conectando ao Qdrant em: {QDRANT_URL}")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

NOME_COLECAO = "identidades_rostos"

try:
    if not client.collection_exists(collection_name=NOME_COLECAO):
        client.create_collection(
            collection_name=NOME_COLECAO,
            # ArcFace gera um vetor de 512 dimensões. Usamos similaridade por Cosseno.
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )
        print(f"✅ Coleção '{NOME_COLECAO}' criada com sucesso!")
    else:
        print(f"⚠️ A coleção '{NOME_COLECAO}' já existia.")
except Exception as e:
    print(f"❌ Erro ao criar a coleção: {e}")
