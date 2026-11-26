import sqlite3
from financas.modelos.recorrencia import Recorrencia
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row aos atributos de um objeto da classe Recorrencia"""
def _row_para_recorrencia(row: sqlite3.Row) -> Recorrencia: 
    return Recorrencia(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Recorrencia' fornecido pelo usuário
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

# Função de busca de uma recorrencia que corresponda ao id dela fornecido
def buscar_por_id(recorrencia_id: int) -> Recorrencia | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM recorrencias WHERE id = ?;", (recorrencia_id,))
        row = cursor.fetchone()
        return _row_para_recorrencia(row) if row else None

# Função que consiste em atualizar os atributos de uma recorrencia já criada pelo id dela
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

# Função excludente de recorrencia de específico id
def excluir(recorrencia_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM recorrencias WHERE id = ?;", (recorrencia_id,))
        return cursor.rowcount > 0

# Função listadora das recorrencias que permanecem ocorrendo no período da data fornecida
def listar_ativas(data_ref: date) -> list[Recorrencia]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM recorrencias
        WHERE data_inicio <= ? AND (data_fim IS NULL OR data_fim >= ?);""", (data_ref.isoformat(), data_ref.isoformat()))
        return [_row_para_recorrencia(row) for row in cursor.fetchall()]

# Listagem geral das recorrencias de ordenação ascendente pelo dia em que ela reinicia
def listar_todas() -> list[Recorrencia]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM recorrencias ORDER BY dia ASC;")
        return [_row_para_recorrencia(row) for row in cursor.fetchall()]