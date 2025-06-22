from datetime import datetime
import sqlite3
from sqlite3 import Error

class Produto:
    def __init__(self, id=None, nome=None, preco=None, quantidade=None):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
    
    def salvar(self, conn):
        sql = '''INSERT INTO produtos(nome, preco, quantidade)
                 VALUES(?,?,?)'''
        cur = conn.cursor()
        cur.execute(sql, (self.nome, self.preco, self.quantidade))
        conn.commit()
        return cur.lastrowid
    
    def atualizar(self, conn):
        sql = '''UPDATE produtos
                 SET nome = ?, preco = ?, quantidade = ?
                 WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (self.nome, self.preco, self.quantidade, self.id))
        conn.commit()
    
    @staticmethod
    def buscar_todos(conn, filtro=None):
        cur = conn.cursor()
        if filtro:
            cur.execute("SELECT * FROM produtos WHERE LOWER(nome) LIKE ?", (f'%{filtro.lower()}%',))
        else:
            cur.execute("SELECT * FROM produtos")
        rows = cur.fetchall()
        produtos = []
        for row in rows:
            produtos.append(Produto(row[0], row[1], row[2], row[3]))
        return produtos
    
    @staticmethod
    def buscar_por_id(conn, id):
        cur = conn.cursor()
        cur.execute("SELECT * FROM produtos WHERE id=?", (id,))
        row = cur.fetchone()
        if row:
            return Produto(row[0], row[1], row[2], row[3])
        return None
    
    @staticmethod
    def atualizar_quantidade(conn, id, quantidade):
        """Diminui a quantidade do produto (usado durante vendas)"""
        sql = '''UPDATE produtos
                 SET quantidade = quantidade - ?
                 WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (quantidade, id))
        conn.commit()
    
    @staticmethod
    def ajustar_estoque(conn, id, nova_quantidade):
        """Define um novo valor absoluto para o estoque"""
        sql = '''UPDATE produtos
                 SET quantidade = ?
                 WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (nova_quantidade, id))
        conn.commit()
    
    @staticmethod
    def adicionar_estoque(conn, id, quantidade):
        """Adiciona quantidade ao estoque existente"""
        sql = '''UPDATE produtos
                 SET quantidade = quantidade + ?
                 WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (quantidade, id))
        conn.commit()

class Venda:
    def __init__(self, id=None, data_venda=None, total=None):
        self.id = id
        self.data_venda = data_venda
        self.total = total
        self.itens = []
    
    def salvar(self, conn):
        sql = '''INSERT INTO vendas(total)
                 VALUES(?)'''
        cur = conn.cursor()
        cur.execute(sql, (self.total,))
        conn.commit()
        self.id = cur.lastrowid
        
        # Salva os itens da venda
        for item in self.itens:
            item.salvar(conn, self.id)
            # Atualiza o estoque
            Produto.atualizar_quantidade(conn, item.produto_id, item.quantidade)
        
        return self.id
    
    @staticmethod
    def buscar_por_periodo(conn, data_inicio, data_fim):
        cur = conn.cursor()
        cur.execute("SELECT * FROM vendas WHERE date(data_venda) BETWEEN ? AND ?", 
                   (data_inicio, data_fim))
        rows = cur.fetchall()
        vendas = []
        for row in rows:
            vendas.append(Venda(row[0], row[1], row[2]))
        return vendas

class ItemVenda:
    def __init__(self, produto_id=None, quantidade=None, preco_unitario=None, subtotal=None):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.subtotal = subtotal
    
    def salvar(self, conn, venda_id):
        sql = '''INSERT INTO itens_venda(venda_id, produto_id, quantidade, preco_unitario, subtotal)
                 VALUES(?,?,?,?,?)'''
        cur = conn.cursor()
        cur.execute(sql, (venda_id, self.produto_id, self.quantidade, 
                         self.preco_unitario, self.subtotal))
        conn.commit()
        return cur.lastrowid

class Divida:
    def __init__(self, id=None, nome_cliente=None, data_divida=None, valor_total=None, paga=False, data_pagamento=None):
        self.id = id
        self.nome_cliente = nome_cliente
        self.data_divida = data_divida
        self.valor_total = valor_total
        self.paga = paga
        self.data_pagamento = data_pagamento
        self.itens = []
    
    def salvar(self, conn):
        sql = '''INSERT INTO dividas(nome_cliente, valor_total)
                 VALUES(?, ?)'''
        cur = conn.cursor()
        cur.execute(sql, (self.nome_cliente, self.valor_total))
        conn.commit()
        self.id = cur.lastrowid
        
        # Salva os itens da dívida
        for item in self.itens:
            item.salvar(conn, self.id)
        
        return self.id
    
    @staticmethod
    def marcar_como_paga(conn, divida_id):
        sql = '''UPDATE dividas
                 SET paga = 1, data_pagamento = CURRENT_TIMESTAMP
                 WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (divida_id,))
        conn.commit()
    
    #Estou a mexer aqui buscar_ativas
    @staticmethod
    
    def buscar_ativas(conn):
        """Busca dívidas ativas com seus itens"""
        cur = conn.cursor()
    
    # Busca as dívidas
        cur.execute("SELECT * FROM dividas WHERE paga = 0")
        dividas = []
        for row in cur.fetchall():
            divida = Divida(row[0], row[1], row[2], row[3], row[4], row[5])
        
        # Busca os itens de cada dívida
            cur.execute("""
            SELECT id.id, id.produto_id, p.nome, id.quantidade, id.preco_unitario 
            FROM itens_divida id
            JOIN produtos p ON id.produto_id = p.id
            WHERE id.divida_id = ?
        """, (divida.id,))
        
            divida.itens = []
            for item_row in cur.fetchall():
                item = ItemDivida(item_row[1], item_row[3], item_row[4])
                item.id = item_row[0]
                item.nome_produto = item_row[2]
                divida.itens.append(item)
        
            dividas.append(divida)
    
        return dividas

class ItemDivida:
    def __init__(self, produto_id=None, quantidade=None, preco_unitario=None):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.id = None
        self.nome_produto = ""
    
    def salvar(self, conn, divida_id):
        sql = '''INSERT INTO itens_divida(divida_id, produto_id, quantidade, preco_unitario)
                 VALUES(?, ?, ?, ?)'''
        cur = conn.cursor()
        cur.execute(sql, (divida_id, self.produto_id, self.quantidade, self.preco_unitario))
        conn.commit()
        return cur.lastrowid  # Corrigido: removido o "-" no final