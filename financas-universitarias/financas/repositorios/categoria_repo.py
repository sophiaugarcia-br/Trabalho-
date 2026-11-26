import sqlite3
from financas.modelos.categoria import Categoria
from financas.repositorios.banco import conectar
from contextlib import closing
from typing import Literal

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row
aos atributos de um objeto da classe Categoria"""
def _row_para_categoria(row: sqlite3.Row) -> Categoria: 
    return Categoria(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Categoria' fornecido pelo usuário
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

# Função de busca de uma categoria que corresponda ao id dela fornecido
def buscar_por_id(categoria_id: int) -> Categoria | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM categorias WHERE id = ?;", (categoria_id,))
        row = cursor.fetchone()
        return _row_para_categoria(row) if row else None

# Função que consiste em atualizar os atributos de uma categoria já criada pelo id dela
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

# Função excludente de categoria de específico id
def excluir(categoria_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM categorias WHERE id = ?;", (categoria_id,))
        return cursor.rowcount > 0

# Função de listagem das categorias de determinado tipo (entrada ou saida) ordenada pelo nome
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

# Listagem geral das categorias de ordenação ascendente pelo nome
def listar_todas() -> list[Categoria]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM categorias ORDER BY nome ASC;")
        return [_row_para_categoria(row) for row in cursor.fetchall()]