import sqlite3
from financas.modelos.relatorio import Relatorio
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row aos atributos de um objeto da classe Relatorio"""
def _row_para_relatorio(row: sqlite3.Row) -> Relatorio: 
    return Relatorio(**dict(row))

# Função de salvamento ou atualização dos metadados de um relatório de algum mês
def salvar(mes: str, caminho_pdf: str, gerado_em: date, hash_dados: str) -> None: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT OR REPLACE INTO relatorios (mes, caminho_pdf, gerado_em, hash_dados) VALUES (?, ?, ?, ?);", (mes, caminho_pdf, gerado_em.isoformat(), hash_dados)
            )
# Função que providencia os dados do relatório de um mês requerido
def buscar_por_mes(mes: str) -> Relatorio | None:
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("""SELECT * FROM relatorios
        WHERE mes = ?;""", (mes,))
        row = cursor.fetchone()
        return _row_para_relatorio(row) if row else None

# Listagem geral dos relatorios de ordenação descendente pelo mês
def listar_todos() -> list[Relatorio]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM relatorios ORDER BY mes DESC;")
        return [_row_para_relatorio(row) for row in cursor.fetchall()]