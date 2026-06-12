import cv2
# OpenCV: captura vídeo da webcam, processa imagens e desenha elementos na tela

import numpy as np
# NumPy: usado para operações matemáticas e manipulação de arrays

import os
# Permite trabalhar com caminhos de arquivos e diretórios

from deepface import DeepFace
# Biblioteca que contém o ArcFace e outros modelos de reconhecimento facial


def capturar_embedding():
    """
    Função principal.
    Ela abre a webcam, espera encontrar um rosto com boa qualidade
    e retorna o embedding de 512 dimensões gerado pelo ArcFace.
    """

    # Descobre automaticamente a pasta onde o script está
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho para os arquivos do detector facial OpenCV
    prototxt_path = os.path.join(base_dir, "deploy.prototxt")
    model_path = os.path.join(
        base_dir,
        "res10_300x300_ssd_iter_140000_fp16.caffemodel"
    )

    # Carrega o detector facial da OpenCV
    net = cv2.dnn.readNetFromCaffe(
        prototxt_path,
        model_path
    )

    # Abre a webcam padrão do computador
    cap = cv2.VideoCapture(0)

    # Loop principal da câmera
    while True:

        # Captura um frame da webcam
        ret, frame = cap.read()

        # Se não conseguiu capturar, tenta novamente
        if not ret:
            continue

        # Altura e largura da imagem
        h, w = frame.shape[:2]

        # Converte a imagem para o formato esperado pelo detector facial
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )

        # Envia a imagem para a rede neural
        net.setInput(blob)

        # Executa a detecção facial
        detections = net.forward()

        # Variáveis para armazenar a melhor face encontrada
        melhor_face = None
        melhor_conf = 0

        # Percorre todas as detecções encontradas
        for i in range(detections.shape[2]):

            # Confiança da detecção
            confidence = detections[0, 0, i, 2]

            # Ignora detecções ruins
            if confidence < 0.7:
                continue

            # Obtém as coordenadas do retângulo facial
            box = (
                detections[0, 0, i, 3:7]
                * np.array([w, h, w, h])
            )

            startX, startY, endX, endY = box.astype("int")

            # Evita coordenadas fora da imagem
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w, endX)
            endY = min(h, endY)

            # Recorta apenas a região do rosto
            face = frame[startY:endY, startX:endX]

            # Se o recorte ficou vazio, ignora
            if face.size == 0:
                continue

            # Dimensões do rosto
            face_w = endX - startX
            face_h = endY - startY

            # Área do rosto
            area = face_w * face_h

            # Mantém apenas a face com maior confiança
            if confidence > melhor_conf:

                melhor_conf = confidence

                melhor_face = (
                    startX,
                    startY,
                    endX,
                    endY,
                    face,
                    area
                )

        # Se encontrou alguma face
        if melhor_face is not None:

            (
                startX,
                startY,
                endX,
                endY,
                face,
                area
            ) = melhor_face

            # Converte para escala de cinza
            gray = cv2.cvtColor(
                face,
                cv2.COLOR_BGR2GRAY
            )

            # Mede a nitidez usando Laplaciano
            # Quanto maior, mais focada está a imagem
            sharpness = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # Mede brilho médio
            brilho = np.mean(gray)

            # Desenha retângulo verde ao redor do rosto
            cv2.rectangle(
                frame,
                (startX, startY),
                (endX, endY),
                (0, 255, 0),
                2
            )

            # Texto exibido na tela
            texto = (
                f"Conf:{melhor_conf:.2f} "
                f"Bright:{brilho:.0f} "
                f"Sharp:{sharpness:.0f}"
            )

            # Escreve informações acima do rosto
            cv2.putText(
                frame,
                texto,
                (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Critérios mínimos para aceitar a foto
            rosto_bom = (
                area > 50000 and      # rosto suficientemente grande
                brilho > 80 and       # não muito escuro
                brilho < 200 and      # não muito claro
                melhor_conf > 0.90 and
                sharpness > 120       # rosto focado
            )

            # Se passou em todos os testes
            if rosto_bom:

                print("GERANDO EMBEDDING...")

                # Gera o embedding ArcFace
                resultado = DeepFace.represent(
                    img_path=face,
                    model_name="ArcFace",
                    enforce_detection=False
                )

                # Vetor de 512 dimensões
                embedding = resultado[0]["embedding"]

                print("Embedding gerado.")
                print("Tamanho:", len(embedding))

                # Fecha webcam e janelas
                cap.release()
                cv2.destroyAllWindows()

                # Retorna o embedding para quem chamou a função
                return embedding

        # Mostra a imagem da webcam
        cv2.imshow(
            "Captura Inteligente",
            frame
        )

        # ESC fecha o programa
        tecla = cv2.waitKey(1)

        if tecla == 27:
            break

    # Libera recursos caso o usuário feche manualmente
    cap.release()
    cv2.destroyAllWindows()

    return None


# Executa apenas quando este arquivo é rodado diretamente
if __name__ == "__main__":

    embedding = capturar_embedding()

    if embedding is not None:

        print("\nPrimeiros 10 valores:")

        # Mostra apenas os 10 primeiros números
        print(embedding[:10])