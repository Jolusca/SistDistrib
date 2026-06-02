import os
# Oculta mensagens informativas e avisos de alocação do TensorFlow/CUDA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging
# Desativa mensagens de log enviadas para o console por bibliotecas internas
logging.getLogger("tensorflow").setLevel(logging.ERROR)

from qdrant_client import QdrantClient
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv()
# print("URL do Banco:", os.getenv("APIURL"))

# Conectar ao Qdrant Cloud
client = QdrantClient(
    url=os.getenv("APIURL"),
    api_key=os.getenv("APITESTE")
)

NOME_COLECAO = "identidades_rostos"
caminho_pasta_busca = "/home/lucas/Downloads/frontal images B"

# print(f"Diretório de busca configurado: {caminho_pasta_busca}")

while True:
    # Captura o nome do arquivo e oferece uma opção de saída do laço
    nome_arquivo = input("\nDigite o nome do arquivo com a extensão (ou 'sair' para encerrar): ")
    
    if nome_arquivo.lower() in ['sair', 'exit', 'quit']:
        print("Programa encerrado.")
        break
        
    caminho_imagem_busca = os.path.join(caminho_pasta_busca, nome_arquivo)
    
    if os.path.exists(caminho_imagem_busca):
        try:
            # print(f"\nAnalisando a imagem de busca: {nome_arquivo}")
            
            # Extrair o vetor da nova imagem usando a mesma configuração (ArcFace)
            embedding_objs = DeepFace.represent(
                img_path=caminho_imagem_busca, 
                model_name="ArcFace",
                enforce_detection=True
            )
            
            embedding_busca = embedding_objs[0]["embedding"]
            
            # print("Consultando o vetor mais próximo no banco de dados...")
            
            resposta = client.query_points(
                collection_name=NOME_COLECAO,
                query=embedding_busca,
                limit=1,
                with_payload=True
            )
            
            if resposta and resposta.points:
                melhor_match = resposta.points[0]
                score_similaridade = melhor_match.score
                metadados = melhor_match.payload
                
                print("\n=== RESULTADO DA IDENTIFICAÇÃO ===")
                print(f"ID do Vetor no Banco: {melhor_match.id}")
                print(f"Nome do Arquivo Encontrado: {metadados.get('titulo_foto')}")
                print(f"Caminho da Foto Cadastrada: {metadados.get('caminho_origem')}")
                print(f"Métrica de Proximidade (Score): {score_similaridade:.4f}")
                print("====================================")
                
                if score_similaridade > 0.60:
                    print("Resultado confiável: Rosto reconhecido com sucesso.")
                else:
                    print("Atenção: O nível de similaridade é baixo. Pode ser uma pessoa diferente.")
            else:
                print("\nNenhum vetor correspondente foi localizado na coleção.")
                
        except Exception as e:
            print(f"\nFalha no processo de reconhecimento. Motivo: {str(e)}")
    else:
        print(f"\nErro: O arquivo '{nome_arquivo}' não existe em '{caminho_pasta_busca}'.")