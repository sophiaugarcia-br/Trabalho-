

import sqlite3
from datetime import date
from pathlib import Path

db_path = Path(__file__).parent / 'financas.db'

# dados iniciais
categorias_padrao = [
    ('Salario', 'Receita'),
    ('Trabalho', 'Receita'),
    ('Outros', 'Receita'),
    ('Rendimentos', 'Receita'),
    ('Alimentacao', 'Despesa'),
    ('Transporte', 'Despesa'),
    ('Lazer', 'Despesa'),
    ('Saude', 'Despesa'),
    ('Moradia', 'Despesa')
]

# conexao -------------------------------------

def _conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# inicializar banco de dados -------------------

def inicializar_banco() -> None:
    with _conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS categorias(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Receita', 'Despesa'))
            );
            CREATE TABLE IF NOT EXISTS transacoes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria_id INTEGER NOT NULL REFERENCES categorias(id),
                descricao TEXT NOT NULL,
                valor REAL NOT NULL CHECK(valor > 0),
                data DATE NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Receita', 'Despesa'))
            );
        """)
        
        qtd = conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
        if qtd == 0:
            conn.executemany(
                "INSERT INTO categorias (nome, tipo) VALUES (?,?)",
                categorias_padrao,
            )

# CRUD - CATEGORIAS ---------------------------

def listar_categorias(tipo: str | None = None) -> list[dict]:
    sql = "SELECT * FROM categorias "
    params: tuple = ()

    if tipo:
        sql += "WHERE tipo = ? "
        params = (tipo,)

    sql += "ORDER BY tipo, nome"

    with _conectar() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def inserir_categoria(nome: str, tipo: str) -> None:
    with _conectar() as conn:
        conn.execute(
            "INSERT INTO categorias (nome, tipo) VALUES (?,?)",
            (nome.strip(), tipo),
        )

def deletar_categoria(categoria_id: int) -> None:
    with _conectar() as conn:
        conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))

# CRUD - TRANSACOES ---------------------------

def inserir_transacao(categoria_id: int, descricao: str, valor: float, data: date, tipo: str) -> None:
    with _conectar() as conn:
        conn.execute(
            """INSERT INTO transacoes (categoria_id, descricao, valor, data, tipo)
               VALUES (?,?,?,?,?)""",
            (categoria_id, descricao.strip(), valor, data.isoformat(), tipo),
        )

def listar_transacoes(mes: int | None = None, ano: int | None = None, tipo: str | None = None) -> list[dict]:
    sql = """
        SELECT t.id,
               t.data,
               t.tipo,
               c.nome AS categoria,
               t.descricao,
               t.valor
        FROM transacoes t
        JOIN categorias c ON c.id = t.categoria_id
        WHERE 1=1
    """
    params: list = []
    
    if mes and ano:
        sql += " AND strftime('%m', t.data) = ? AND strftime('%Y', t.data) = ?"
        params.extend([f'{mes:02d}', str(ano)])
    if tipo:
        sql += " AND t.tipo = ?"
        params.append(tipo)
        
    sql += " ORDER BY t.data DESC, t.id DESC"
    
    with _conectar() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def deletar_transacao(transacao_id: int) -> None:
    with _conectar() as conn:
        conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))

# CONSULTAS ANALITICAS - DASHBOARD ------------

def resumo_mes_atual() -> dict:
    hoje = date.today()
    mes = f'{hoje.month:02d}'
    ano = str(hoje.year)
    
    with _conectar() as conn:
        receitas = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) FROM transacoes
               WHERE tipo = 'Receita' AND strftime('%m', data) = ? AND strftime('%Y', data) = ?""",
            (mes, ano),
        ).fetchone()[0]
        
        despesas = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) FROM transacoes
               WHERE tipo = 'Despesa' AND strftime('%m', data) = ? AND strftime('%Y', data) = ?""",
            (mes, ano),
        ).fetchone()[0]
        
    return {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': receitas - despesas,
    }

def fluxo_mensal() -> list[dict]:
    with _conectar() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-%m', data) AS mes,
                   tipo,
                   SUM(valor) AS total
            FROM transacoes
            WHERE data >= date('now', '-12 months')
            GROUP BY mes, tipo
            ORDER BY mes
        """).fetchall()
        return [dict(r) for r in rows]

def despesas_por_categoria_mes_atual() -> list[dict]:
    """Retorna o total de despesas agrupado por categoria no mes corrente"""
    hoje = date.today()
    mes = f'{hoje.month:02d}'
    ano = str(hoje.year)
    
    query = """
        SELECT c.nome AS categoria,
               SUM(t.valor) AS total
        FROM transacoes t
        JOIN categorias c ON c.id = t.categoria_id
        WHERE t.tipo = 'Despesa'
          AND strftime('%m', t.data) = ?
          AND strftime('%Y', t.data) = ?
        GROUP BY c.nome
        ORDER BY total DESC
    """
    with _conectar() as conn:
        rows = conn.execute(query, (mes, ano)).fetchall()
        return [dict(r) for r in rows]
