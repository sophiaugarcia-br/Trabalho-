import sqlite3
from financas.modelos.transacao import Transacao
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date
from typing import Literal

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row aos atributos de um objeto da classe Transacao"""
def _row_para_transacao(row: sqlite3.Row) -> Transacao: 
    return Transacao(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Transacao' fornecido pelo usuário
def criar(transacao: Transacao) -> Transacao: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            INSERT INTO transacoes (tipo, descricao, valor_centavos, data, categoria_id, recorrencia_id) VALUES (?, ?, ?, ?, ?, ?);
        """, (transacao.tipo, transacao.descricao, transacao.valor_centavos, transacao.data.isoformat(), transacao.categoria_id, transacao.recorrencia_id))
        transacao.id = cursor.lastrowid
        return transacao

# Função de busca de uma transacao que corresponda ao id dela fornecido
def buscar_por_id(transacao_id: int) -> Transacao | None: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE id = ?;", (transacao_id,))
            row = cursor.fetchone()
            return _row_para_transacao(row) if row else None

# Função que consiste em atualizar os atributos de uma transacao já criada pelo id dela
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

# Função excludente de transacao de específico id
def excluir(transacao_id: int) -> bool: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM transacoes WHERE id = ?;", (transacao_id,))
            return cursor.rowcount > 0

# Função que lista as transacoes ocorridas no período apontado
def listar_por_periodo(data_inicio: date, data_fim: date) -> list[Transacao]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM transacoes WHERE data BETWEEN ? AND ? ORDER BY data DESC, id DESC;", (data_inicio.isoformat(), data_fim.isoformat()))
        manyrows = cursor.fetchall()
        return [_row_para_transacao(row) for row in manyrows]

# Função que lista as transacoes do tipo 'ENTRADA' ou 'SAIDA'
def listar_por_tipo(tipo: Literal["ENTRADA", "SAIDA"]) -> list[Transacao]: 
    tipo = tipo.strip().upper() # type: ignore
    if tipo not in ("ENTRADA", "SAIDA"): 
        raise ValueError("Erro: 'tipo' da transacao deve ser 'ENTRADA' ou 'SAIDA'.")
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT * FROM transacoes
        WHERE tipo = ?
        ORDER BY data DESC, id DESC;""", (tipo,))
        return [_row_para_transacao(row) for row in cursor.fetchall()]
        
# Função de listagem apenas das transacoes de sinalizado 'categoria_id'
def listar_por_categoria(categoria_id: int) -> list[Transacao]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("""
        SELECT * FROM transacoes
        WHERE categoria_id = ?
        ORDER BY data DESC;""", (categoria_id,))
        manyrows = cursor.fetchall()
        return [_row_para_transacao(row) for row in manyrows]