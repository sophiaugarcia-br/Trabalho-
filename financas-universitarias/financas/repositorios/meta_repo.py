import sqlite3
from financas.modelos.meta import Meta
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date
from typing import Literal

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row
aos atributos de um objeto da classe Meta"""
def _row_para_meta(row: sqlite3.Row) -> Meta: 
    return Meta(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Meta' fornecido pelo usuário
def criar(meta: Meta) -> Meta: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT INTO metas (produto, preco_centavos, criada_em, guardado_centavos, status, concluida_em, prazo) VALUES (?, ?, ?, ?, ?, ?, ?);", 
                (
                    meta.produto, 
                    meta.preco_centavos, 
                    meta.criada_em.isoformat(), 
                    meta.guardado_centavos, 
                    meta.status, 
                    meta.concluida_em.isoformat() if meta.concluida_em is not None else None, 
                    meta.prazo.isoformat() if meta.prazo is not None else None
                )
            )
        meta.id = cursor.lastrowid
        return meta

# Função de busca de uma meta que corresponda ao id dela fornecido
def buscar_por_id(meta_id: int) -> Meta | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM metas WHERE id = ?;", (meta_id,))
        row = cursor.fetchone()
        return _row_para_meta(row) if row else None

# Função que consiste em atualizar os atributos de uma meta já criada pelo id dela
def atualizar(meta: Meta) -> bool:
    if meta.id is None: 
        raise ValueError("Erro: Meta.id não pode ser nulo.")
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            UPDATE metas
            SET produto = ?, 
                preco_centavos = ?, 
                criada_em = ?, 
                guardado_centavos = ?, 
                status = ?, 
                concluida_em = ?, 
                prazo = ?
            WHERE id = ?;
            """, (
                meta.produto, 
                meta.preco_centavos, 
                meta.criada_em.isoformat(), 
                meta.guardado_centavos, 
                meta.status, 
                meta.concluida_em.isoformat() if meta.concluida_em is not None else None, 
                meta.prazo.isoformat() if meta.prazo is not None else None, 
                meta.id
            ))
        return cursor.rowcount > 0

# Função excludente de meta de específico id
def excluir(meta_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM metas WHERE id = ?;", (meta_id,))
        return cursor.rowcount > 0

# Função listadora das metas de status (aberta ou concluida) indicado
def listar_por_status(status: Literal["ABERTA", "CONCLUIDA"]) -> list[Meta]: 
    status = status.strip().upper() # type: ignore
    if status not in ("ABERTA", "CONCLUIDA"): 
        raise ValueError(f"O Meta.status digitado ({status}) deve ser 'ABERTA' ou 'CONCLUIDA'.")
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM metas 
            WHERE status = ?
            ORDER BY id;
        """, (status,))
        return [_row_para_meta(row) for row in cursor.fetchall()]

# Função listadora das metas dentro do prazo proposto
def listar_por_prazo(prazo_min: date, prazo_max: date) -> list[Meta]: 
    if type(prazo_max) is not date or type(prazo_min) is not date: 
        raise TypeError("Erro: tipo de dado deve ser 'date', e nem prazo_max, nem prazo_min podem ser nulos.")
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM metas
            WHERE prazo BETWEEN ? AND ?
            ORDER BY prazo ASC, id ASC;
        """, (prazo_min.isoformat(), prazo_max.isoformat()))
        return [_row_para_meta(row) for row in cursor.fetchall()]

# Listagem geral dos investimentos de ordenação ascendente pelo status deles
def listar_todas() -> list[Meta]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM metas ORDER BY status ASC, id ASC;")
        return [_row_para_meta(row) for row in cursor.fetchall()]