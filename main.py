import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models import Produto, Venda, ItemVenda, Divida, ItemDivida
import database

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Loja Samir")
        self.root.geometry("300x200")
        
        # Conexão com o banco
        self.conn = database.criar_conexao("loja.db")
        
        # Widgets
        ttk.Label(root, text="Usuário:").pack(pady=5)
        self.entry_usuario = ttk.Entry(root)
        self.entry_usuario.pack(pady=5)
        
        ttk.Label(root, text="Senha:").pack(pady=5)
        self.entry_senha = ttk.Entry(root, show="*")
        self.entry_senha.pack(pady=5)
        
        ttk.Button(root, text="Entrar", command=self.validar_login).pack(pady=10)
    
    def validar_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha usuário e senha!")
            return
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (usuario, senha))
        usuario_db = cursor.fetchone()
        
        if usuario_db:
            self.root.destroy()  # Fecha a janela de login
            root = tk.Tk()  # Nova janela principal
            app = LojaApp(root)  # Abre a LojaApp
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

class LojaApp:
    def __init__(self, root):
       # style = ttk.Style()
       # style.configure("Treeview", rowheight=25)  # Altura das linhas
       # style.map("Treeview", foreground=[])   # Itens filtrados ficam esmaecidos
        self.root = root
        self.root.title("Sistema de Gestão - Loja Samir")
        self.root.geometry("1000x600")
        
        # Conectar ao banco de dados
        self.conn = database.criar_conexao("loja.db")
        database.criar_tabelas(self.conn)
        
        # Criar abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Abas do sistema
        self.criar_aba_vendas()
        self.criar_aba_produtos()
        self.criar_aba_estoque()
        self.criar_aba_dividas()  # Nova aba de dívidas
        self.criar_aba_relatorios()
        self.criar_aba_configuracoes()
        
        # Carregar dados iniciais
        self.carregar_produtos()
        self.carregar_dividas()
    
    def criar_aba_produtos(self):
        """Cria a aba para cadastro de produtos"""
        self.aba_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_produtos, text="Cadastro de Produtos")
        
        # Frame de formulário
        frame_form = ttk.LabelFrame(self.aba_produtos, text="Informações do Produto")
        frame_form.pack(padx=10, pady=10, fill='x')
        
        # Campos do formulário
        ttk.Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_nome = ttk.Entry(frame_form, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_form, text="Preço:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_preco = ttk.Entry(frame_form, width=20)
        self.entry_preco.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame_form, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_quantidade = ttk.Entry(frame_form, width=20)
        self.entry_quantidade.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Botões
        frame_botoes = ttk.Frame(self.aba_produtos)
        frame_botoes.pack(pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_produto).pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Limpar", command=self.limpar_formulario).pack(side='left', padx=5)
    
    def criar_aba_estoque(self):
        """Cria a aba para visualização e edição de estoque com pesquisa"""
        self.aba_estoque = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_estoque, text="Estoque")
    
    # Frame para pesquisa
        frame_pesquisa = ttk.Frame(self.aba_estoque)
        frame_pesquisa.pack(padx=10, pady=5, fill='x')
    
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side='left', padx=5)
        self.entry_pesquisa_estoque = ttk.Entry(frame_pesquisa)
        self.entry_pesquisa_estoque.pack(side='left', padx=5, fill='x', expand=True)
        self.entry_pesquisa_estoque.bind('<KeyRelease>', self.filtrar_estoque)
    
    # Frame para a treeview e botões
        frame_principal = ttk.Frame(self.aba_estoque)
        frame_principal.pack(fill='both', expand=True, padx=10, pady=5)
    
    # Treeview para exibir produtos
        self.tree_estoque = ttk.Treeview(frame_principal, 
                                    columns=('id', 'nome', 'preco', 'quantidade'), 
                                    show='headings')
        self.tree_estoque.heading('id', text='ID')
        self.tree_estoque.heading('nome', text='Nome')
        self.tree_estoque.heading('preco', text='Preço')
        self.tree_estoque.heading('quantidade', text='Quantidade')
        self.tree_estoque.column('id', width=50, anchor='center')
        self.tree_estoque.column('nome', width=200)
        self.tree_estoque.column('preco', width=100, anchor='e')
        self.tree_estoque.column('quantidade', width=100, anchor='center')
        self.tree_estoque.pack(fill='both', expand=True, side='left')
    
    # Scrollbar
        scrollbar = ttk.Scrollbar(frame_principal, 
                             orient='vertical', 
                             command=self.tree_estoque.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_estoque.configure(yscrollcommand=scrollbar.set)
    
    # Frame para botões
        frame_botoes = ttk.Frame(self.aba_estoque)
        frame_botoes.pack(fill='x', padx=10, pady=5)
    
        ttk.Button(frame_botoes, 
                text="Atualizar Quantidade", 
                command=self.abrir_janela_edicao).pack(side='left', padx=5)
    
        ttk.Button(frame_botoes, 
              text="Atualizar Lista", 
              command=lambda: self.carregar_produtos()).pack(side='left', padx=5)
    
    # Configurar evento de duplo clique
        self.tree_estoque.bind('<Double-1>', self.abrir_janela_edicao)
    
    # Carregar produtos inicialmente
        self.carregar_produtos()
    
    def filtrar_estoque(self, event=None):
        """Filtra os produtos no estoque conforme o texto digitado"""
        termo = self.entry_pesquisa_estoque.get().lower()
    
    # Se o campo estiver vazio, mostra todos os produtos
        if not termo:
            self.carregar_produtos()
            return
    
    # Filtra os produtos localmente (mais rápido para bancos pequenos)
        for item in self.tree_estoque.get_children():
            valores = self.tree_estoque.item(item, 'values')
            nome_produto = valores[1].lower()
            if termo in nome_produto:
                self.tree_estoque.item(item, tags=('visivel',))
                self.tree_estoque.selection_set(item)  # Opcional: seleciona o item
            else:
                self.tree_estoque.item(item, tags=('invisivel',))
    
    # Configura a tag para ocultar itens
        self.tree_estoque.tag_configure('invisivel', foreground='gray90')  # Ou completamente invisível

    def abrir_janela_edicao(self, event=None):
        """Abre janela para editar a quantidade do produto"""
        # Obter item selecionado
        item_selecionado = self.tree_estoque.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar!")
            return
        
        # Obter dados do produto
        item = self.tree_estoque.item(item_selecionado)
        produto_id = item['values'][0]
        produto_nome = item['values'][1]
        quantidade_atual = item['values'][3]
        
        # Criar janela de edição
        janela_edicao = tk.Toplevel(self.root)
        janela_edicao.title(f"Atualizar Estoque - {produto_nome}")
        janela_edicao.geometry("300x150")
        
        # Frame principal
        frame_principal = ttk.Frame(janela_edicao)
        frame_principal.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Labels e entries
        ttk.Label(frame_principal, text="Quantidade Atual:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Label(frame_principal, text=str(quantidade_atual)).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(frame_principal, text="Nova Quantidade:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        entry_nova_quantidade = ttk.Entry(frame_principal)
        entry_nova_quantidade.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        entry_nova_quantidade.insert(0, str(quantidade_atual))
        entry_nova_quantidade.focus()
        
        # Botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=janela_edicao.destroy).pack(side='right', padx=5)
        
        ttk.Button(frame_botoes, text="Salvar", 
                  command=lambda: self.salvar_quantidade(
                      produto_id, entry_nova_quantidade.get(), janela_edicao)
                  ).pack(side='right', padx=5)
    
    def salvar_quantidade(self, produto_id, nova_quantidade_str, janela):
        """Salva a nova quantidade no banco de dados"""
        try:
            nova_quantidade = int(nova_quantidade_str)
            if nova_quantidade < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo!")
            return
        
        # Atualizar no banco de dados
        Produto.ajustar_estoque(self.conn, produto_id, nova_quantidade)
        
        messagebox.showinfo("Sucesso", "Quantidade atualizada com sucesso!")
        janela.destroy()
        self.carregar_produtos()  # Atualizar a lista
    
    def criar_aba_vendas(self):
        """Cria a aba para realizar vendas"""
        self.aba_vendas = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_vendas, text="Caixa")
        
        # Frame para pesquisa
        frame_pesquisa = ttk.Frame(self.aba_vendas)
        frame_pesquisa.pack(padx=10, pady=5, fill='x')
    
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side='left', padx=5)
        self.entry_pesquisa = ttk.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side='left', padx=5, fill='x', expand=True)
        self.entry_pesquisa.bind('<KeyRelease>', self.filtrar_produtos)

        # Frame para seleção de produtos
        frame_selecao = ttk.LabelFrame(self.aba_vendas, text="Selecionar Produto")
        frame_selecao.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(frame_selecao, text="Produto:").pack(side='left', padx=5)
        self.combo_produtos = ttk.Combobox(frame_selecao, state="readonly")
        self.combo_produtos.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Label(frame_selecao, text="Quantidade:").pack(side='left', padx=5)
        self.entry_qtd_venda = ttk.Entry(frame_selecao, width=10)
        self.entry_qtd_venda.pack(side='left', padx=5)
        
        ttk.Button(frame_selecao, text="Adicionar", command=self.adicionar_item_venda).pack(side='left', padx=5)
        
        # Frame para itens da venda
        frame_itens = ttk.LabelFrame(self.aba_vendas, text="Itens da Venda")
        frame_itens.pack(padx=10, pady=5, fill='both', expand=True)
        
        self.tree_itens = ttk.Treeview(frame_itens, columns=('produto', 'quantidade', 'preco', 'subtotal'), show='headings')
        self.tree_itens.heading('produto', text='Produto')
        self.tree_itens.heading('quantidade', text='Quantidade')
        self.tree_itens.heading('preco', text='Preço Unitário')
        self.tree_itens.heading('subtotal', text='Subtotal')
        self.tree_itens.column('produto', width=200)
        self.tree_itens.column('quantidade', width=100)
        self.tree_itens.column('preco', width=100)
        self.tree_itens.column('subtotal', width=100)
        self.tree_itens.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame para total e finalização
        frame_total = ttk.Frame(self.aba_vendas)
        frame_total.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(frame_total, text="Total da Venda:").pack(side='left')
        self.label_total = ttk.Label(frame_total, text="MZN 0.00", font=('Arial', 12, 'bold'))
        self.label_total.pack(side='left', padx=10)
        
        ttk.Button(frame_total, text="Finalizar Venda", command=self.finalizar_venda).pack(side='right')
        ttk.Button(frame_total, text="Cancelar Venda", command=self.limpar_venda).pack(side='right', padx=5)
        
        # Variáveis para controle da venda
        self.itens_venda = []
        self.total_venda = 0.0

    def filtrar_produtos(self, event):
        """Filtra os produtos conforme o texto digitado"""
        termo_pesquisa = self.entry_pesquisa.get()
        self.carregar_produtos(filtro=termo_pesquisa)
    
    def criar_aba_dividas(self):
        """Cria a aba para gerenciamento de dívidas"""
        self.aba_dividas = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_dividas, text="Dívidas")
        
        # Frame para nova dívida
        frame_nova = ttk.LabelFrame(self.aba_dividas, text="Nova Dívida")
        frame_nova.pack(padx=10, pady=5, fill='x')
        
        # Campos do cliente
        ttk.Label(frame_nova, text="Nome do Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_cliente_divida = ttk.Entry(frame_nova, width=30)
        self.entry_cliente_divida.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Botão para adicionar itens
        ttk.Button(frame_nova, text="Adicionar Itens", 
                  command=self.abrir_janela_itens_divida).grid(row=0, column=2, padx=5)
        
        # Lista de itens da dívida
        self.tree_itens_divida = ttk.Treeview(frame_nova, columns=('produto', 'quantidade', 'preco'), 
                                            show='headings', height=4)
        self.tree_itens_divida.heading('produto', text='Produto')
        self.tree_itens_divida.heading('quantidade', text='Qtd')
        self.tree_itens_divida.heading('preco', text='Preço Unit.')
        self.tree_itens_divida.column('produto', width=150)
        self.tree_itens_divida.column('quantidade', width=50)
        self.tree_itens_divida.column('preco', width=80)
        self.tree_itens_divida.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Total da dívida
        ttk.Label(frame_nova, text="Total:").grid(row=2, column=1, padx=5, pady=5, sticky='e')
        self.label_total_divida = ttk.Label(frame_nova, text="MZN 0.00")
        self.label_total_divida.grid(row=2, column=2, padx=5, pady=5, sticky='w')
        
        # Botão para registrar dívida
        ttk.Button(frame_nova, text="Registrar Dívida", 
                  command=self.registrar_divida).grid(row=3, column=0, columnspan=3, pady=5)
        
        # Lista de dívidas ativas
        frame_lista = ttk.LabelFrame(self.aba_dividas, text="Dívidas Pendentes")
        frame_lista.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Treeview para dívidas
        self.tree_dividas = ttk.Treeview(frame_lista, columns=('id', 'cliente', 'data', 'valor'), 
                                       show='headings')
        self.tree_dividas.heading('id', text='ID')
        self.tree_dividas.heading('cliente', text='Cliente')
        self.tree_dividas.heading('data', text='Data')
        self.tree_dividas.heading('valor', text='Valor (MZN)')
        self.tree_dividas.column('id', width=50)
        self.tree_dividas.column('cliente', width=150)
        self.tree_dividas.column('data', width=100)
        self.tree_dividas.column('valor', width=100)
        self.tree_dividas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botão para marcar como paga
        ttk.Button(frame_lista, text="Marcar como Paga", 
                  command=self.marcar_divida_paga).pack(pady=5)
        
        # Variáveis para controle
        self.itens_divida = []
        self.total_divida = 0.0
    
    def abrir_janela_itens_divida(self):
        """Abre janela para adicionar itens à dívida"""
        if not self.entry_cliente_divida.get():
            messagebox.showerror("Erro", "Informe o nome do cliente primeiro!")
            return
            
        self.janela_itens_divida = tk.Toplevel(self.root)
        self.janela_itens_divida.title("Adicionar Itens à Dívida")
        self.janela_itens_divida.geometry("500x400")
        
        # Frame para seleção de produtos
        frame_selecao = ttk.LabelFrame(self.janela_itens_divida, text="Selecionar Produto")
        frame_selecao.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(frame_selecao, text="Produto:").pack(side='left', padx=5)
        self.combo_produtos_divida = ttk.Combobox(frame_selecao, state="readonly")
        self.combo_produtos_divida.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Label(frame_selecao, text="Quantidade:").pack(side='left', padx=5)
        self.entry_qtd_divida = ttk.Entry(frame_selecao, width=10)
        self.entry_qtd_divida.pack(side='left', padx=5)
        
        ttk.Button(frame_selecao, text="Adicionar", 
                  command=self.adicionar_item_divida).pack(side='left', padx=5)
        
        # Atualizar combobox com produtos
        produtos = Produto.buscar_todos(self.conn)
        self.combo_produtos_divida['values'] = [(f"{p.nome} - MZN {p.preco:.2f}", p.id) for p in produtos]
        if produtos:
            self.combo_produtos_divida.current(0)
    
    def adicionar_item_divida(self):
        """Adiciona um item à dívida atual"""
        if not self.combo_produtos_divida.get():
            messagebox.showerror("Erro", "Selecione um produto!")
            return
            
        try:
            qtd = int(self.entry_qtd_divida.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo!")
            return
            
        # Obter produto selecionado
        produto_idx = self.combo_produtos_divida.current()
        produto_id = self.combo_produtos_divida['values'][produto_idx][1]
        produto = Produto.buscar_por_id(self.conn, produto_id)
        
        # Verificar estoque (mas não diminui ainda)
        if produto.quantidade < qtd:
            messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {produto.quantidade}")
            return
            
        # Adicionar à lista de itens
        self.itens_divida.append({
            'produto_id': produto.id,
            'nome': produto.nome,
            'quantidade': qtd,
            'preco': produto.preco
        })
        
        # Atualizar Treeview
        self.tree_itens_divida.insert('', 'end', values=(
            produto.nome, qtd, f"MZN {produto.preco:.2f}"
        ))
        
        # Atualizar total
        self.total_divida += produto.preco * qtd
        self.label_total_divida.config(text=f"MZN {self.total_divida:.2f}")
        
        # Limpar campos
        self.entry_qtd_divida.delete(0, 'end')
    
    def registrar_divida(self):
        """Registra a dívida no sistema"""
        if not self.entry_cliente_divida.get():
            messagebox.showerror("Erro", "Informe o nome do cliente!")
            return
            
        if not self.itens_divida:
            messagebox.showerror("Erro", "Adicione pelo menos um item à dívida!")
            return
            
        # Criar objeto Dívida
        divida = Divida(
            nome_cliente=self.entry_cliente_divida.get(),
            valor_total=self.total_divida
        )
        
        # Adicionar itens à dívida
        for item in self.itens_divida:
            item_divida = ItemDivida(
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco']
            )
            divida.itens.append(item_divida)
        
        # Salvar no banco de dados
        try:
            divida.salvar(self.conn)
            messagebox.showinfo("Sucesso", "Dívida registrada com sucesso!")
            
            # Limpar formulário
            self.entry_cliente_divida.delete(0, 'end')
            for item in self.tree_itens_divida.get_children():
                self.tree_itens_divida.delete(item)
            self.itens_divida = []
            self.total_divida = 0.0
            self.label_total_divida.config(text="MZN 0.00")
            
            # Atualizar lista de dívidas
            self.carregar_dividas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao registrar dívida: {str(e)}")
    
    def carregar_dividas(self):
        """Carrega as dívidas ativas com produtos em formato hierárquico"""
    # Limpa a treeview
        for item in self.tree_dividas.get_children():
            self.tree_dividas.delete(item)
    
    # Configura as colunas
        self.tree_dividas['columns'] = ('id', 'cliente', 'data', 'valor', 'detalhes')
        self.tree_dividas.heading('id', text='ID')
        self.tree_dividas.heading('cliente', text='Cliente')
        self.tree_dividas.heading('data', text='Data')
        self.tree_dividas.heading('valor', text='Valor (MZN)')
        self.tree_dividas.heading('detalhes', text='Detalhes')
    
        self.tree_dividas.column('id', width=50, anchor='center')
        self.tree_dividas.column('cliente', width=150)
        self.tree_dividas.column('data', width=100, anchor='center')
        self.tree_dividas.column('valor', width=100, anchor='e')
        self.tree_dividas.column('detalhes', width=250)
    
    # Busca as dívidas com itens
        dividas = Divida.buscar_ativas(self.conn)
    
        for divida in dividas:
            data_formatada = datetime.strptime(divida.data_divida, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        
        # Adiciona a dívida como item pai
            parent = self.tree_dividas.insert('', 'end', values=(
                divida.id,
                divida.nome_cliente,
                data_formatada,
                f"{divida.valor_total:.2f}",
                f"{len(divida.itens)} itens - Clique para expandir"
            ), tags=('parent',))
        
        # Adiciona os itens como filhos
            for item in divida.itens:
                subtotal = item.quantidade * item.preco_unitario
                self.tree_dividas.insert(parent, 'end', values=(
                "",
                    item.nome_produto,
                    f"Qtd: {item.quantidade}",
                    f"Preço: {item.preco_unitario:.2f}",
                    f"Subtotal: {subtotal:.2f}"
                ), tags=('child',))
    
    # Configura estilos para diferenciar pais e filhos
        self.tree_dividas.tag_configure('parent', background='#f0f0f0', font=('Arial', 10, 'bold'))
        self.tree_dividas.tag_configure('child', font=('Arial', 9))
    
    # Adiciona bind para expandir/recolher ao clicar
        self.tree_dividas.bind('<Button-1>', self.toggle_expand)
    
    def toggle_expand(self, event):
        """Alterna entre expandir e recolher os itens da dívida"""
        region = self.tree_dividas.identify("region", event.x, event.y)
        if region == "heading":
            return  # Não faz nada se clicar no cabeçalho
    
        item = self.tree_dividas.identify('item', event.x, event.y)
        tag = self.tree_dividas.item(item, "tags")[0]
    
        if tag == 'parent':
            if self.tree_dividas.item(item, 'open'):
                self.tree_dividas.item(item, open=False)
                self.tree_dividas.set(item, 'detalhes', f"{len(self.tree_dividas.get_children(item))} itens - Clique para expandir")
            else:
                self.tree_dividas.item(item, open=True)
                self.tree_dividas.set(item, 'detalhes', f"{len(self.tree_dividas.get_children(item))} itens - Clique para recolher")

    def marcar_divida_paga(self):
        """Marca a dívida selecionada como paga"""
        item_selecionado = self.tree_dividas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma dívida para marcar como paga!")
            return
    
        item = item_selecionado[0]
        tags = self.tree_dividas.item(item, "tags")
    
    # Se clicou em um item filho, pega o pai
        if 'child' in tags:
            item = self.tree_dividas.parent(item)
    
        divida_id = self.tree_dividas.item(item, 'values')[0]
    
        if messagebox.askyesno("Confirmar", "Deseja realmente marcar esta dívida como paga?"):
            try:
                Divida.marcar_como_paga(self.conn, divida_id)
                messagebox.showinfo("Sucesso", "Dívida marcada como paga!")
                self.carregar_dividas()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao marcar dívida como paga: {str(e)}")
    
    def criar_aba_relatorios(self):
        """Cria a aba para relatórios e ganhos"""
        self.aba_relatorios = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_relatorios, text="Relatórios")
        
        # Frame para filtros
        frame_filtros = ttk.LabelFrame(self.aba_relatorios, text="Filtrar por Período")
        frame_filtros.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(frame_filtros, text="De:").pack(side='left', padx=5)
        self.entry_data_inicio = ttk.Entry(frame_filtros, width=12)
        self.entry_data_inicio.pack(side='left', padx=5)
        
        ttk.Label(frame_filtros, text="Até:").pack(side='left', padx=5)
        self.entry_data_fim = ttk.Entry(frame_filtros, width=12)
        self.entry_data_fim.pack(side='left', padx=5)
        
        ttk.Button(frame_filtros, text="Buscar", command=self.buscar_vendas_periodo).pack(side='left', padx=5)
        
        # Treeview para exibir vendas
        self.tree_vendas = ttk.Treeview(self.aba_relatorios, columns=('id', 'data', 'total'), show='headings')
        self.tree_vendas.heading('id', text='ID')
        self.tree_vendas.heading('data', text='Data')
        self.tree_vendas.heading('total', text='Total')
        self.tree_vendas.column('id', width=50)
        self.tree_vendas.column('data', width=150)
        self.tree_vendas.column('total', width=100)
        self.tree_vendas.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame para totais
        frame_totais = ttk.Frame(self.aba_relatorios)
        frame_totais.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(frame_totais, text="Total do Período:").pack(side='left')
        self.label_total_periodo = ttk.Label(frame_totais, text="MZN 0.00", font=('Arial', 12, 'bold'))
        self.label_total_periodo.pack(side='left', padx=10)
        
        # Preencher datas padrão (mês atual)
        hoje = datetime.now().date()
        primeiro_dia = hoje.replace(day=1)
        self.entry_data_inicio.insert(0, primeiro_dia.strftime('%Y-%m-%d'))
        self.entry_data_fim.insert(0, hoje.strftime('%Y-%m-%d'))
        
        # Buscar vendas do mês atual
        self.buscar_vendas_periodo()
    
    def criar_aba_configuracoes(self):
        """Cria a aba para configurações do sistema"""
        self.aba_config = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_config, text="Configurações")
        
        ttk.Label(self.aba_config, text="Configurações do Sistema", font=('Arial', 12)).pack(pady=20)
        
        # Botão para backup
        ttk.Button(self.aba_config, text="Fazer Backup do Banco de Dados", 
                  command=self.fazer_backup).pack(pady=10)
        
        # Botão para restaurar
        ttk.Button(self.aba_config, text="Restaurar Backup", 
                  command=self.restaurar_backup).pack(pady=10)
    
    def carregar_produtos(self, filtro=None):
        """Carrega os produtos no Treeview e no Combobox com opção de filtro avançado"""
        try:
        # Busca produtos (com filtro no banco de dados para melhor performance)
            produtos = Produto.buscar_todos(self.conn, filtro) if filtro else Produto.buscar_todos(self.conn)
        
        # Limpar Treeview
            self.tree_estoque.delete(*self.tree_estoque.get_children())
        
        # Preencher Treeview com formatação profissional
            for produto in produtos:
                self.tree_estoque.insert('', 'end', 
                                  values=(
                                      produto.id,
                                      produto.nome,
                                      f"MZN {produto.preco:,.2f}".replace(",", " "),  # Formato 1 000.00
                                      produto.quantidade
                                  ),
                                  tags=('estoque_baixo' if produto.quantidade < 10 else '',))
        
        # Destacar produtos com estoque baixo
            self.tree_estoque.tag_configure('estoque_baixo', background='#FFF3CD')  # Amarelo claro
        
        # Atualizar Combobox na aba de vendas com informações completas
            self.combo_produtos['values'] = [
            (f"{p.id} - {p.nome[:30]}{'...' if len(p.nome)>30 else ''} | MZN {p.preco:.2f} | Est: {p.quantidade}", p.id) 
                for p in produtos
        ]
        
        # Selecionar automaticamente o primeiro item se existir
            if produtos:
                self.combo_produtos.current(0)
                self.tree_estoque.focus_set()
                self.tree_estoque.selection_set(self.tree_estoque.get_children()[0])
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
            print(f"Erro em carregar_produtos: {e}")
    
    def salvar_produto(self):
        """Salva um novo produto ou atualiza um existente"""
        nome = self.entry_nome.get()
        preco = self.entry_preco.get()
        quantidade = self.entry_quantidade.get()
        
        if not nome or not preco or not quantidade:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            preco = float(preco)
            quantidade = int(quantidade)
        except ValueError:
            messagebox.showerror("Erro", "Preço e quantidade devem ser números válidos!")
            return
        
        produto = Produto(nome=nome, preco=preco, quantidade=quantidade)
        produto.salvar(self.conn)
        
        messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
        self.limpar_formulario()
        self.carregar_produtos()
    
    def limpar_formulario(self):
        """Limpa o formulário de cadastro de produtos"""
        self.entry_nome.delete(0, 'end')
        self.entry_preco.delete(0, 'end')
        self.entry_quantidade.delete(0, 'end')
    
    def adicionar_item_venda(self):
        """Adiciona um item à venda atual"""
        if not self.combo_produtos.get():
            messagebox.showerror("Erro", "Selecione um produto!")
            return
        
        try:
            qtd = int(self.entry_qtd_venda.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo!")
            return
        
        # Obter produto selecionado
        produto_idx = self.combo_produtos.current()
        produto_id = self.combo_produtos['values'][produto_idx][1]
        produto = Produto.buscar_por_id(self.conn, produto_id)
        
        # Verificar estoque
        if produto.quantidade < qtd:
            messagebox.showerror("Erro", f"Estoque insuficiente! Disponível: {produto.quantidade}")
            return
        
        # Calcular subtotal
        subtotal = produto.preco * qtd
        
        # Adicionar à lista de itens
        self.itens_venda.append({
            'produto_id': produto.id,
            'nome': produto.nome,
            'quantidade': qtd,
            'preco': produto.preco,
            'subtotal': subtotal
        })
        
        # Atualizar Treeview
        self.tree_itens.insert('', 'end', values=(
            produto.nome, qtd, f"MZN {produto.preco:.2f}", f"MZN {subtotal:.2f}"
        ))
        
        # Atualizar total
        self.total_venda += subtotal
        self.label_total.config(text=f"MZN {self.total_venda:.2f}")
        
        # Limpar campos
        self.entry_qtd_venda.delete(0, 'end')
    
    def finalizar_venda(self):
        """Finaliza a venda atual"""
        if not self.itens_venda:
            messagebox.showerror("Erro", "Nenhum item adicionado à venda!")
            return
        
        # Criar objeto Venda
        venda = Venda(total=self.total_venda)
        
        # Adicionar itens à venda
        for item in self.itens_venda:
            item_venda = ItemVenda(
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco'],
                subtotal=item['subtotal']
            )
            venda.itens.append(item_venda)
        
        # Salvar venda no banco de dados
        venda.salvar(self.conn)
        
        messagebox.showinfo("Sucesso", f"Venda finalizada com sucesso! Total: MZN {self.total_venda:.2f}")
        self.limpar_venda()
        self.carregar_produtos()  # Atualizar estoque
    
    def limpar_venda(self):
        """Limpa a venda atual"""
        self.itens_venda = []
        self.total_venda = 0.0
        self.label_total.config(text="MZN 0.00")
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
    
    def buscar_vendas_periodo(self):
        """Busca vendas no período especificado"""
        data_inicio = self.entry_data_inicio.get()
        data_fim = self.entry_data_fim.get()
        
        try:
            vendas = Venda.buscar_por_periodo(self.conn, data_inicio, data_fim)
            
            # Limpar Treeview
            for item in self.tree_vendas.get_children():
                self.tree_vendas.delete(item)
            
            # Preencher Treeview
            total_periodo = 0.0
            for venda in vendas:
                data_formatada = datetime.strptime(venda.data_venda, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                self.tree_vendas.insert('', 'end', values=(
                    venda.id, data_formatada, f"MZN {venda.total:.2f}"
                ))
                total_periodo += venda.total
            
            # Atualizar total do período
            self.label_total_periodo.config(text=f"MZN {total_periodo:.2f}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar vendas: {str(e)}")
    
    def fazer_backup(self):
        """Cria um backup do banco de dados"""
        try:
            from shutil import copyfile
            import os
            from datetime import datetime
            
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"loja_backup_{data_hora}.db")
            
            copyfile("loja.db", backup_file)
            messagebox.showinfo("Sucesso", f"Backup criado com sucesso em:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar backup:\n{str(e)}")
    
    def restaurar_backup(self):
        """Restaura um backup do banco de dados"""
        from tkinter import filedialog
        from shutil import copyfile
        
        try:
            arquivo = filedialog.askopenfilename(
                title="Selecione o arquivo de backup",
                filetypes=[("Banco de dados SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            
            if arquivo:
                # Fechar conexão atual
                self.conn.close()
                
                # Fazer cópia de segurança do banco atual
                from datetime import datetime
                data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
                copyfile("loja.db", f"loja_pre_restore_{data_hora}.db")
                
                # Restaurar backup
                copyfile(arquivo, "loja.db")
                
                # Reconectar
                self.conn = database.criar_conexao("loja.db")
                
                messagebox.showinfo("Sucesso", "Backup restaurado com sucesso!\nO sistema será reiniciado.")
                
                # Reiniciar aplicação
                self.root.destroy()
                root = tk.Tk()
                app = LojaApp(root)
                root.mainloop()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar backup:\n{str(e)}")
            # Tentar reconectar se houve erro
            self.conn = database.criar_conexao("loja.db")

def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()