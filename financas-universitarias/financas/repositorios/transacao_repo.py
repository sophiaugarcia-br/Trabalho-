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
        """, (transacao.tipo, transacao.descricao, transacao.valor_centavos, transacao.data, transacao.categoria_id, transacao.recorrencia_id))
        transacao.id = cursor.lastrowid
        return transacao

