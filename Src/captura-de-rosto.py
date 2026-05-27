import os
import numpy as np
from deepface import DeepFace
import csv

# Exemplo de extração de embeddings com ArcFace
try:
    print("Inicializando o modelo ArcFace via DeepFace...")
    
    # Substitua pelo caminho da sua imagem de captura
    caminho_imagem = "Src/imagensdeTeste/imagemPerfil.jpeg" 
    
    embedding_objs = DeepFace.represent(
        img_path = caminho_imagem, 
        model_name = "ArcFace",
        enforce_detection = True  # Garante que um rosto precisa ser detectado
    )
    
    # O embedding é o vetor numérico que representa o rosto
    embedding = embedding_objs[0]["embedding"]


    nome_arquivo_csv = "Src/embedding_rosto.csv"

    with open(nome_arquivo_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Indice", "Valor_Embedding"])
        for i, valor in enumerate(embedding):
            writer.writerow([i, valor])

    print(f"Vetor exportado com sucesso para tabela em: {nome_arquivo_csv}")

except Exception as e:
    print("Ocorreu um erro durante o processamento:", str(e))