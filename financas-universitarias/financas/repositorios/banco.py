from config import PASTA_BANCO, CAMINHO_BANCO
from contextlib import closing
import os
import sqlite3
from financas.modelos.categoria import Categoria

# Função de conexão com o banco

def conectar():
    os.makedirs(PASTA_BANCO, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao

# Criar as tabelas

def criar_tabelas(): 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, 
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        cor TEXT NOT NULL,
        UNIQUE (nome, tipo)
        );

        CREATE TABLE IF NOT EXISTS recorrencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        descricao TEXT, 
        valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
        periodicidade TEXT NOT NULL CHECK (periodicidade IN ('SEMANAL', 'MENSAL')),
        dia INTEGER NOT NULL CHECK (dia BETWEEN 1 AND 31), 
        data_inicio TEXT NOT NULL, 
        data_fim TEXT, 
        categoria_id INTEGER NOT NULL, 
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        descricao TEXT, 
        valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
        data TEXT NOT NULL,
        categoria_id INTEGER NOT NULL, 
        recorrencia_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id), 
        FOREIGN KEY (recorrencia_id) REFERENCES recorrencias(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT NOT NULL, 
        preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0), 
        prazo TEXT, 
        criada_em TEXT NOT NULL, 
        guardado_centavos INTEGER NOT NULL CHECK (guardado_centavos >= 0), 
        status TEXT NOT NULL CHECK (status IN ('ABERTA', 'CONCLUIDA')), 
        concluida_em TEXT
        );

        CREATE TABLE IF NOT EXISTS investimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        valor_inicial_centavos INTEGER NOT NULL CHECK (valor_inicial_centavos > 0), 
        taxa TEXT NOT NULL, 
        periodicidade_taxa TEXT NOT NULL CHECK (periodicidade_taxa IN ('AA', 'AM')), 
        data_inicio TEXT NOT NULL, 
        data_resgate TEXT
        );

        CREATE TABLE IF NOT EXISTS previsoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gerada_em TEXT NOT NULL, 
        saldo_projetado_centavos INTEGER NOT NULL, 
        situacao TEXT NOT NULL CHECK (situacao IN ('LUCRO', 'EQUILIBRIO', 'DIVIDA'))
        );

        CREATE TABLE IF NOT EXISTS relatorios (
        mes TEXT PRIMARY KEY, 
        caminho_pdf TEXT NOT NULL, 
        gerado_em TEXT NOT NULL, 
        hash_dados TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS config (
        chave TEXT PRIMARY KEY, 
        valor TEXT NOT NULL
        );
""")

# Criar categorias padrões no BD caso seja o primeiro acesso do usuário à aplicação

CATEGORIAS_PADRAO: list[Categoria] = [
Categoria(nome="Salário", tipo="ENTRADA", cor="#13A500"),
Categoria(nome="Freelance", tipo="ENTRADA", cor="#0068A5"),
Categoria(nome="Moradia", tipo="SAIDA", cor="#2400A5"),
Categoria(nome="Alimentação", tipo="SAIDA", cor="#FFF241"),
Categoria(nome="Educação", tipo="SAIDA", cor="#BB0000"),
Categoria(nome="Saúde", tipo="SAIDA", cor="#FFFFFF"),
Categoria(nome="Transporte", tipo="SAIDA", cor="#009FA5"),
Categoria(nome="Vestuário", tipo="SAIDA", cor="#B36500")
]

def semear_categorias() -> None: 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM categorias;")
        retorno = cursor.fetchone()[0]
        if retorno > 0: return
        categorias = [(cat.nome, cat.tipo, cat.cor) for cat in CATEGORIAS_PADRAO]
        cursor.executemany("INSERT INTO categorias (nome, tipo, cor) VALUES (?, ?, ?)", categorias)
        conexao.commit()

# Função padrão utilizada ao inicializar o sistema

def inicializar_banco() -> None: 
    criar_tabelas()
    semear_categorias()