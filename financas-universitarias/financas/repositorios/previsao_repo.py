import sqlite3
from financas.modelos.previsao import Previsao
from financas.repositorios.banco import conectar
from contextlib import closing

def _row_para_previsao(row: sqlite3.Row) -> Previsao: 
    return Previsao(**dict(row))

def criar(previsao: Previsao) -> Previsao: 
    with closing(conectar()) as conexao:
        with conexao: 
            cursor = conexao.cursor() 
            cursor.execute("INSERT INTO previsoes (gerada_em, saldo_projetado_centavos, situacao) VALUES (?, ?, ?);", 
                (
                    previsao.gerada_em.isoformat(), 
                    previsao.saldo_projetado_centavos, 
                    previsao.situacao
                )
            )
        previsao.id = cursor.lastrowid
        return previsao

def buscar_ultima() -> Previsao | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("""SELECT * FROM previsoes
        ORDER BY gerada_em DESC, id DESC
        LIMIT 1;""")
        row = cursor.fetchone()
        return _row_para_previsao(row) if row else None

def listar_todas() -> list[Previsao]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM previsoes ORDER BY gerada_em ASC, id ASC;")
        return [_row_para_previsao(row) for row in cursor.fetchall()]