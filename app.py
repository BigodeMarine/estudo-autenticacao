from typing import List, Optional, Literal
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import secrets

app = FastAPI(title="API de Tarefas com Auth + Paginação + Ordenação")

security = HTTPBasic()

USERS_DB = {
    "edson": "123",
}

class Tarefa(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    descricao: str = Field(min_length=1, max_length=200)
    concluida: bool = False

class MessageResponse(BaseModel):
    message: str

class TarefaResponse(BaseModel):
    message: str
    data: Tarefa

class TarefaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    descricao: str = Field(min_length=1, max_length=200)

tarefas: List[Tarefa] = [
    Tarefa(nome="Comprar coxinha", descricao="Ir na padaria", concluida=False),
    Tarefa(nome="Comprar livro", descricao="Ir na amazon", concluida=False),
    Tarefa(nome="Comprar jogo", descricao="Ir na steam", concluida=False),
]

def validar_credenciais(credentials: HTTPBasicCredentials) -> str:
    username = credentials.username
    password = credentials.password

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais ausentes.",
            headers={"WWW-Authenticate": "Basic"},
        )

    senha_esperada = USERS_DB.get(username)
    if senha_esperada is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Basic"},
        )
    ok_user = secrets.compare_digest(username, username)
    ok_pass = secrets.compare_digest(password, senha_esperada)

    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    return validar_credenciais(credentials)

OrderField = Literal["nome", "descricao", "concluida"]
OrderDir = Literal["asc", "desc"]

def aplicar_ordenacao(
    items: List[Tarefa],
    order_by: Optional[OrderField],
    order_dir: OrderDir,
) -> List[Tarefa]:
    if order_by is None:
        return items

    reverse = (order_dir == "desc")
    return sorted(items, key=lambda t: getattr(t, order_by), reverse=reverse)

def aplicar_paginacao(items: List[Tarefa], page: int, size: int) -> List[Tarefa]:
    start = (page - 1) * size
    end = start + size
    return items[start:end]

@app.get("/listar", response_model=List[Tarefa])
def listar_tarefas(
    user: str = Depends(auth_user), 
    page: int = Query(1, ge=1, description="Página (>=1)"), 
    size: int = Query(10, ge=1, le=100, description="Itens por página (1..100)"),
    order_by: Optional[OrderField] = Query(
        None,
        description="Campo para ordenar: nome | descricao | concluida",
    ), 
    order_dir: OrderDir = Query(
        "asc",
        description="Direção da ordenação: asc | desc",
    ),
):
    
    items = tarefas.copy()
    items = aplicar_ordenacao(items, order_by, order_dir)
    items = aplicar_paginacao(items, page, size)
    return items

@app.post("/criar", response_model=TarefaResponse, status_code=201)
def criar_tarefa(
    payload: TarefaCreate,
    user: str = Depends(auth_user),
):
    if any(t.nome == payload.nome for t in tarefas):
        raise HTTPException(
            status_code=409,
            detail="Já existe uma tarefa com esse nome.",
        )

    nova = Tarefa(nome=payload.nome, descricao=payload.descricao, concluida=False)
    tarefas.append(nova)
    return {
        "message": "Tarefa criada com sucesso.",
        "data": nova
    }

@app.put("/tarefas/{nome}/concluir", response_model=TarefaResponse)
def concluir_tarefa(
    nome: str,
    user: str = Depends(auth_user),
):
    for i, t in enumerate(tarefas):
        if t.nome == nome:
            tarefas[i] = t.model_copy(update={"concluida": True})
            return {
                "message": "Tarefa atualizada com sucesso.",
                "data": tarefas[i]
            }

    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

@app.delete("/remover/{nome}", response_model=MessageResponse, status_code=200)
def remover_tarefa(
    nome: str,
    user: str = Depends(auth_user),
):
    for i, t in enumerate(tarefas):
        if t.nome == nome:
            del tarefas[i]
            return {"message": "Tarefa removida com sucesso."}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")