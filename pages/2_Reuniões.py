import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

DB_FILE = "nomes.csv"
PARTES_FILE = "partes.csv"

def load_nomes():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

def load_partes():
    if os.path.exists(PARTES_FILE):
        return pd.read_csv(PARTES_FILE)
    else:
        return pd.DataFrame(columns=["Parte", "Responsável"])

def save_partes(df):
    df.to_csv(PARTES_FILE, index=False)

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Partes da Reunião", ln=True, align="C")

    pdf.cell(100, 10, "Parte", 1, 0, "C")
    pdf.cell(80, 10, "Responsável", 1, 1, "C")

    for _, row in df.iterrows():
        pdf.cell(100, 10, str(row["Parte"]), 1, 0)
        pdf.cell(80, 10, str(row["Responsável"]), 1, 1)

    return pdf.output(dest="S").encode("latin-1")

# --- Interface ---
st.title("📅 Gestão de Reuniões")

nomes_df = load_nomes()
partes_df = load_partes()

st.subheader("Lista de Partes da Reunião")
st.dataframe(partes_df, use_container_width=True)

# Formulário para adicionar parte
st.subheader("Adicionar Nova Parte")
with st.form("add_part_form"):
    parte = st.text_input("Nome da Parte (ex.: Introdução)")
    responsavel = st.selectbox("Responsável", nomes_df[nomes_df["Visível"] == True]["Nome"].tolist())
    submitted = st.form_submit_button("Adicionar Parte")
    if submitted and parte.strip():
        novo_df = pd.DataFrame([{"Parte": parte.strip(), "Responsável": responsavel}])
        partes_df = pd.concat([partes_df, novo_df], ignore_index=True)
        save_partes(partes_df)
        st.success(f"Parte '{parte}' atribuída a {responsavel} com sucesso!")
        st.stop()

# Gestão de partes
st.subheader("Gerir Partes")
for i, row in partes_df.iterrows():
    col1, col2 = st.columns([3,1])
    col1.write(f"{row['Parte']} → {row['Responsável']}")
    if col2.button("Eliminar", key=f"delete_part_{i}"):
        partes_df = partes_df.drop(i).reset_index(drop=True)
        save_partes(partes_df)
        st.stop()

# Exportar CSV
st.download_button("📥 Exportar CSV", data=partes_df.to_csv(index=False), file_name="partes.csv", mime="text/csv")

# Exportar PDF
pdf_bytes = export_pdf(partes_df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="partes.pdf", mime="application/pdf")
