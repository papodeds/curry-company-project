import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon=':curry:',
    layout='wide'
)

image=Image.open('logo.png')
st.sidebar.image(image, width=240)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivered in Town!')

st.sidebar.markdown("""---""")

st.sidebar.markdown('#### Powered by Pedro Castro')

st.write('# :curry: Curry Company - Growth Dashboard')

st.markdown(
    """
        Esse Growth Dashboard foi construído para acompanhar as métricas de crescimento da empresa Curry Company.
        ### Como utilizar o Growth Dashboard?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de localização.
        - Visão Entregadores:
            - Acompanhamento dos indicadores semanais de crescimento.
        - Visão Restaurantes:
            - Indicadores semanais de crescimento dos restaurantes.
        ### Entre em contato:
        - Time de Data Science no Discord
            - @phcastro03
    """
)