import sqlite3
import pandas as pd

# Carregar os CSVs gerados na Etapa 1
df_lojas = pd.read_csv('dim_lojas.csv')
df_vendedores = pd.read_csv('dim_vendedores.csv')
df_clientes = pd.read_csv('dim_clientes.csv')
df_produtos = pd.read_csv('dim_produtos.csv')
df_vendas = pd.read_csv('fato_vendas.csv')

# Conectar e gravar todas as tabelas no arquivo .db
conn = sqlite3.connect('varejo_analytics.db')

df_lojas.to_sql('dim_lojas', conn, if_exists='replace', index=False)
df_vendedores.to_sql('dim_vendedores', conn, if_exists='replace', index=False)
df_clientes.to_sql('dim_clientes', conn, if_exists='replace', index=False)
df_produtos.to_sql('dim_produtos', conn, if_exists='replace', index=False)
df_vendas.to_sql('fato_vendas', conn, if_exists='replace', index=False)

conn.close()
print("Banco varejo_analytics.db atualizado com sucesso!")