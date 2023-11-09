#Importanto bibliotecas
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
import numpy as np
import datetime
from PIL import Image 
from datetime import datetime
from streamlit_folium import folium_static
from haversine import haversine

#============================================
# Início das funções 
# =========================================== 

def clean_code(df1):
    """ Está função tem a responsabilidade de limpar o dataframe

    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança de tipos das colunas de dados
    3. Remoção de espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo

    Input: DataFrame
    Output: DataFrame
    
    """
    
    # Removendo linhas vazias:
    linhas_removidas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['Weatherconditions'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['Type_of_order'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['Type_of_vehicle'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    linhas_removidas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()

    #2 Convertendo a coluna Delivery_person_Age de object para inteiro:
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    #3 Convertendo a coluna Delivery_person_Ratings de object para float:
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    #4 Convertendo a coluna Order_Date de object para data:
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    #5 Removendo linhas vazias e convertendo a coluna muliply_deliveries de object para int:
    linhas_removidas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_removidas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # Retirando os numeros da coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int)

    df1 = df1.reset_index( drop=True )

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    return df1

def top_entregadores(df1, top_asc):
    df_aux = round((df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City' , 'Delivery_person_ID' ])
                       .mean()
                       .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                       .reset_index()),3)

    df_1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df_final = pd.concat([df_1, df_2, df_3]).reset_index(drop=True)
    return df_final

#============================================ 
# Perfumarias do layout
#============================================
st.set_page_config(page_title='Visão Entregadores', page_icon=':motor_scooter:', layout='wide')

#============================================ 
# Início da estrutura lógica do código 
# ============================================

# Carregando dataset
df_raw = pd.read_csv('dataset/train.csv')

# Copiar a base
df_copy = df_raw.copy()

# Limpando os dados
df1 = clean_code(df_copy)

#============================================
# Barra lateral
# ===========================================

image=Image.open('logo.png')
st.sidebar.image(image, width=240)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivered in Town!')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite:')
date_slider = st.sidebar.slider(
    'Defina o intervalo de data',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11),
    max_value=datetime( 2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

st.sidebar.markdown('#### Powered by Pedro Castro')

#Filtro de Datas
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Tráfegos
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#============================================ 
# Layout StreamLit 
# ===========================================

st.markdown('# Marketplace - Visão Entregadores')

st.header('Visão Gerencial', divider='orange')

with st.container():
    st.markdown('## Métricas Gerais:') 

    col1, col2, col3, col4 = st.columns(4, gap='small')

    with col1:
        max = df1['Delivery_person_Age'].max()
        col1.metric(label = 'Maior idade:', value = max )

    with col2:
        min = df1['Delivery_person_Age'].min()
        col2.metric(label = 'Menor idade:', value = min )

    with col3:
        better = df1['Vehicle_condition'].max()
        col3.metric(label = 'Melhor condição:', value = better )

    with col4:
        worst = df1['Vehicle_condition'].min()
        col4.metric(label = 'Pior condição:', value = worst )

with st.container():
    st.markdown("""---""")
    st.markdown('##  Avaliações:')

    col1, col2 = st.columns(2, gap='small')
    
    with col1: 
        st.markdown('###### Avaliações por entregador:')
        df_aux = (round(df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                           .groupby(['Delivery_person_ID'])
                           .mean()
                           .reset_index(), 3))
        st.dataframe(df_aux)

    with col2:
        st.markdown('###### Avaliações médias por trânsito:')
        df_avg_std = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                        .groupby(['Road_traffic_density'])
                        .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
        df_avg_std.columns = ['Delivery_ratings_mean', 'Delivery_ratings_std']
        df_avg_std = df_avg_std.reset_index()
        st.dataframe(df_avg_std)

        st.markdown('###### Avaliações médias por clima:')
        df_avg_std = round((df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                        .groupby(['Weatherconditions'])
                        .agg({'Delivery_person_Ratings' : ['mean', 'std']})),3)
        df_avg_std.columns = ['Delivery_Weatherconditions_mean', 'Delivery_Weatherconditions_std']
        df_avg_std = df_avg_std.reset_index()
        st.dataframe(df_avg_std)

with st.container():
    st.markdown("""---""")
    st.markdown('##  Velociadade de entrega:')

    col1, col2 = st.columns(2, gap='small')

    with col1:
        st.markdown('###### Top entregadores mais rápidos:')
        df_final = top_entregadores(df1, top_asc=True)
        st.dataframe(df_final)

    with col2:
        st.markdown('###### Top entregadores mais lentos:')
        df_final = top_entregadores(df1, top_asc=False)
        st.dataframe(df_final)  
