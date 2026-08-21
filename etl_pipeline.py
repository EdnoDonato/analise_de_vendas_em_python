import sqlite3
import pandas as pd
import numpy as np

def executar_etl():
    # 1. Conexão ao banco de dados SQLite
    conn = sqlite3.connect('varejo_analytics.db')

    # 2. Extração via SQL (Modelo Estrela / Star Schema)
    query_sql = """
    SELECT 
        v.id_venda,
        v.data_venda,
        v.status,
        l.nome_loja,
        l.tipo AS tipo_loja,
        l.cidade AS cidade_loja,
        l.estado AS estado_loja,
        p.nome_produto,
        p.categoria,
        c.nome_cliente,
        c.estado AS estado_cliente,
        vend.nome_vendedor,
        v.quantidade,
        v.valor_bruto,
        v.desconto,
        v.valor_liquido,
        v.custo_total
    FROM fato_vendas v
    LEFT JOIN dim_lojas l ON v.id_loja = l.id_loja
    LEFT JOIN dim_produtos p ON v.id_produto = p.id_produto
    LEFT JOIN dim_clientes c ON v.id_cliente = c.id_cliente
    LEFT JOIN dim_vendedores vend ON v.id_vendedor = vend.id_vendedor
    """

    df_raw = pd.read_sql_query(query_sql, conn)
    conn.close()

    # 3. Transformação (ETL com Pandas)
    df_raw['data_venda'] = pd.to_datetime(df_raw['data_venda'])
    df_raw['ano_mes'] = df_raw['data_venda'].dt.to_period('M')

    # Aplicação de Regra de Negócio Financeira:
    # - Vendas Concluídas: geram Receita Líquida, Custo e Lucro Real.
    # - Cancelamentos / Devoluções: geram Perda Operacional e ZERAM a Receita Líquida Real.
    def aplicar_regras_financeiras(row):
        if row['status'] == 'Concluída':
            receita_real = row['valor_liquido']
            custo_real = row['custo_total']
            lucro_bruto = receita_real - custo_real
            perda_operacional = 0.0
        else:
            receita_real = 0.0
            custo_real = 0.0
            lucro_bruto = 0.0
            perda_operacional = row['valor_liquido']
            
        return pd.Series([receita_real, custo_real, lucro_bruto, perda_operacional], 
                         index=['receita_real', 'custo_real', 'lucro_bruto', 'perda_operacional'])

    df_transformed = df_raw.join(df_raw.apply(aplicar_regras_financeiras, axis=1))

    # 4. Cálculo de Métricas Agregadas
    # A) Performance por Canal (Físico vs Online)
    resumo_canal = df_transformed.groupby('tipo_loja').agg({
        'id_venda': 'count',
        'valor_bruto': 'sum',
        'desconto': 'sum',
        'receita_real': 'sum',
        'lucro_bruto': 'sum',
        'perda_operacional': 'sum'
    }).reset_index()

    resumo_canal['margem_media_%'] = round((resumo_canal['lucro_bruto'] / resumo_canal['receita_real']) * 100, 2)
    resumo_canal['ticket_medio'] = round(resumo_canal['receita_real'] / resumo_canal['id_venda'], 2)

    # B) Performance por Categoria
    resumo_categoria = df_transformed.groupby('categoria').agg({
        'receita_real': 'sum',
        'lucro_bruto': 'sum',
        'perda_operacional': 'sum'
    }).reset_index().sort_values(by='lucro_bruto', ascending=False)

    resumo_categoria['margem_%'] = round((resumo_categoria['lucro_bruto'] / resumo_categoria['receita_real']) * 100, 2)

    return df_transformed, resumo_canal, resumo_categoria

if __name__ == '__main__':
    df, canal, cat = executar_etl()
    print("ETL concluído com sucesso!")
    print("\n--- RESUMO CANAL DE VENDAS ---")
    print(canal)
    print("\n--- PERFORMANCE POR CATEGORIA ---")
    print(cat)