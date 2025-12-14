import streamlit as st
import pandas as pd
import os

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
        # Estrutura inicial baseada no ficheiro modelo
        return pd.DataFrame({
            "Semana": ["01 set", "08 set", "15 set", "22 set"],
            "Presidente": ["", "", "", ""],
            "Oração Inicial": ["", "", "", ""],
            "Comentários introdutórios": ["", "", "", ""],
            "Tesouros da Palavra de Deus": ["", "", "", ""],
            "Pérolas Espirituais": ["", "", "", ""],
            "Leitura da Bíblia": ["", "", "", ""],
            "Parte n.º 1": ["", "", "", ""],
            "Parte n.º 2": ["", "", "", ""],
            "Leitor": ["", "", "", ""],
            "Comentários finais": ["", "", "", ""],
            "Oração Final": ["", "", "", ""]
        })

def save_partes(df):
    df.to_csv(PARTES_FILE, index=False)

st.title("📅 Gestão de Reuniões")

nomes_df = load_nomes()
partes_df = load_partes()

# Mostrar layout com selectboxes
for col in partes_df.columns[1:]:  # ignora coluna "Semana"
    st.subheader(col)
    for i, semana in enumerate(partes_df["Semana"]):
        partes_df.at[i, col] = st.selectbox(
            f"{col} ({semana})",
            options=[""] + nomes_df[nomes_df["Visível"] == True]["Nome"].tolist(),
            index=0 if partes_df.at[i, col] == "" else nomes_df[nomes_df["Visível"] == True]["Nome"].tolist().index(partes_df.at[i, col]) + 1,
            key=f"{col}_{i}"
        )

# Guardar alterações
if st.button("💾 Guardar Designações"):
    save_partes(partes_df)
    st.success("Designações guardadas com sucesso!")

# Exportar PDF
pdf_bytes = export_pdf(df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="nomes.pdf", mime="application/pdf")

# Exportar CSV
st.download_button("📥 Exportar CSV", data=partes_df.to_csv(index=False), file_name="partes.csv", mime="text/csv")


