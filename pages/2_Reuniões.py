import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from fpdf import FPDF

DB_FILE = "nomes.csv"
PARTES_FILE = "partes.csv"

def load_nomes():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

def load_partes(semanas):
    if os.path.exists(PARTES_FILE):
        return pd.read_csv(PARTES_FILE)
    else:
        return pd.DataFrame({
            "Semana": semanas,
            "Presidente": ["" for _ in semanas],
            "Oração Inicial": ["" for _ in semanas],
            "Comentários introdutórios": ["" for _ in semanas],
            "Tesouros da Palavra de Deus": ["" for _ in semanas],
            "Pérolas Espirituais": ["" for _ in semanas],
            "Leitura da Bíblia": ["" for _ in semanas],
            "Parte n.º 1": ["" for _ in semanas],
            "Parte n.º 2": ["" for _ in semanas],
            "Leitor": ["" for _ in semanas],
            "Comentários finais": ["" for _ in semanas],
            "Oração Final": ["" for _ in semanas]
        })

def save_partes(df):
    df.to_csv(PARTES_FILE, index=False)

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reunião Vida e Ministério Cristãos", ln=True, align="C")

    # Cabeçalho
    colunas = list(df.columns)
    pdf.set_font("Arial", size=10)
    for col in colunas:
        pdf.cell(40, 10, col, 1, 0, "C")
    pdf.ln()

    # Linhas
    for _, row in df.iterrows():
        for col in colunas:
            pdf.cell(40, 10, str(row[col]), 1, 0)
        pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# --- Interface ---
st.title("📅 Gestão de Reuniões")

st.subheader("Definir Semanas do Mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

# Corrigir para gerar segundas-feiras consecutivas
semanas = []
data = primeira_semana
for _ in range(num_semanas):
    while data.weekday() != 0:
        data += timedelta(days=1)
    semanas.append(data.strftime("%d %b"))
    data += timedelta(weeks=1)

nomes_df = load_nomes()
partes_df = load_partes(semanas)

st.subheader("Designações")
for col in partes_df.columns[1:]:
    st.markdown(f"### {col}")
    for i, semana in enumerate(partes_df["Semana"]):
        opcoes = [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist()
        valor_atual = partes_df.at[i, col]
        index_selecionado = opcoes.index(valor_atual) if valor_atual in opcoes else 0

        partes_df.at[i, col] = st.selectbox(
            f"{col} ({semana})",
            options=opcoes,
            index=index_selecionado,
            key=f"{col}_{i}"
        )

if st.button("💾 Guardar Designações"):
    save_partes(partes_df)
    st.success("Designações guardadas com sucesso!")

# Exportar CSV
st.download_button("📥 Exportar CSV", data=partes_df.to_csv(index=False), file_name="partes.csv", mime="text/csv")

# Exportar PDF
pdf_bytes = export_pdf(partes_df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="partes.pdf", mime="application/pdf")
