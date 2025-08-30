# API_MOBILAB

```

├── main.py                     # Onde sua aplicação FastAPI é inicializada e os endpoints são definidos.
├── database.py                 # Contém a configuração da conexão com o banco de dados e as definições dos modelos ORM (SQLAlchemy) para suas tabelas.
├── crud.py                     # Funções para interagir com o banco de dados (Criar, Ler, Atualizar, Deletar - CRUD). É a "camada de serviço" que a API usa para buscar/salvar dados.
├── models.py                   # Define os modelos de dados (Pydantic) que a API usará para validar requisições e formatar respostas.
├── .env                        # Arquivo para variáveis de ambiente (ex: URL de conexão com o banco de dados, chaves de API, etc.).
└── data_ingestion/             # Pasta que contém os scripts para coletar e processar seus dados brutos antes de inseri-los no banco.
    ├── __init__.py             # (Arquivo vazio para indicar que é um pacote Python)
    ├── ingest_manual_stations.py   # Script para ler CSVs de estações manuais e inseri-los no DB.
    ├── ingest_automatic_api.py     # Script para coletar dados de APIs externas de estações automáticas e inseri-los no DB.
    ├── calculate_vehicle_emissions.py # Script para calcular emissões a partir de dados de veículos (CSV).
    └── ingest_calculated_emissions.py # Script para inserir os dados de emissões calculadas no DB.

```