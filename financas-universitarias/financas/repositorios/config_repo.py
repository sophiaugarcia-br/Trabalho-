from financas.repositorios.banco import conectar
from contextlib import closing

# Função de obtenção do valor de uma chave da tabela 'config'
def obter(chave: str) -> str | None: 
    with closing(conectar()) as conexao: 
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM config WHERE chave = ?;", (chave,))
        row = cursor.fetchone()
        return row["valor"] if row else None

# Função para definição (ou atualização) de um objeto chave-valor de configuração do sistema
def definir(chave: str, valor: str) -> None: 
    with closing(conectar()) as conexao: 
        with conexao: 
            cursor = conexao.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?);", (chave, valor))