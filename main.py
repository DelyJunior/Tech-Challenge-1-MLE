from fastapi import FastAPI, Query, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import pandas as pd   
from fastapi.responses import JSONResponse
import os
import sqlite3


app = FastAPI(
    title="API Tech Challenge",
    version="1.0.0",
    description="Trabalho Fase 1"
    )


# Caminho do banco de dados
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "challenge1.sqlite")

# Função utilitária para consultar o banco
def query_db(query: str, params: tuple = ()):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Retorna como dicionário
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Home
@app.get("/")
async def home():
    return "Hello, FastAPI!"

################################################################
#################### Endpoints Obrigatórios ####################
################################################################

# lista todos os livros disponíveis na base de dados
@app.get("/api/v1/books")
async def get_books():
    query = """
        SELECT titulo
        FROM books_details
        WHERE disponibilidade > 0
    """
    livros = query_db(query)
    return {"livros_disponiveis": livros}



# retorna detalhes completos de um livro específico pelo ID
@app.get("/api/v1/books/{id:int}")
async def get_book(id: int):
    query = """
        SELECT rowid as ID, *
        FROM books_details
        WHERE rowid = ?
    """
    result = query_db(query, (id,))
    if not result:
        return {"error": "Livro não encontrado"}
    return result[0]

# busca livros por título e/ou categoria
@app.get("/api/v1/books/search")
async def search_books(
    title: str = Query(None, description="Título ou parte do título do livro"),
    category: str = Query(None, description="Categoria ou parte da categoria")
):
    query = "SELECT rowid as ID, titulo, categoria, disponibilidade FROM books_details WHERE 1=1"
    params = []

    if title:
        query += " AND titulo LIKE ?"
        params.append(f"%{title}%")
    if category:
        query += " AND categoria LIKE ?"
        params.append(f"%{category}%")

    livros = query_db(query, tuple(params))
    return {"resultado": livros}

# lista todas as categorias disponíveis
@app.get("/api/v1/categories")
async def get_categories():
    query = """
        SELECT DISTINCT categoria
        FROM books_details
        WHERE disponibilidade > 0
    """
    categorias = query_db(query)
    return {"Categorias_disponiveis": categorias}

# verifica status da API e conectividade com os dados
@app.get("/api/v1/health")
async def health_check():
    if not os.path.exists(DB_FILE):
        return {"status": "error", "detail": "Banco de dados não encontrado"}
    try:
        result = query_db("SELECT COUNT(*) as total FROM books_details")
    except Exception as e:
        return {"status": "error", "detail": f"Erro ao ler BD: {str(e)}"}
    return {"status": "ok", "total_livros": result[0]["total"]}
