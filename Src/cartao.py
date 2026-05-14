import cv2
import numpy as np


#cap = cv2.VideoCapture(http://usuario:senha@http://192.168.18.192:8080/video:8080/video)
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("http://192.168.18.192:8080/video")

# Limites da cor LARANJA no padrao HSV
laranja_claro = np.array([5, 100, 100])
laranja_escuro = np.array([22, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Converte o frame para HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Cria a mascara isolando apenas o que é laranja
    mascara = cv2.inRange(hsv, laranja_claro, laranja_escuro)
    
    # Encontra os contornos na máscara
    # Nota: A compatibilidade do findContours pode retornar 2 ou 3 variaveis dependendo da versao do OpenCV. 
    # Usar [-2:] garante que pegamos os contornos corretamente em qualquer versao.
    contornos = cv2.findContours(mascara, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        
        # Ignora manchas pequenas (ruído) - ajuste esse valor dependendo da altura da camera
        if area > 1000: 
            # Pega as coordenadas para desenhar o retangulo
            x, y, w, h = cv2.boundingRect(contorno)
            
            # Desenha o retangulo na imagem original (cor da caixa em BGR: Azul, Verde, Vermelho)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
            cv2.putText(frame, "Cartao Laranja", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

    cv2.imshow("Deteccao de Cartao Laranja", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()