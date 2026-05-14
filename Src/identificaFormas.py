import cv2
import numpy as np
try:
    # Tenta conectar à câmera IP
    #cap = cv2.VideoCapture(http://usuario:senha@http://192.168.18.192:8080/video:8080/video)
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("http://192.168.18.95:8080/video")
    if not cap.isOpened():
        raise Exception("Não foi possível conectar à câmera IP.")
except Exception as e:
    print(f"Erro ao conectar à câmera: {e}")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame.")
        break

    # Converte o frame para escala de cinza
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplica desfoque mais forte para reduzir ruídos
    cinza = cv2.GaussianBlur(cinza, (3, 3), 0)


    # --- Detecção de Círculos ---
    circulos = cv2.HoughCircles(
        cinza,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=50,
        param2=100,
        minRadius=10,
        maxRadius=1000
    )

    # Desenha os círculos detectados
    if circulos is not None:
        circulos = np.uint16(np.around(circulos))
        for circulo in circulos[0, :]:
            cv2.circle(frame, (circulo[0], circulo[1]), circulo[2], (0, 255, 0), 2)  # Circunferência
            cv2.circle(frame, (circulo[0], circulo[1]), 2, (0, 0, 255), 3)  # Centro
            cv2.putText(frame, "Circulo", (circulo[0] - 30, circulo[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # --- Detecção de Polígonos (Otimizada) ---
    # Aplica limiarização adaptativa para melhorar a detecção

    limiar = cv2.adaptiveThreshold(
        cinza, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 5
    )

    # Encontra contornos
    contornos, _ = cv2.findContours(limiar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        # Filtra contornos muito pequenos (ruído)
        if cv2.contourArea(contorno) < 1000:  # Aumenta o limite de área
            continue

        # Aproxima o contorno para um polígono
        epsilon = 0.05 * cv2.arcLength(contorno, True)  # Maior epsilon para menos detalhes
        aproximacao = cv2.approxPolyDP(contorno, epsilon, True)

        # Classifica a forma com base no número de vértices
        vertices = len(aproximacao)
        if vertices >= 3:  # Ignora formas com menos de 3 vértices
            if vertices == 3:
                forma = "Triangulo"
                cor = (0, 255, 0)  # Verde
            elif vertices == 4:
                # Verifica se é um quadrado ou retângulo
                (x, y, w, h) = cv2.boundingRect(aproximacao)
                aspecto = float(w) / h
                #forma = "Quadrado" if 0.95 <= aspecto <= 1.05 else "Retangulo"
                forma = "Retangulo"
                cor = (0, 0, 255)  # Vermelho
            elif vertices == 5:
                forma = "Pentagono"
                cor = (255, 0, 0)  # Azul
           # else:
            #    forma = f"Poligono ({vertices} lados)"
             #   cor = (255, 255, 0)  # Amarelo

            # Desenha o contorno e o nome da forma
            cv2.drawContours(frame, [aproximacao], 0, cor, 2)
            (x, y) = aproximacao[0][0]
            cv2.putText(frame, forma, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)

    cv2.imshow("Deteccao de Circulos e Poligonos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()