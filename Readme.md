
# Planejamento de Projeto: Sistema de Ponto Eletrônico Distribuído (Versão CNN ONNX)

## 1. Visão Geral

O sistema visa automatizar o registro de jornada de trabalho através de visão computacional e arquitetura distribuída. A solução utiliza um cliente de captura leve na borda (Edge) e centraliza a inteligência de processamento de imagens e extração de dados em uma infraestrutura em nuvem totalmente baseada no modelo Serverless, garantindo escalabilidade e baixo custo operacional.

---

## 2. Arquitetura do Sistema

* **Módulo Local (Edge / Cliente Leve):**
* Conexão ao fluxo de vídeo gerado pelo aplicativo IP Webcam via celular.
* Captura periódica de frames estáveis da transmissão de vídeo.
* Identificação de rosto e de texto no cartão. 
* Envio assíncrono e direto da imagem bruta para o armazenamento em nuvem.



* **Módulo Nuvem (Cloud Serverless & IA Baseada em CPU):**
* **Armazenamento:** Amazon S3 recebe o upload do frame bruto gerado pela borda.
* **Processamento e IA (AWS Lambda + ONNX):** Função executada via container que carrega a CNN própria (exportada em formato ONNX) usando a biblioteca leve onnxruntime. A função executa o processamento de imagem (PDI) na nuvem para segmentar o cartão e ler os dados.
* **Persistência:** Amazon DynamoDB armazena as strings com o espelho de ponto e as chaves de acesso do arquivo no S3.



---

## 3. Requisitos de Sistema

### 3.1. Requisitos Funcionais

1. **Consumo de Stream de Vídeo:** O nó local deve se conectar ao endereço IP fornecido pelo aplicativo de captura para coletar os quadros.
2. **Envio por Evento de Tempo:** O cliente de borda deve enviar capturas pontuais para a nuvem de forma assíncrona.
3. **Inferência por Deep Learning:** O ecossistema de nuvem deve carregar a CNN customizada em formato ONNX para processar o frame recebido.
4. **Extração de Texto:** O sistema deve isolar e converter os caracteres da imagem processada para recuperar a identificação do funcionário.
5. **Persistência Centralizada:** Gravação imediata dos dados validados em um banco de dados NoSQL.

### 3.2. Requisitos Não Funcionais

1. **Leveza na Borda:** O script local não realiza inferências pesadas de machine learning, permitindo execução em hardware básico.
2. **Uso Eficiente de CPU na Nuvem:** A execução do modelo convertido para ONNX dispensa o provisionamento caro de instâncias com placas de vídeo (GPU) dedicadas.
3. **Isolamento de Dependências:** O código do backend deve ser empacotado em um container Docker para suportar o runtime de inferência matemática e manipulação de matrizes de pixels no AWS Lambda.
4. **Escalabilidade Elástica:** Criação de instâncias paralelas da função de IA de acordo com o volume de uploads simultâneos no S3.

---

## 4. Fluxo de Funcionamento

1. O aplicativo IP Webcam transmite o vídeo do celular na rede local.
2. O script do nó de borda acessa esse stream, extrai um frame limpo e envia o arquivo para o Amazon S3.
3. O Amazon S3 aciona de forma automática o gatilho da função AWS Lambda.
4. A AWS Lambda (rodando a imagem de container) executa a inferência da CNN via onnxruntime na CPU para processar o arquivo.
5. O texto traduzido e as informações de data/hora são enviados para gravação definitiva na tabela do Amazon DynamoDB.

---

## 5. Estrutura de Diretórios do Projeto

```text
sistema-ponto-distribuido/
├── edge_node/                  # Cliente leve de captura local
│   ├── main.py                 # Conexão com IP Webcam e extração de frames
│   ├── uploader.py             # Envio direto das fotos para o Amazon S3
│   └── requirements.txt        # Dependências locais (opencv-python, boto3)
│
└── cloud_serverless/           # Ambiente de processamento e IA na nuvem
    ├── app/
    │   ├── lambda_function.py  # Script de processamento e execução do ONNX
    │   └── modelo_ponto.onnx   # Pesos e arquitetura da CNN treinada e exportada
    ├── Dockerfile              # Configuração do ambiente (onnxruntime, opencv-headless)
    └── iam_policy.json         # Políticas de acesso ao S3 e DynamoDB

```