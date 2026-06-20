import cv2
import numpy as np
from ultralytics import YOLO

from deepface import DeepFace

def capturar_embedding():
    # Carrega o seu modelo treinado
    # Certifique-se que o caminho está correto
    model = YOLO('modeloYoloTreinado.pt') 

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # A YOLOv8 já lida com o redimensionamento internamente
        # Faz a predição no frame
        results = model.predict(frame, conf=0.7, verbose=False)
        
        melhor_face = None
        melhor_conf = 0

        # Processa os resultados
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Coordenadas do retângulo
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].item()
                
                # Recorta o rosto
                face = frame[y1:y2, x1:x2]
                if face.size == 0: continue
                
                # Área e lógica de qualidade
                area = (x2 - x1) * (y2 - y1)
                
                if conf > melhor_conf:
                    melhor_conf = conf
                    melhor_face = (x1, y1, x2, y2, face, area)

        if melhor_face is not None:
            (startX, startY, endX, endY, face, area) = melhor_face

            # Métricas de qualidade
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            brilho = np.mean(gray)

            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            
            # Critérios de qualidade
            rosto_bom = (area > 5000 and brilho > 80 and brilho < 200 and melhor_conf > 0.90 and sharpness > 100)

            if rosto_bom:
                print("GERANDO EMBEDDING...")
                resultado = DeepFace.represent(img_path=face, model_name="ArcFace", enforce_detection=False)
                embedding = resultado[0]["embedding"]
                
                cap.release()
                cv2.destroyAllWindows()
                return embedding

        cv2.imshow("Captura Inteligente YOLO", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    embedding = capturar_embedding()
    if embedding is not None:
        print("Embedding gerado com sucesso.")