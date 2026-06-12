import cv2
import numpy as np
import time
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

prototxt_path = os.path.join(base_dir, "deploy.prototxt")
model_path = os.path.join(base_dir, "res10_300x300_ssd_iter_140000_fp16.caffemodel")

print(prototxt_path)
print(model_path)

net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
# Modelo OpenCV DNN
#net = cv2.dnn.readNetFromCaffe(
#    "res10_300x300_ssd_iter_140000_fp16.caffemodel"
#)

cap = cv2.VideoCapture(0)

foto_salva = False
ultimo_tempo = time.time()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    h, w = frame.shape[:2]

    # Blob para o detector
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    melhor_face = None
    melhor_conf = 0

    for i in range(detections.shape[2]):

        confidence = detections[0, 0, i, 2]

        if confidence > 0.7:

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            startX, startY, endX, endY = box.astype("int")

            face = frame[startY:endY, startX:endX]

            if face.size == 0:
                continue

            face_w = endX - startX
            face_h = endY - startY

            area = face_w * face_h

            # pega melhor rosto
            if confidence > melhor_conf:
                melhor_conf = confidence
                melhor_face = (
                    startX, startY,
                    endX, endY,
                    face,
                    area
                )

    if melhor_face is not None:

        startX, startY, endX, endY, face, area = melhor_face

        # brilho médio
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brilho = np.mean(gray)

        # desenha info
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)

        texto = f"Conf:{melhor_conf:.2f} Bright:{brilho:.0f} Sharp:{sharpness:.0f}"

        cv2.putText(
            frame,
            texto,
            (startX, startY - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

        # critérios mínimos
        rosto_bom = (
            area > 50000 and
            brilho > 80 and
            brilho < 200 and
            melhor_conf > 0.90 and
            sharpness >120
        )

        if rosto_bom and not foto_salva:

            caminho = r"C:\Users\AUGUSTO\Desktop\SistDistrib-main\SistDistrib-main\Src\Exemplos-de-uso\testesYolo\images\testefotowebcam.jpg"

            cv2.imwrite(caminho, face)

            print("FOTO CAPTURADA!")

            foto_salva = True

            time.sleep(1)

            break

    cv2.imshow("Captura Inteligente", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
