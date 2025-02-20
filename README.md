# FastAPI MongoDB API

Uma API REST simples construída com FastAPI e MongoDB.

## Pré-requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)
- Conexão com internet (para acessar MongoDB Atlas)

## Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd <pasta-do-projeto>
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

O projeto já está configurado para usar MongoDB Atlas. As credenciais estão no arquivo `.env`.

## Executando a API

1. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

2. A API estará disponível em:
- http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

## Endpoints Disponíveis

- `GET /`: Página inicial
- `POST /products/`: Criar um novo produto
- `GET /products/`: Listar todos os produtos
- `GET /products/{id}`: Buscar produto por ID

## Estrutura do Projeto

```
trabalho_03/
├── app/
│   ├── config/
│   │   └── database.py
│   ├── models/
│   │   └── product.py
│   ├── repositories/
│   │   └── product_repository.py
│   ├── routes/
│   │   └── product_routes.py
│   └── main.py
├── requirements.txt
├── .env
└── README.md
```

## Exemplo de Uso

Para criar um novo produto:
```bash
curl -X 'POST' \
  'http://localhost:8000/products/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Produto Teste",
  "description": "Descrição do Produto",
  "price": 99.99
}'
```
