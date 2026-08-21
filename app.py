import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard Executivo de Vendas",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS para ajustar cards de métricas
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. Função de Carregamento dos Dados via SQLite + ETL
@st.cache_data
def carregar_dados():
    caminho_pasta = os.path.dirname(os.path.abspath(__file__))
    caminho_db = os.path.join(caminho_pasta, 'varejo_analytics.db')
    conn = sqlite3.connect(caminho_db)
    
    query = """
    SELECT 
        v.id_venda, v.data_venda, v.status,
        l.nome_loja, l.tipo AS tipo_loja, l.estado AS estado_loja,
        p.nome_produto, p.categoria,
        c.nome_cliente, c.estado AS estado_cliente,
        vend.nome_vendedor,
        v.quantidade, v.valor_bruto, v.desconto, v.valor_liquido, v.custo_total
    FROM fato_vendas v
    LEFT JOIN dim_lojas l ON v.id_loja = l.id_loja
    LEFT JOIN dim_produtos p ON v.id_produto = p.id_produto
    LEFT JOIN dim_clientes c ON v.id_cliente = c.id_cliente
    LEFT JOIN dim_vendedores vend ON v.id_vendedor = vend.id_vendedor
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    
    # Aplicação de Regras Financeiras
    def aplicar_financeiro(row):
        if row['status'] == 'Concluída':
            rec = row['valor_liquido']
            custo = row['custo_total']
            lucro = rec - custo
            perda = 0.0
        else:
            rec, custo, lucro = 0.0, 0.0, 0.0
            perda = row['valor_liquido']
        return pd.Series([rec, custo, lucro, perda], 
                         index=['receita_real', 'custo_real', 'lucro_bruto', 'perda_operacional'])

    df[['receita_real', 'custo_real', 'lucro_bruto', 'perda_operacional']] = df.apply(aplicar_financeiro, axis=1)
    return df

df = carregar_dados()

# 3. Barra Lateral de Filtros
st.sidebar.header("🔍 Filtros Globais")

# Filtro de Período
min_data = df['data_venda'].min().date()
max_data = df['data_venda'].max().date()
data_inicio, data_fim = st.sidebar.date_input("Período:", [min_data, max_data])

# Filtro de Canal (Físico vs Online)
canais_disponiveis = df['tipo_loja'].unique().tolist()
canais_selecionados = st.sidebar.multiselect("Canal de Venda:", canais_disponiveis, default=canais_disponiveis)

# Filtro de Categoria
categorias_disponiveis = df['categoria'].unique().tolist()
categorias_selecionadas = st.sidebar.multiselect("Categoria:", categorias_disponiveis, default=categorias_disponiveis)

# Aplicação dos Filtros no DataFrame
df_filtrado = df[
    (df['data_venda'].dt.date >= data_inicio) &
    (df['data_venda'].dt.date <= data_fim) &
    (df['tipo_loja'].isin(canais_selecionados)) &
    (df['categoria'].isin(categorias_selecionadas))
]

# 4. Cabeçalho
st.title("📊 Painel Executivo de Performance de Vendas")
st.markdown("Análise financeira integrada de lojas físicas e e-commerce.")
st.markdown("---")

# 5. Métricas e KPIs
rec_total = df_filtrado['receita_real'].sum()
lucro_total = df_filtrado['lucro_bruto'].sum()
perdas_totais = df_filtrado['perda_operacional'].sum()
total_pedidos = len(df_filtrado[df_filtrado['status'] == 'Concluída'])
ticket_medio = rec_total / total_pedidos if total_pedidos > 0 else 0
margem_pct = (lucro_total / rec_total * 100) if rec_total > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Receita Líquida Real", f"R$ {rec_total:,.2f}")
kpi2.metric("Lucro Bruto", f"R$ {lucro_total:,.2f}", f"{margem_pct:.1f}% margem")
kpi3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
kpi4.metric("Perda (Devoluções/Canc.)", f"R$ {perdas_totais:,.2f}", delta_color="inverse")
kpi5.metric("Pedidos Concluídos", f"{total_pedidos:,}")

st.markdown("---")

# 6. Gráficos Principais (Linha 1)
col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    # Evolução Mensal da Receita e Lucro
    df_mensal = df_filtrado.set_index('data_venda').resample('M').agg({
        'receita_real': 'sum',
        'lucro_bruto': 'sum',
        'perda_operacional': 'sum'
    }).reset_index()
    df_mensal['Data'] = df_mensal['data_venda'].dt.strftime('%b/%Y')

    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(x=df_mensal['Data'], y=df_mensal['receita_real'], name="Receita Real", line=dict(color='#0083B0', width=3)))
    fig_evo.add_trace(go.Scatter(x=df_mensal['Data'], y=df_mensal['lucro_bruto'], name="Lucro Bruto", line=dict(color='#2E7D32', width=3)))
    fig_evo.add_trace(go.Bar(x=df_mensal['Data'], y=df_mensal['perda_operacional'], name="Perda Operacional", marker_color='#D32F2F', opacity=0.5))
    fig_evo.update_layout(title="Evolução Mensal (Receita vs Lucro vs Perdas)", template="plotly_white", barmode="overlay")
    st.plotly_chart(fig_evo, use_container_width=True)

with col_g2:
    # Distribuição por Categoria
    df_cat = df_filtrado.groupby('categoria')['receita_real'].sum().reset_index()
    fig_pie = px.pie(df_cat, values='receita_real', names='categoria', title="Receita por Categoria", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_pie, use_container_width=True)

# 7. Gráficos Secundários (Linha 2)
col_g3, col_g4 = st.columns(2)

with col_g3:
    # Desempenho por Loja
    df_loja = df_filtrado.groupby('nome_loja').agg({'receita_real': 'sum', 'lucro_bruto': 'sum'}).reset_index()
    fig_bar = px.bar(df_loja, x='nome_loja', y=['receita_real', 'lucro_bruto'], 
                     title="Performance por Filial/Canal", barmode='group',
                     labels={'value': 'Valor (R$)', 'variable': 'Métrica'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g4:
    # Tabela com Detalhamento
    st.subheader("📋 Tabela de Transações Filtradas")
    st.dataframe(
        df_filtrado[['data_venda', 'nome_loja', 'categoria', 'nome_produto', 'status', 'receita_real', 'lucro_bruto']]
        .sort_values(by='data_venda', ascending=False),
        use_container_width=True,
        height=350
    )