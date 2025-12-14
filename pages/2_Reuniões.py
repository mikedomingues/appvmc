import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

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
        # Estrutura inicial baseada no modelo
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

st.title("📅 Gestão de Reuniões")

# --- Escolher primeira semana ---
st.subheader("Definir Semanas do Mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")

# Escolher se o mês tem 4 ou 5 semanas
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

# Gerar lista de semanas
semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()
partes_df = load_partes(semanas)

# --- Mostrar layout com selectboxes ---
st.subheader("Designações")
for col in partes_df.columns[1:]:  # ignora coluna "Semana"
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

# --- Guardar alterações ---
if st.button("💾 Guardar Designações"):
    save_partes(partes_df)
    st.success("Designações guardadas com sucesso!")

# Exportar PDF
pdf_bytes = export_pdf(df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="nomes.pdf", mime="application/pdf")

# --- Exportar CSV ---
st.download_button("📥 Exportar CSV", data=partes_df.to_csv(index=False), file_name="partes.csv", mime="text/csv")
