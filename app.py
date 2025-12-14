import streamlit as st

st.set_page_config(
    page_title="App VMC",
    page_icon="📑",
    layout="centered"
)

st.title("📑 Bem-vindo à App VMC")

st.markdown("""
Esta aplicação está dividida em várias páginas:

- 👤 **Gestão de Nomes** — Adiciona, oculta, reativa e exporta nomes
- 📅 **Gestão de Reuniões** — Atribui partes, organiza reuniões e exporta relatórios

Usa o menu lateral à esquerda para navegar entre elas.
""")
