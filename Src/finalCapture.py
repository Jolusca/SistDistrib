import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace
import requests
import json
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do ambiente AWS
URL_AWS = os.getenv("API_AWS")
PORTA_ATUAL = "Catraca 01 - Entrada Principal"

def enviar_para_aws(embedding, face_img):
    try:
        # Converter o recorte do rosto (formato OpenCV) para Base64 (JPG)
        _, buffer = cv2.imencode('.jpg', face_img)
        foto_base64 = base64.b64encode(buffer).decode('utf-8')
        
        dados = {
            "vetor": embedding,
            "porta": PORTA_ATUAL,
            "foto_base64": foto_base64
        }
        
        print("\n Enviando biometria para a AWS...")
        resposta = requests.post(URL_AWS, json=dados, timeout=10)
        
        if resposta.status_code in [200, 403]:
            resp_json = resposta.json()
            mensagem = resp_json.get("mensagem", "Sem mensagem")
            nome_funcionario = resp_json.get("nome_funcionario", "Funcionário Desconhecido")
            print(f"AWS Respondeu [{resposta.status_code}]: {mensagem} - {nome_funcionario}")
            return mensagem, nome_funcionario
        else:
            print(f"Erro inesperado da AWS: {resposta.status_code} - {resposta.text}")
            return "Erro no Servidor", "Desconhecido"
            
    except Exception as e:
        print(f"Erro de conexão com a AWS: {e}")
        return "Erro de Conexão"

def iniciar_catraca():
    model = YOLO('modeloYoloTreinado.pt')

    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(os.getenv("QDRANT_URL").strip().rstrip('/'))
    
    ultimo_envio = 0
    COOLDOWN_SEGUNDOS = 5  # Espera 5 segundos após enviar uma foto para não sobrecarregar a AWS

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Faz a predição no frame com a YOLO
        results = model.predict(frame, conf=0.7, verbose=False)
        
        melhor_face = None
        melhor_conf = 0

        # Identifica a melhor face na tela
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].item()
                
                face = frame[y1:y2, x1:x2]
                if face.size == 0: continue
                
                area = (x2 - x1) * (y2 - y1)
                
                if conf > melhor_conf:
                    melhor_conf = conf
                    melhor_face = (x1, y1, x2, y2, face, area)

        # Se detectou rosto e já passou o tempo de espera (cooldown)
        tempo_atual = time.time()
        if melhor_face is not None and (tempo_atual - ultimo_envio > COOLDOWN_SEGUNDOS):
            (startX, startY, endX, endY, face, area) = melhor_face

            # Auditoria de qualidade da imagem
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            brilho = np.mean(gray)
            
            rosto_bom = (area > 5000 and brilho > 80 and brilho < 200 and melhor_conf > 0.90 and sharpness > 100)

            if rosto_bom:
                # Desenha quadrado amarelo na hora de processar
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 255), 2)
                #cv2.putText(frame, "Processando na Nuvem...", (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow("Sistema de Ponto Distribuido", frame)
                cv2.waitKey(1) # Força a atualização da janela instantaneamente
                
                print("\nGERANDO EMBEDDING LOCAL (ArcFace)...")
                resultado = DeepFace.represent(img_path=face, model_name="ArcFace", enforce_detection=False)
                embedding = resultado[0]["embedding"]
                
                # Chamada na AWS (Trava a execução até a AWS responder)
                status_acesso, nome_funcionario = enviar_para_aws(embedding, face)
                
                # Define a cor baseado na resposta (Verde para sucesso, Vermelho para erro/negado)
                cor_status = (0, 255, 0) if status_acesso == "Acesso Liberado" else (0, 0, 255)


                # Desenha a resposta na tela
                cv2.rectangle(frame, (startX, startY), (endX, endY), cor_status, 4)
                
                # Junta o Status e o Nome para escrever na tela
                texto_tela = f"{status_acesso} - {nome_funcionario}"
                cv2.putText(frame, texto_tela, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_status, 2)
                cv2.imshow("Sistema de Ponto Distribuido", frame)
                
                # Pausa a tela com a resposta por 2.5 segundos para a pessoa ler
                cv2.waitKey(2500) 
                
                # Atualiza o cronômetro para não processar nada nos próximos 5 segundos
                ultimo_envio = time.time() 
            else:
                # Desenha vermelho se a pessoa estiver muito longe/escura
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 1)

        cv2.imshow("Sistema de Ponto Distribuido", frame)
        if cv2.waitKey(1) == 27: # Pressione ESC no teclado para fechar
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Câmera desligada.")

if __name__ == "__main__":
    iniciar_catraca()