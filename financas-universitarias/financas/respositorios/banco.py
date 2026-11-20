from config import PASTA_BANCO, CAMINHO_BANCO
from contextlib import closing
import os
import sqlite3

def conectar():
    os.makedirs(PASTA_BANCO, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao

def criar_tabelas(): 
    with closing(conectar()) as conexao:
        cursor = conexao.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, 
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        cor TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recorrencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        descricao TEXT, 
        valor_centavos INTEGER NOT NULL,
        periodicidade TEXT NOT NULL CHECK (periodicidade IN ('SEMANAL', 'MENSAL')),
        dia INTEGER NOT NULL, 
        data_inicio TEXT NOT NULL, 
        data_fim TEXT, 
        categoria_id INTEGER NOT NULL, 
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
        descricao TEXT, 
        valor_centavos INTEGER NOT NULL,
        data TEXT NOT NULL,
        categoria_id INTEGER NOT NULL, 
        recorrencia_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id), 
        FOREIGN KEY (recorrencia_id) REFERENCES recorrencias(id)
        );

        CREATE TABLE IF NOT EXISTS metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT NOT NULL, 
        preco_centavos INTEGER NOT NULL, 
        prazo TEXT, 
        criada_em TEXT NOT NULL, 
        guardado_centavos INTEGER NOT NULL, 
        status TEXT NOT NULL CHECK (status IN ('ABERTA', 'CONCLUIDA')), 
        concluida_em TEXT
        );

        CREATE TABLE IF NOT EXISTS investimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        valor_inicial_centavos INTEGER NOT NULL, 
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


def semear_categorias(): 
    with closing(conectar()) as conexao:
        