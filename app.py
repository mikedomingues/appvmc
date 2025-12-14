import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

st.set_page_config(page_title="Base de Dados de Nomes", page_icon="👤", layout="centered")

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

# Função para exportar para PDF
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Lista de Nomes", ln=True, align="C")

    # Cabeçalho
    pdf.cell(100, 10, "Nome", 1, 0, "C")
    pdf.cell(40, 10, "Visível", 1, 1, "C")

    # Linhas
    for _, row in df.iterrows():
        pdf.cell(100, 10, str(row["Nome"]), 1, 0)
        pdf.cell(40, 10, str(row["Visível"]), 1, 1)

    return pdf.output(dest="S").encode("latin-1")

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
        novo_df = pd.DataFrame([{"Nome": novo_nome.strip(), "Visível": True}])
        df = pd.concat([df, novo_df], ignore_index=True)
        save_data(df)
        st.success(f"Nome '{novo_nome}' adicionado com sucesso!")
        st.stop()  # evita crash do experimental_rerun

# Secção para gerir nomes
st.subheader("Gerir Nomes")
for i, row in df.iterrows():
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    col1.write(row["Nome"])
    if row["Visível"]:
        if col2.button("Ocultar", key=f"hide_{i}"):
            df.at[i, "Visível"] = False
            save_data(df)
            st.stop()
    else:
        if col2.button("Reativar", key=f"show_{i}"):
            df.at[i, "Visível"] = True
            save_data(df)
            st.stop()
    if col3.button("Eliminar", key=f"delete_{i}"):
        df = df.drop(i).reset_index(drop=True)
        save_data(df)
        st.stop()

# Exportar CSV
st.download_button("📥 Exportar CSV", data=df.to_csv(index=False), file_name="nomes.csv", mime="text/csv")

# Exportar PDF
pdf_bytes = export_pdf(df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="nomes.pdf", mime="application/pdf")
