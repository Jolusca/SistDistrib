import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
import cv2
from ultralytics import YOLO

# 1. Carrega o modelo
model_path = '/home/lucas/git/SistDistrib/runs/detect/train-3/weights/best.pt'
modelo = YOLO(model_path)

# 2. Inicializa a captura fora do loop
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 3. Cria a janela uma única vez antes do loop
cv2.namedWindow("Detecção de Rosto - YOLOv8", cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Erro: Não foi possível ler a câmera.")
        break

    # 4. Predição com imgsz reduzido para velocidade
    resultados = modelo.predict(frame, conf=0.5, verbose=False, imgsz=320)
    
    # 5. Extrai o frame plotado
    frame_processado = resultados[0].plot()

    # 6. Exibe na janela já criada
    cv2.imshow("Detecção de Rosto - YOLOv8", frame_processado)
    
    # O waitKey é vital. O tempo de 1ms é o padrão para tempo real
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()