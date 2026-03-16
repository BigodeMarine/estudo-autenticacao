from typing import List, Optional, Literal
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import secrets
import sqlite3

app = FastAPI(title="API de Tarefas com Auth + Paginação + Ordenação")

security = HTTPBasic()

DATABASE = "tarefas.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabela():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT NOT NULL,
        concluida BOOLEAN NOT NULL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

criar_tabela()

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
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):

    conn = get_connection()
    cursor = conn.cursor()

    offset = (page - 1) * size

    cursor.execute(
        "SELECT nome, descricao, concluida FROM tarefas LIMIT ? OFFSET ?",
        (size, offset),
    )

    rows = cursor.fetchall()
    conn.close()

    return [Tarefa(**dict(row)) for row in rows]

@app.post("/criar", response_model=TarefaResponse, status_code=201)
def criar_tarefa(payload: TarefaCreate, user: str = Depends(auth_user)):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO tarefas (nome, descricao, concluida) VALUES (?, ?, ?)",
            (payload.nome, payload.descricao, False),
        )

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma tarefa com esse nome.",
        )

    conn.close()

    nova = Tarefa(nome=payload.nome, descricao=payload.descricao, concluida=False)

    return {
        "message": "Tarefa criada com sucesso.",
        "data": nova
    }

@app.put("/tarefas/{nome}/concluir", response_model=TarefaResponse)
def concluir_tarefa(nome: str, user: str = Depends(auth_user)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tarefas SET concluida = 1 WHERE nome = ?",
        (nome,),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    conn.commit()

    cursor.execute(
        "SELECT nome, descricao, concluida FROM tarefas WHERE nome = ?",
        (nome,),
    )

    row = cursor.fetchone()
    conn.close()

    tarefa = Tarefa(**dict(row))

    return {
        "message": "Tarefa atualizada com sucesso.",
        "data": tarefa
    }

@app.delete("/remover/{nome}", response_model=MessageResponse)
def remover_tarefa(nome: str, user: str = Depends(auth_user)):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tarefas WHERE nome = ?",
        (nome,),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    conn.commit()
    conn.close()

    return {"message": "Tarefa removida com sucesso."}