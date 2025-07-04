import streamlit as st
import requests
import pandas as pd
import plotly.express as px

#st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS \U0001F6D2')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

##Tabelas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = (dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']]
                       .merge(receita_estados, left_on='Local da compra', right_index=True)
                       .sort_values('Preço', ascending=False))

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = (dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']]
                  .merge(vendas_estados, left_on = 'Local da compra', right_index = True)
                  .sort_values('Preço', ascending = False))

vendas_mensal = (pd.DataFrame(dados.set_index('Data da Compra')
                              .groupby(pd.Grouper(freq = 'M'))['Preço']
                              .count())
                              .reset_index())

vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = (pd.DataFrame(dados.groupby('Categoria do Produto')['Preço']
                                  .count()
                                  .sort_values(ascending = False)))

##Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat':False, 'lon':False},
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal, 
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title='Receita')

fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

##Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita) #use_container_width = True
        st.plotly_chart(fig_receita_estados)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal) #use_container_width = True
        st.plotly_chart(fig_receita_categorias)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas)
        st.plotly_chart(fig_vendas_estados)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal)
        st.plotly_chart(fig_vendas_categorias)

with aba3:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))

#st.dataframe(dados)