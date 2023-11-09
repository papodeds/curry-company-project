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

def pedidos_diarios(df1):
    df_aux = (df1.loc[:, ['ID', 'Order_Date']]
                 .groupby(['Order_Date'])
                 .count()
                 .reset_index())
    fig = px.bar (df_aux, x = 'Order_Date', y = 'ID')
    return fig

def pedidos_trafego(df1):
    df_aux = (df1.loc [:, ['ID', 'Road_traffic_density']]
                 .groupby(['Road_traffic_density'])
                 .count()
                 .reset_index())
    df_aux['Delivery_Perc'] = (df_aux['ID'] / df_aux['ID'].sum())
    fig = px.pie(df_aux, values='Delivery_Perc', names='Road_traffic_density')
    return fig

def pedidos_cidade(df1):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', color='City', size= 'ID')     
    return fig

def pedidos_semanais(df1):
    df1['Week_Date'] = df1['Order_Date'].dt.strftime ('%U')
    dx_aux = (df1.loc[: , ['ID', 'Week_Date']]
                 .groupby(['Week_Date'])
                 .count()
                 .reset_index())
    fig = px.line( dx_aux, x ='Week_Date', y = 'ID')
    return fig

def pedidos_entregadores(df1):
    df_aux1 = (df1.loc[:, ['ID', 'Week_Date']]
                  .groupby(['Week_Date'])
                  .count()
                  .reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'Week_Date']]
                .groupby(['Week_Date'])
                .nunique()
                .reset_index())
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_Date', y='Order_by_deliver')
    return fig

def mapa_pedidos(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map();

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)
    return None

#============================================ 
# Perfumarias do layout
#============================================
st.set_page_config(page_title='Visão Empresa', page_icon=':bar_chart:', layout='wide')

#============================================ 
# Início da estrutura lógica do código 
# ============================================

# Carregando dataset
df_raw = pd.read_csv('../FTC/dataset/train.csv')

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
st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Gráfico 1 - Pedidos por dia
        st.markdown('### Pedidos por dia')
        fig = pedidos_diarios(df1)
        st.plotly_chart(fig, use_container_width=True)


    with st.container():
        col1, col2 = st.columns(2, gap='small')

        with col1:
            #Gráfico 2 - Pedidos por tipo de tráfego
            st.markdown('### Pedidos por tipo de tráfego')
            fig = pedidos_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            #Gráfico 3 - Pedidos por cidade
            st.markdown('### Pedidos por cidade')
            fig = pedidos_cidade(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        #Gráfico 1 - Pedidos por semana
        st.markdown('### Pedidos por semana')
        fig = pedidos_semanais(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        #Gráfico 2 - Pedidos por entregador por semana
        st.markdown('### Pedidos por entregador por semana')
        fig = pedidos_entregadores(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    #Gráfico 1 - Mapa de pedidos
    st.markdown('### Mapa de pedidos')
    mapa_pedidos(df1)