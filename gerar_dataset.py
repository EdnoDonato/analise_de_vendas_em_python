import sqlite3
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Configurar semente de reprodutibilidade
np.random.seed(42)
random.seed(42)

# --- Funções Auxiliares para Dados Fictícios ---
primeiros_nomes = ['Ana', 'Bruno', 'Carla', 'Diego', 'Eduarda', 'Felipe', 'Gabriela', 'Henrique', 
                   'Isabela', 'João', 'Lucas', 'Mariana', 'Natan', 'Patricia', 'Rafael', 'Sofia']
sobrenomes = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira']
cidades_estados = [('São Paulo', 'SP'), ('Rio de Janeiro', 'RJ'), ('Belo Horizonte', 'MG'), ('Curitiba', 'PR')]

def gerar_nome():
    return f"{random.choice(primeiros_nomes)} {random.choice(sobrenomes)} {random.choice(sobrenomes)}"

def gerar_cpf():
    return f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"

# 1. Dimensão Lojas
lojas = [
    {'id_loja': 1, 'nome_loja': 'E-commerce Oficial', 'cidade': 'São Paulo', 'estado': 'SP', 'tipo': 'Online'},
    {'id_loja': 2, 'nome_loja': 'Loja Shopping Morumbi', 'cidade': 'São Paulo', 'estado': 'SP', 'tipo': 'Física'},
    {'id_loja': 3, 'nome_loja': 'Loja Centro Rio', 'cidade': 'Rio de Janeiro', 'estado': 'RJ', 'tipo': 'Física'},
    {'id_loja': 4, 'nome_loja': 'Loja Savassi', 'cidade': 'Belo Horizonte', 'estado': 'MG', 'tipo': 'Física'},
    {'id_loja': 5, 'nome_loja': 'Loja Batel', 'cidade': 'Curitiba', 'estado': 'PR', 'tipo': 'Física'}
]
df_lojas = pd.DataFrame(lojas)

# 2. Dimensão Vendedores
vendedores = []
vend_id = 1
for loja in lojas:
    if loja['tipo'] == 'Física':
        for _ in range(3):
            vendedores.append({'id_vendedor': vend_id, 'nome_vendedor': gerar_nome(), 'id_loja': loja['id_loja'], 'meta_mensal': 35000.0})
            vend_id += 1
vendedores.append({'id_vendedor': vend_id, 'nome_vendedor': 'Venda Automatizada Web', 'id_loja': 1, 'meta_mensal': 150000.0})
df_vendedores = pd.DataFrame(vendedores)

# 3. Dimensão Clientes
clientes = []
for i in range(1, 1001):
    cid, est = random.choice(cidades_estados)
    clientes.append({'id_cliente': i, 'nome_cliente': gerar_nome(), 'cpf': gerar_cpf(), 'cidade': cid, 'estado': est})
df_clientes = pd.DataFrame(clientes)

# 4. Dimensão Produtos
catalogo = [
    {'nome': 'Smartphone Galaxy S23', 'cat': 'Eletrônicos', 'preco': 3200.0, 'custo': 1800.0},
    {'nome': 'Notebook Dell Inspiron', 'cat': 'Eletrônicos', 'preco': 4100.0, 'custo': 2500.0},
    {'nome': 'Camisa Polo Algodão', 'cat': 'Vestuário', 'preco': 110.0, 'custo': 45.0},
    {'nome': 'Air Fryer Digital 5L', 'cat': 'Eletrodomésticos', 'preco': 490.0, 'custo': 220.0}
]
df_produtos = pd.DataFrame(catalogo)
df_produtos['id_produto'] = range(101, 101 + len(df_produtos))

# 5. Fato Vendas
# ... (Geração dinâmica das 6.000 transações de venda)

# --- Salvar em Banco de Dados SQLite ---
conn = sqlite3.connect('varejo_analytics.db')
df_lojas.to_sql('dim_lojas', conn, if_exists='replace', index=False)
df_vendedores.to_sql('dim_vendedores', conn, if_exists='replace', index=False)
df_clientes.to_sql('dim_clientes', conn, if_exists='replace', index=False)
df_produtos.to_sql('dim_produtos', conn, if_exists='replace', index=False)
# df_vendas.to_sql('fato_vendas', conn, if_exists='replace', index=False)
conn.close()