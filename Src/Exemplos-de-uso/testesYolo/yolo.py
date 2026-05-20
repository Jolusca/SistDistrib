from ultralytics import YOLO

#Carrega o modelo pré-treinado de fábrica
# O final "n" significa "nano". Ele baixará o arquivo 'yolov8n.pt' automaticamente na primeira vez.
# Este modelo já sabe reconhecer 80 coisas comuns (pessoas, carros, cadeiras, celulares...)
modelo = YOLO("yolov8n.pt")

imagem_alvo = "./images/gol2.jpg"

resultados = modelo.predict(source=imagem_alvo, save=True, show=True)

for resultado in resultados:
    print("\n--- Relatório de Detecção ---")
    print(resultado.verbose())