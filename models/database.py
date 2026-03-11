"""
Configuração e inicialização do banco de dados SQLite
Contém as funções para criar tabelas e conectar ao banco
"""

import sqlite3
import os

# Caminho do banco de dados local
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite
    Configura para retornar dicionários em vez de tuplas
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas necessárias
    Executado uma vez na inicialização da aplicação
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            saldo_devedor REAL DEFAULT 0.0
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total REAL NOT NULL,
            tipo_pagamento TEXT NOT NULL,  -- 'dinheiro', 'cartao', 'fiado'
            cliente_id INTEGER,  -- NULL se for venda à vista
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    # Tabela de Itens da Venda (relacionamento N:N)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venda_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Tabela de Contas a Receber (Fiado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            venda_id INTEGER,
            valor REAL NOT NULL,
            data_vencimento DATE,
            data_pagamento TIMESTAMP,
            status TEXT DEFAULT 'pendente',  -- 'pendente', 'pago', 'atrasado'
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (venda_id) REFERENCES vendas (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")

def query_db(query, args=(), one=False):
    """
    Executa uma consulta no banco de dados
    :param query: String SQL
    :param args: Tupla de argumentos para a query
    :param one: Se True, retorna apenas o primeiro resultado
    :return: Resultado da consulta
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, args)
        rv = cursor.fetchall()
        conn.commit()
        return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()