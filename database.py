import sqlite3
from sqlite3 import Error

def criar_conexao(db_file):
    """Cria uma conexão com o banco de dados SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON")  # Ativa o suporte a chaves estrangeiras
        criar_tabelas(conn)
        return conn
    except Error as e:
        print(e)
    return conn

def criar_tabelas(conn):
    """Cria todas as tabelas necessárias"""
    try:
        c = conn.cursor()
        
        # Tabela de produtos
        c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     preco REAL NOT NULL,
                     quantidade INTEGER NOT NULL,
                     data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                     )''')
        
        # Tabela de vendas
        c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_venda TEXT DEFAULT CURRENT_TIMESTAMP,
                     total REAL NOT NULL
                     )''')
        
        # Tabela de itens vendidos
        c.execute('''CREATE TABLE IF NOT EXISTS itens_venda (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     venda_id INTEGER NOT NULL,
                     produto_id INTEGER NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco_unitario REAL NOT NULL,
                     subtotal REAL NOT NULL,
                     FOREIGN KEY (venda_id) REFERENCES vendas (id),
                     FOREIGN KEY (produto_id) REFERENCES produtos (id)
                     )''')
        
        # Tabela de dívidas (corrigido - removido o comentário)
        c.execute('''CREATE TABLE IF NOT EXISTS dividas (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_cliente TEXT NOT NULL,
                     data_divida TEXT DEFAULT CURRENT_TIMESTAMP,
                     valor_total REAL NOT NULL,
                     paga INTEGER DEFAULT 0,
                     data_pagamento TEXT
                     )''')
        
        # Tabela de itens da dívida
        c.execute('''CREATE TABLE IF NOT EXISTS itens_divida (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     divida_id INTEGER NOT NULL,
                     produto_id INTEGER NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco_unitario REAL NOT NULL,
                     FOREIGN KEY (divida_id) REFERENCES dividas (id),
                     FOREIGN KEY (produto_id) REFERENCES produtos (id)
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             nome TEXT NOT NULL UNIQUE,
             senha TEXT NOT NULL,
             is_admin INTEGER DEFAULT 0
             )''')
        c.execute("INSERT OR IGNORE INTO usuarios (nome, senha, is_admin) VALUES (?, ?, ?)", 
          ("admin", "123456", 1))  # Senha simples (em produção, use hash!)
        
        conn.commit()
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")