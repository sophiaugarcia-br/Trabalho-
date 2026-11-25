from financas.repositorios.banco import conectar
from contextlib import closing

def obter(chave: str) -> str | None: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM config WHERE chave = ?;", (chave,))
        row = cursor.fetchone()
        return row["valor"] if row else None

def definir(chave: str, valor: str) -> None: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?);", (chave, valor))