import cv2
from ultralytics import YOLO

# Configurações
stream_url = "http://192.168.18.103:8080/video"#Ajustar o IP para cada iteração
modelo = YOLO("yolov8n.pt")  # Modelo nano
frame_skip = 2  # Pula frames
frame_count = 0

# Abre o stream
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue

    # Detecção 2 Para carros, 11 para placa de pare
    resultados = modelo(frame, classes=[11], show=False)
    frame_processado = resultados[0].plot()

    # Exibe
    cv2.imshow("YOLO + Camera IP", frame_processado)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()