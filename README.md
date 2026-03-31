Estudo de autenticação / (Código refatorado)

API REST desenvolvida em Python + FastAPI e SQlite para o banco de dados.

Tecnologias utilizadas

Python 3.13

FastAPI

Uvicorn

Pydantic

Poetry (gerenciamento de dependências)

HTTP Basic Authentication  

SQlite  

Docker  

Docker Compose

Funcionalidades

✅ Autenticação básica por usuário e senha  
✅ CRUD de tarefas  
✅ Paginação nos endpoints  
✅ Ordenação dinâmica dos resultados  
✅ Respostas padronizadas com mensagens de sucesso  
✅ Tratamento de erros HTTP  
✅ Substituindo o uso do dicionário para o armazenamento de dados por um banco de dados SQLite.  

⚙️ Como executar o projeto:  

1. Clonar o repositório:  
git clone https://github.com/BigodeMarine/estudo-autenticacao.git  
cd estudo-autenticacao  

2. Subir a aplicação com Docker:  
docker compose up --build -d  

3. Acessar a API  

Abra no navegador:  

http://localhost:8000/docs  

4. Parar containers:  
docker compose down  

5. Rebuild da aplicação:  
docker compose up --build  
  
🔐 Autenticação

A API utiliza HTTP Basic Auth.

Crie um arquivo .env na raiz:

APP_USER=edson
APP_PASSWORD=123
DATABASE=/app/data/tarefas.db

Todos os endpoints de tarefas exigem autenticação.
