import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Gestão de Nomes", page_icon="👤", layout="centered")

# Caminho do ficheiro CSV
DB_FILE = "nomes.csv"

# Função para carregar a base de dados
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

# Função para guardar a base de dados
def save_data(df):
    df.to_csv(DB_FILE, index=False)

# Carregar dados existentes
df = load_data()

st.title("👤 Base de Dados de Nomes")

# Mostrar tabela apenas com nomes visíveis
st.subheader("Lista de Nomes Ativos")
st.dataframe(df[df["Visível"] != False], use_container_width=True)

# Formulário para adicionar nome
st.subheader("Adicionar Novo Nome")
with st.form("add_name_form"):
    novo_nome = st.text_input("Escreve o nome")
    submitted = st.form_submit_button("Adicionar")
    if submitted and novo_nome.strip():
        df = df.append({"Nome": novo_nome.strip(), "Visível": True}, ignore_index=True)
        save_data(df)
        st.success(f"Nome '{novo_nome}' adicionado com sucesso!")
        st.experimental_rerun()

# Secção para gerir nomes
st.subheader("Gerir Nomes")
for i, row in df.iterrows():
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    col1.write(row["Nome"])
    if row["Visível"]:
        if col2.button("Ocultar", key=f"hide_{i}"):
            df.at[i, "Visível"] = False
            save_data(df)
            st.experimental_rerun()
    else:
        if col2.button("Reativar", key=f"show_{i}"):
            df.at[i, "Visível"] = True
            save_data(df)
            st.experimental_rerun()
    if col3.button("Eliminar", key=f"delete_{i}"):
        df = df.drop(i).reset_index(drop=True)
        save_data(df)
        st.experimental_rerun()
