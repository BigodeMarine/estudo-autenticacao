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

Funcionalidades

✅ Autenticação básica por usuário e senha  
✅ CRUD de tarefas  
✅ Paginação nos endpoints  
✅ Ordenação dinâmica dos resultados  
✅ Respostas padronizadas com mensagens de sucesso  
✅ Tratamento de erros HTTP  
✅ Substituindo o uso do dicionário para o armazenamento de dados por um banco de dados SQLite.

🔐 Autenticação

A API utiliza HTTP Basic Auth.

Usuários de teste:

edson / 123

Todos os endpoints de tarefas exigem autenticação.
