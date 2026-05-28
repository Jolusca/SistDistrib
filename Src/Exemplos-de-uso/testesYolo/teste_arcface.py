#AQUI É SÓ UM TESTE DO ARCFACE COM UMA FOTO QUALQUER, 
#PARA VER SE O EMBEDDING ESTÁ FUNCIONANDO CORRETAMENTE.



from deepface import DeepFace

resultado = DeepFace.represent(
    img_path=r"Src\Exemplos-de-uso\testesYolo\images\FOTO.jpeg",
    model_name="ArcFace"
)

embedding = resultado[0]["embedding"]

print("Tamanho do embedding:", len(embedding))
print(embedding[:10])  # primeiros 10 valores
