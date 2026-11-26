import sqlite3
from financas.modelos.previsao import Previsao
from financas.repositorios.banco import conectar
from contextlib import closing

"""Função interna do módulo que tem por finalidade a atribuição facilitada dos conjuntos chave-valor do sqlite3.Row aos atributos de um objeto da classe Previsao"""
def _row_para_previsao(row: sqlite3.Row) -> Previsao: 
    return Previsao(**dict(row))

# Função que cria um novo campo no Banco de Dados a partir de um objeto 'Previsao' fornecido pelo usuário
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

"""Função de busca da última previsao feita correspondente ao id dela fornecido, a fim de que posteriormente se identifique a necessidade de gera nova previsao pela data"""
def buscar_ultima() -> Previsao | None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor() 
        cursor.execute("""SELECT * FROM previsoes
        ORDER BY gerada_em DESC, id DESC
        LIMIT 1;""")
        row = cursor.fetchone()
        return _row_para_previsao(row) if row else None

# Listagem geral das previsoes de ordenação ascendente pela data em que foram geradas
def listar_todas() -> list[Previsao]: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM previsoes ORDER BY gerada_em ASC, id ASC;")
        return [_row_para_previsao(row) for row in cursor.fetchall()]