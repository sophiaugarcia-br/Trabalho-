import sqlite3
from financas.modelos.relatorio import Relatorio
from financas.repositorios.banco import conectar
from contextlib import closing
from datetime import date

def _row_para_relatorio(row: sqlite3.Row) -> Relatorio: 
    return Relatorio(**dict(row))

def salvar(mes: str, caminho_pdf: str, gerado_em: date, hash_dados: str) -> None: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT OR REPLACE INTO relatorios (mes, caminho_pdf, gerado_em, hash_dados) VALUES (?, ?, ?, ?);", (mes, caminho_pdf, gerado_em.isoformat(), hash_dados)
            )

def buscar_por_mes(mes: str) -> Relatorio | None:
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("""SELECT * FROM relatorios
        WHERE mes = ?;""", (mes,))
        row = cursor.fetchone()
        return _row_para_relatorio(row) if row else None

def listar_todos() -> list[Relatorio]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM relatorios ORDER BY mes DESC;")
        return [_row_para_relatorio(row) for row in cursor.fetchall()]