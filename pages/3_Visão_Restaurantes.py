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
    """
    Está função tem a responsabilidade de limpar o dataframe

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

def distancia(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]

    df1['Distance'] = round(df1.loc[:, cols].apply( lambda x:
                                haversine(
                                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1),2)

    avg_distance = round(df1['Distance'].mean(),2)
    return avg_distance

def tempo_entrega(df1, festival, op):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmentros:
            Input:
                - df: DataFrame com os dados necessários para o cálculo
                - op: Tipo de operação desejada
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão
            Output:
                 - df: DataFrame com 2 colunas e 1 linha.
            """
    df_aux = (df1.loc[:, [ 'Festival', 'Time_taken(min)']]
                 .groupby(['Festival'])
                 .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = round(df_aux.loc[df_aux['Festival'] == festival, op],2)
    return df_aux

def tempo_medio_desvpad(df1):
    cols = ['City', 'Time_taken(min)']
    df_aux = (df1.loc[:, cols]
                 .groupby(['City'])
                 .agg({'Time_taken(min)' : ['mean', 'std']})) 
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace (go.Bar(name='Control',
                            x=df_aux['City'],
                            y=df_aux['avg_time'],
                            error_y=dict( type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def tempo_medio_desvpad_cidade_pedido (df1):
    cols = ['City', 'Type_of_order', 'Time_taken(min)']

    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Type_of_order'])
                 .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'st_time']

    df_aux = df_aux.reset_index()
    return df_aux

def med_desvpad_cidade_trafego(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

    df1['distance'] = (df1.loc[:, cols]
                          .apply(lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                   (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                                   axis=1))
       
    avg_distance = (df1.loc[:, ['City', 'distance']]
                       .groupby('City')
                       .mean()
                       .reset_index())

    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    return fig

def med_restaurante_entrega(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']

    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Road_traffic_density'])
                 .agg({'Time_taken(min)' : ['mean', 'std']}))
        
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

#============================================ 
# Perfumarias do layout
#============================================
st.set_page_config(page_title='Visão Restaurantes', page_icon=':fork_and_knife:', layout='wide')

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
st.markdown('# Marketplace - Visão Restaurantes')

#st.header('Visão Gerencial', divider='gray')
st.markdown("## Visão Gerencial\n---")

with st.container():
    st.markdown('## Métricas Gerais:') 

    col1, col2, col3 = st.columns(3, gap='small')

    with col1:
        entregadores = df1['Delivery_person_ID'].nunique()
        st.markdown('###### Entregadores cadastrados para realizar entregas:')
        col1.metric(label = '', value = entregadores )

    with col2:
        avg_distance = distancia(df1)
        st.markdown('###### Distância média até as entregas:')
        col2.metric(label = '', value=avg_distance)

    with col3:
        df_aux = tempo_entrega(df1, 'Yes', 'avg_time')
        st.markdown('###### Tempo médio de entrega com Festival:')
        col3.metric(label = '', value = df_aux )

with st.container():

    col4, col5, col6 = st.columns(3, gap='small')

    with col4:
        df_aux = tempo_entrega(df1, 'Yes', 'std_time')
        st.markdown('###### Desvio padrão de entrega com Festival:')
        col4.metric(label = '', value = df_aux )

    with col5:
        df_aux = tempo_entrega(df1, 'No', 'avg_time')
        st.markdown('###### Tempo médio de entrega sem Festival:')
        col5.metric(label = '', value = df_aux )

    with col6:
        df_aux = tempo_entrega(df1, 'No', 'std_time')
        st.markdown('###### Desvio padrão de entrega sem Festival:')
        col6.metric(label = '', value = df_aux )

with st.container():
    st.markdown("""---""")
    st.markdown('##  Tempo médio de entregas por cidade:')

    col1, col2 = st.columns(2, gap='small')

    with col1: 
        st.markdown('###### O tempo médio e o desvio padrão de entregas por cidade:')
        fig = tempo_medio_desvpad(df1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('###### O tempo médio e o desvio padrão de entregas por cidade e tipo de pedido:')
        df_aux = tempo_medio_desvpad_cidade_pedido (df1)
        st.dataframe(df_aux)
   
with st.container():
    st.markdown("""---""")
    st.markdown('##  Distribuição do Tempo:')

    col1, col2 = st.columns(2, gap='small')
    
    with col1: 
        st.markdown('###### O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego:')
        fig = med_desvpad_cidade_trafego(df1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('###### A distância média dos resturantes e dos locais de entrega:')
        fig = med_restaurante_entrega(df1)
        st.plotly_chart(fig, use_container_width=True)
