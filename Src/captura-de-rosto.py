import cv2
import json
from deepface import DeepFace

def cadastrar_rosto_local(nome_funcionario, cpf_funcionario):
    cap = cv2.VideoCapture("http://192.168.18.19:8080/video")
    # cap = cv2.VideoCapture(0)
    print(f"Webcam iniciada. Cadastrando: {nome_funcionario}")
    print("Pressione 'C' para capturar o rosto ou 'Q' para cancelar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao acessar a câmera.")
            break

        cv2.imshow("Cadastro ArcFace", frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord('c'):
            print("\nProcessando a imagem... aguarde.")
            try:
                # Extrai o vetor matemático do rosto
                resultado = DeepFace.represent(
                    img_path=frame,
                    model_name="ArcFace",
                    enforce_detection=True
                )
                
                vetor = resultado[0]["embedding"]
                
                # Prepara o pacote de dados (Metadata + Embeddings)
                dados_cadastro = {
                    "nome": nome_funcionario,
                    "cpf": cpf_funcionario,
                    "vetor_biometrico": vetor
                }
                
                # Define o nome do arquivo usando o CPF para não haver duplicatas
                nome_arquivo = f"funcionario_{cpf_funcionario}.json"
                
                # Salva o arquivo localmente
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    json.dump(dados_cadastro, arquivo, indent=4)
                    
                print(f"SUCESSO: Rosto convertido e salvo em '{nome_arquivo}'!")
                break # Encerra o loop após salvar com sucesso

            except ValueError:
                print("AVISO: Nenhum rosto nítido encontrado no frame. Tente novamente.")

        elif tecla == ord('q'):
            print("Operação cancelada pelo usuário.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Simulação de dados recebidos de um formulário de RH
    nome = input("Digite o nome do funcionário: ")
    cpf = input("Digite o CPF do funcionário (apenas números): ")
    
    cadastrar_rosto_local(nome, cpf)