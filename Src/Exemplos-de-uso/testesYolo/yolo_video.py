from ultralytics import YOLO

modelo = YOLO("yolov8n.pt")

video_alvo = "./videos/road_traffic.mp4"

resultados = modelo.predict(
    source=video_alvo, 
    classes=[2],   # 2 é o ID para 'carro' no dataset COCO
    show=True,     # Abre uma janela mostrando o vídeo processado em tempo real
    save=True      # Salva o vídeo final com as Bounding Boxes na pasta runs/detect/predict
)