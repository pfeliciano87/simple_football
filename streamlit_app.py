# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 13:58:11 2025

@author: pmbfe
"""

import streamlit as st
import pandas as pd
import numpy as np


# Carregar os dados (substituir pelo caminho real do ficheiro se necessário)
# df = pd.DataFrame({
#     "Nome": ["Jogador A", "Jogador B", "Jogador C", "Jogador D", "Jogador E"],
#     "Clube": ["Clube X", "Clube Y", "Clube Z", "Clube X", "Clube Y"],
#     "Liga": ["Liga 1", "Liga 2", "Liga 1", "Liga 3", "Liga 2"],
#     "Posição": ["Avançado", "Médio", "Defesa", "Avançado", "Médio"],
#     "Idade": [25, 30, 22, 27, 29],
#     "Score": [90, 85, 88, 92, 80]
# })

@st.cache_data
def load_data():
    return pd.read_excel('database.xlsx').drop(columns='Unnamed: 0')  # Or load it however needed

def convert_to_int(value):
    if isinstance(value, str):  # Check if the value is a string
        value = value.replace(" €", "").strip()  # Remove €
        value = value.replace("(Highest)", "").strip()  # Remove €

        if "M" in value:
            return int(float(value.replace("M", "")) * 1_000_000)
        elif "K" in value:
            return int(float(value.replace("K", "")) * 1_000)
        return int(value)  # If it's already a number in string format
    return value  # If not a string, return as is


df2 = load_data()
df2['Valor'].fillna(0,inplace=True)
df2["Valor"] = df2["Valor"].apply(convert_to_int)

df_pivot_valores = pd.pivot_table(data=df2,index=['Clube'],values=['Valor'],aggfunc='sum')
df_pivot_valores.columns = ['Valor do Clube']

df2.dropna(subset=['Score','IntraTeamScore','JogosFeitos'],inplace=True)

df2['JogosFeitos'] = df2.apply(lambda row: int(row['JogosFeitos'][:-12]),axis=1)
df3 = df2[df2['JogosFeitos']>=5].copy()

df_pivot = pd.pivot_table(data=df3,index=['Liga','Clube','Posicao'],values=['Score','IntraTeamScore'],aggfunc=np.max).reset_index()
df = df_pivot

df = df.merge(df_pivot_valores,on='Clube',how='left').copy()

# df = pd.read_excel('database.xlsx')

# Título e descrição
st.title("Simple Football")
st.markdown("Uma ferramenta simples para analisar jogadores de futebol com base em suas ligas, posições e pontuações.")

st.header("Filtragem de Jogadores de Futebol")

# Seleção de Ligas
ligas_disponiveis = df["Liga"].unique()
ligas_escolhidas = st.multiselect("Escolha as Ligas:", ligas_disponiveis, default=ligas_disponiveis)

# Slider com o valor do clube
min_valor_clube, max_valor_clube = st.slider("Escolha o intervalo de Valor do clube:", 
                                 min_value=int(df["Valor do Clube"].min()), 
                                 max_value=int(df["Valor do Clube"].max()), 
                                 value=(int(df["Valor do Clube"].min()), int(df["Valor do Clube"].max())),
                                 format="%d")
st.write(f"Intervalo selecionado: **{min_valor_clube:,.0f}** - **{max_valor_clube:,.0f}**")


# Seleção de Posições
posicoes_disponiveis = df["Posicao"].unique()
posicoes_escolhidas = st.multiselect("Escolha as Posições:", posicoes_disponiveis, default=posicoes_disponiveis)

# Ordenação
ordem = st.radio("Ordenar por Score:", ["Ascendente", "Descendente"])
ordem_ascendente = ordem == "Ascendente"

# Adicionar um botão para atualizar
if st.button("Atualizar tabela"):
    st.session_state["update"] = True

if "update" in st.session_state and st.session_state["update"]:
    # Filtrar os dados
    filtro_df = df[(df["Liga"].isin(ligas_escolhidas)) & (df["Posicao"].isin(posicoes_escolhidas)) & (df['Valor do Clube'] >= min_valor_clube) & (df['Valor do Clube'] <= max_valor_clube) ]

    # Ordenar os dados
    filtro_df = filtro_df.sort_values(by="Score", ascending=ordem_ascendente)

    # Exibir tabela
    st.dataframe(filtro_df)
    
    clubes_disponiveis = filtro_df['Clube'].unique()
    clube_escolhido = st.selectbox("Escolha um Clube:", clubes_disponiveis)
    # Apply club filter only if a specific club is selected
    filtered_df_position = df[df['Clube']== clube_escolhido]
    
    filtered_df_players = df3[df3["Clube"] == clube_escolhido]
    # filtered_df_position['IntraTeamScore'] = filtered_df_position['IntraTeamScore'] - 1
    
    st.bar_chart(filtered_df_position,x='Posicao',y='IntraTeamScore')
    
    st.dataframe(filtered_df_players)

