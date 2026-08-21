# 📊 Dashboard Executivo de Vendas & Performance Financeira (Omnichannel)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-green?style=flat&logo=sqlite)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?style=flat&logo=pandas)

Projeto completo end-to-end de Engenharia e Análise de Dados para o setor de varejo. O projeto engloba desde a **modelagem relacional** e **geração de dados sintéticos**, passando por **pipelines de ETL com regras de negócio financeiras**, até a construção de um **Dashboard Interativo** para tomada de decisão executiva.

---

## 🎯 Objetivos do Projeto

* **Modelagem Relacional:** Estruturação de um banco de dados relacional em *Star Schema* (Modelo Estrela) com tabela Fato e Dimensões.
* **Métricas Financeiras Reais:** Distinção entre Receita Bruta, Receita Líquida Real, Lucro Bruto e Perdas Operacionais (provenientes de cancelamentos e devoluções).
* **Análise Omnichannel:** Comparativo de desempenho entre lojas físicas e e-commerce.

---

## 🏗️ Arquitetura e Estrutura dos Dados

O banco de dados `varejo_analytics.db` possui 5 tabelas integradas:

dim_clientes: ID, Nome, Estado, Data de Cadastro, Canal Preferencial.

dim_lojas: ID, Nome da Loja, Cidade, Estado, Tipo (Física ou Online).

dim_vendedores: ID, Nome, ID_Loja, Meta Mensal.

dim_produtos: ID, Nome, Categoria, Custo Unitário, Preço Venda.

fato_vendas: ID_Venda, Data, ID_Cliente, ID_Loja, ID_Vendedor, ID_Produto, Quantidade, Valor_Total, Desconto, Status (Concluída, Cancelada, Devolvida).

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Pandas & NumPy:** Manipulação, limpeza e transformação de dados (ETL).
* **SQLite3:** Persistência e consultas SQL avançadas (`JOINs`, agregação).
* **Plotly:** Visualizações gráficas interativas e dinâmicas.
* **Streamlit:** Construção da aplicação web/dashboard.
