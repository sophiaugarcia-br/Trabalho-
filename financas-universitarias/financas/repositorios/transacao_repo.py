import sqlite3
from financas.modelos.transacao import Transacao
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

def _row_para_transacao(row: sqlite3.Row) -> Transacao: 
    return Transacao(**dict(row))

def criar(transacao: Transacao) -> Transacao: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            INSERT INTO transacoes (tipo, descricao, valor_centavos, data, categoria_id, recorrencia_id) VALUES (?, ?, ?, ?, ?, ?);
        """, (transacao.tipo, transacao.descricao, transacao.valor_centavos, transacao.data.isoformat(), transacao.categoria_id, transacao.recorrencia_id))
        transacao.id = cursor.lastrowid
        return transacao

def buscar_por_id(transacao_id: int) -> Transacao | None: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE id = ?;", (transacao_id,))
            row = cursor.fetchone()
            return _row_para_transacao(row) if row else None

def atualizar(transacao: Transacao) -> bool: 
    if transacao.id is None:
        raise ValueError("Erro: Transacao.id não pode ser nulo.") 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            UPDATE transacoes 
            SET tipo = ?,
                descricao = ?,
                valor_centavos = ?,
                data = ?,
                categoria_id = ?,
                recorrencia_id = ?
            WHERE id = ?;""", (transacao.tipo, transacao.descricao, transacao.valor_centavos, transacao.data.isoformat(), transacao.categoria_id, transacao.recorrencia_id, transacao.id))
            return cursor.rowcount > 0

def excluir(transacao_id: int) -> bool: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM transacoes WHERE id = ?;", (transacao_id,))
            return cursor.rowcount > 0

def listar_por_periodo(data_inicio: date, data_fim: date) -> list[Transacao]: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE data BETWEEN ? AND ? ORDER BY data DESC, id DESC;", (data_inicio.isoformat(), data_fim.isoformat()))
            manyrows = cursor.fetchall()
            return [_row_para_transacao(row) for row in manyrows]