# Planejamento de Projeto: Sistema de Ponto Eletrônico Distribuído

## 1. Visão Geral

O sistema visa automatizar o registro de jornada de trabalho através de visão computacional e arquitetura distribuída. A solução utiliza o processamento na borda (Edge) para reduzir o consumo de banda e serviços em nuvem para inteligência e persistência de dados.



## 2. Arquitetura do Sistema

* **Módulo Local (Edge Computing):**
* Captura do vídeo através da câmera do celular com o app ipCAM
* Execução de algoritmo de detecção de geometria em tempo real.
* Captura de frame estático apenas sob detecção de gatilho (cartão de identificação).
* Envio assíncrono da imagem para armazenamento em nuvem.


* **Módulo Nuvem (Cloud Serverless):**
* **Armazenamento:** Repositório de imagens para auditoria e processamento.
* **Processamento:** Função orquestradora disparada por eventos de upload.
* **OCR & Inteligência:** Serviço especializado para extração de caracteres e identificação de nomes.
* **Persistência:** Banco de dados externo para armazenamento dos registros de ponto.





## 3. Requisitos de Sistema

### 3.1. Requisitos Funcionais

1. **Detecção de ROI:** O sistema deve identificar localmente a região de interesse (cartão) no fluxo de vídeo.
2. **Upload por Evento:** A imagem deve ser enviada para a nuvem apenas quando um cartão for detectado.
3. **Extração de Dados:** O sistema deve converter a imagem em texto para identificar o nome do funcionário.
4. **Sincronização de Horário:** O registro deve conter o timestamp preciso do momento da captura.
5. **Integração Externa:** Os dados processados devem ser salvos em um banco de dados NoSQL remoto.

### 3.2. Requisitos Não Funcionais

1. **Eficiência de Rede:** Ocupação mínima de banda larga, evitando streaming de vídeo para a nuvem.
2. **Escalabilidade:** Capacidade de processar múltiplas requisições simultâneas de diferentes pontos de acesso.
3. **Disponibilidade:** Operação baseada em serviços sob demanda, garantindo funcionamento contínuo sem gestão de servidores.
4. **Auditabilidade:** Manutenção da imagem original como evidência do registro de ponto.



## 4. Fluxo de Funcionamento

1. O funcionário apresenta o cartão à câmera local.
2. O software de borda detecta o retângulo do cartão e captura uma foto.
3. A foto é enviada para o serviço de armazenamento (S3).
4. O upload dispara uma função (Lambda) que solicita o OCR ao serviço de IA (Textract).
5. O nome extraído e o horário são validados e enviados para o banco de dados final (Firebase/DynamoDB).


## 5. Estrutura de Diretórios do Projeto

```text
sistema-ponto-distribuido/
├── edge_node/                  # Código que roda localmente na câmera
│   ├── main.py                 # Loop principal do OpenCV e captura
│   ├── uploader.py             # Lógica de envio de arquivos para o S3
│   └── requirements.txt        # Dependências locais (opencv-python, boto3)
│
└── cloud_serverless/           # Código que será implantado na AWS
    ├── lambda_function.py      # Código orquestrador do AWS Lambda
    └── iam_policy.json         # Permissões de segurança para os serviços