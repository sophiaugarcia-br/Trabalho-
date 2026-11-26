import sqlite3
from financas.modelos.investimento import Investimento
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row aos atributos de um objeto da classe Investimento"""
def _row_para_investimento(row: sqlite3.Row) -> Investimento: 
    return Investimento(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Investimento' fornecido pelo usuário
def criar(investimento: Investimento) -> Investimento: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT INTO investimentos (nome, valor_inicial_centavos, taxa, periodicidade_taxa, data_inicio, data_resgate) VALUES (?, ?, ?, ?, ?, ?);", 
                (
                    investimento.nome, 
                    investimento.valor_inicial_centavos, 
                    str(investimento.taxa), 
                    investimento.periodicidade_taxa, 
                    investimento.data_inicio.isoformat(), 
                    investimento.data_resgate.isoformat() if investimento.data_resgate is not None else None
                )
            )
        investimento.id = cursor.lastrowid
        return investimento

# Função de busca de um investimento que corresponda ao id dela fornecido
def buscar_por_id(investimento_id: int) -> Investimento | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("SELECT * FROM investimentos WHERE id = ?;", (investimento_id,))
        row = cursor.fetchone()
        return _row_para_investimento(row) if row else None

# Função que consiste em atualizar os atributos de um investimento já criada pelo id dela
def atualizar(investimento: Investimento) -> bool:
    if investimento.id is None: 
        raise ValueError("Erro: Investimento.id não pode ser nulo.")
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("""
            UPDATE investimentos
            SET nome = ?, 
                valor_inicial_centavos = ?, 
                taxa = ?, 
                periodicidade_taxa = ?, 
                data_inicio = ?, 
                data_resgate = ?
            WHERE id = ?;
            """, (
                    investimento.nome, 
                    investimento.valor_inicial_centavos, 
                    str(investimento.taxa), 
                    investimento.periodicidade_taxa, 
                    investimento.data_inicio.isoformat(), 
                    investimento.data_resgate.isoformat() if investimento.data_resgate is not None else None, 
                    investimento.id
            ))
        return cursor.rowcount > 0

# Função excludente de investimento de específico id
def excluir(investimento_id: int) -> bool: 
    with closing(conectar()) as conexao:
        with conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM investimentos WHERE id = ?;", (investimento_id,))
        return cursor.rowcount > 0

# Função listadora dos investimentos ativos no mês informado
def listar_ativos_no_periodo(inicio_mes: date, fim_mes: date) -> list[Investimento]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT * FROM investimentos
            WHERE data_inicio <= ? AND (data_resgate IS NULL OR data_resgate >= ?)
            ORDER BY data_inicio ASC, id ASC;""", (fim_mes.isoformat(), inicio_mes.isoformat()))
        return [_row_para_investimento(row) for row in cursor.fetchall()]

# Listagem geral dos investimentos de ordenação ascendente pelo nome
def listar_todos() -> list[Investimento]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM investimentos ORDER BY nome ASC;")
        return [_row_para_investimento(row) for row in cursor.fetchall()]