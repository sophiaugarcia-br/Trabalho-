import sqlite3
from financas.modelos.categoria import Categoria
from financas.repositorios.banco import conectar
from contextlib import closing
from typing import Literal

def _row_para_categoria(row: sqlite3.Row) -> Categoria: 
    return Categoria(**dict(row))

def criar(categoria: Categoria) -> Categoria: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT INTO categorias (nome, tipo, cor) VALUES (?, ?, ?);", 
                (
                    categoria.nome, 
                    categoria.tipo, 
                    categoria.cor
                )
            )
        categoria.id = cursor.lastrowid
        return categoria

def buscar_por_id(categoria_id: int) -> Categoria | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM categorias WHERE id = ?;", (categoria_id,))
        row = cursor.fetchone()
        return _row_para_categoria(row) if row else None

def atualizar(categoria: Categoria) -> bool:
    if categoria.id is None: 
        raise ValueError("Erro: Categoria.id não pode ser nulo.")
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            UPDATE categorias
            SET nome = ?, 
                tipo = ?, 
                cor = ?
            WHERE id = ?;
            """, (
                categoria.nome, 
                categoria.tipo, 
                categoria.cor, 
                categoria.id
            ))
        return cursor.rowcount > 0

def excluir(categoria_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM categorias WHERE id = ?;", (categoria_id,))
        return cursor.rowcount > 0

def listar_por_tipo(tipo: Literal["ENTRADA", "SAIDA"]) -> list[Categoria]: 
    tipo = tipo.strip().upper() # type: ignore
    if tipo not in ("ENTRADA", "SAIDA"): 
        raise ValueError(f"O Categoria.tipo digitado ({tipo}) deve ser 'ENTRADA' ou 'SAIDA'.")
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM categorias 
            WHERE tipo = ?
            ORDER BY nome ASC;
        """, (tipo,))
        return [_row_para_categoria(row) for row in cursor.fetchall()]

def listar_todas() -> list[Categoria]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM categorias ORDER BY nome ASC;")
        return [_row_para_categoria(row) for row in cursor.fetchall()]