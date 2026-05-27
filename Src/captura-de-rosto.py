import os
import numpy as np
from arcface import ArcFace

def extrair_e_salvar_vetor(caminho_imagem, caminho_txt):
    if not os.path.exists(caminho_imagem):
        print(f"Erro: A imagem '{caminho_imagem}' não foi encontrada.")
        return

    print("Inicializando o modelo ArcFace e processando a imagem...")
    try:
        # Inicializa a ferramenta de reconhecimento do ArcFace
        face_rec = ArcFace.ArcFace()
        
        # Calcula o embedding (vetor de características) da imagem
        vetor = face_rec.calc_emb(caminho_imagem)
        
        # Salva o vetor no arquivo de texto (um número por linha)
        np.savetxt(caminho_txt, vetor, fmt='%f')
        
        print("\nProcessamento concluído com sucesso!")
        print(f"Arquivo gerado: {caminho_txt}")
        print(f"Dimensões do vetor: {vetor.shape}")
        
    except Exception as erro:
        print(f"Ocorreu um erro durante o processamento: {erro}")

if __name__ == "__main__":
    # Defina aqui o nome da sua imagem e do arquivo de saída
    IMAGEM_ENTRADA = "Src/imagensdeTeste/imagemPerfil.jpeg"
    ARQUIVO_SAIDA = "vetor_rosto.txt"
    
    extrair_e_salvar_vetor(IMAGEM_ENTRADA, ARQUIVO_SAIDA)