import sqlite3
from financas.modelos.recorrencia import Recorrencia
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

def _row_para_recorrencia(row: sqlite3.Row) -> Recorrencia: 
    return Recorrencia(**dict(row))

def criar(recorrencia: Recorrencia) -> Recorrencia: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT INTO recorrencias (tipo, descricao, valor_centavos, periodicidade, dia, data_inicio, data_fim, categoria_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", 
                (
                    recorrencia.tipo, 
                    recorrencia.descricao, 
                    recorrencia.valor_centavos, 
                    recorrencia.periodicidade, 
                    recorrencia.dia, 
                    recorrencia.data_inicio.isoformat(), 
                    recorrencia.data_fim.isoformat() if recorrencia.data_fim is not None else None, 
                    recorrencia.categoria_id
                )
            )
        recorrencia.id = cursor.lastrowid
        return recorrencia

def buscar_por_id(recorrencia_id: int) -> Recorrencia | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM recorrencias WHERE id = ?;", (recorrencia_id,))
        row = cursor.fetchone()
        return _row_para_recorrencia(row) if row else None

def atualizar(recorrencia: Recorrencia) -> bool:
    if recorrencia.id is None: 
        raise ValueError("Erro: Recorrencia.id não pode ser nulo.")
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            UPDATE recorrencias
            SET tipo = ?, 
                descricao = ?, 
                valor_centavos = ?, 
                periodicidade = ?, 
                dia = ?, 
                data_inicio = ?, 
                data_fim = ?, 
                categoria_id = ?
            WHERE id = ?;
            """, (
                    recorrencia.tipo, 
                    recorrencia.descricao, 
                    recorrencia.valor_centavos, 
                    recorrencia.periodicidade, 
                    recorrencia.dia, 
                    recorrencia.data_inicio.isoformat(), 
                    recorrencia.data_fim.isoformat() if recorrencia.data_fim is not None else None, 
                    recorrencia.categoria_id, 
                    recorrencia.id
            ))
        return cursor.rowcount > 0

def excluir(recorrencia_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM recorrencias WHERE id = ?;", (recorrencia_id,))
        return cursor.rowcount > 0

def listar_ativas(data_ref: date) -> list[Recorrencia]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM recorrencias
        WHERE data_inicio <= ? AND (data_fim IS NULL OR data_fim >= ?);""", (data_ref.isoformat(), data_ref.isoformat()))
        return [_row_para_recorrencia(row) for row in cursor.fetchall()]

def listar_todas() -> list[Recorrencia]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM recorrencias ORDER BY dia ASC;")
        return [_row_para_recorrencia(row) for row in cursor.fetchall()]