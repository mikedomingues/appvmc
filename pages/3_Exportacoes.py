import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io

EXPORT_DIR = "pages/exportacoes"

# ---------------------------------------------------------
# Garantir que a pasta de exportações existe
# ---------------------------------------------------------
os.makedirs(EXPORT_DIR, exist_ok=True)

# ---------------------------------------------------------
# Função para gerar PDF normal
# ---------------------------------------------------------
def gerar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Designações da Reunião", ln=True, align="C")
    pdf.ln(5)

    col_widths = [30, 45, 35, 70, 30]
    headers = ["Semana", "Secção", "Ordem", "Parte", "Responsável"]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["Semana"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["Secção"]), border=1)
        pdf.cell(col_widths[2], 8, str(row["Ordem"]), border=1)
        pdf.cell(col_widths[3], 8, str(row["Parte"])[:65], border=1)
        pdf.cell(col_widths[4], 8, str(row["Responsável"]), border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------------
# Função para gerar PDF versão limpa (para imprimir)
# ---------------------------------------------------------
def gerar_pdf_limpo(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Designações — Versão para Impressão", ln=True, align="C")
    pdf.ln(10)

    for _, row in df.iterrows():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"{row['Semana']} — {row['Secção']}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, f"{row['Ordem']}: {row['Parte']}")
        pdf.cell(0, 6, f"Responsável: {row['Responsável']}", ln=True)
        pdf.ln(3)

    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------------
# Página principal
# ---------------------------------------------------------
st.title("📦 Exportações e Histórico")

# ---------------------------------------------------------
# Carregar partes.csv
# ---------------------------------------------------------
if not os.path.exists("partes.csv"):
    st.warning("⚠️ Ainda não existe o ficheiro partes.csv. Gera primeiro na página das reuniões.")
    st.stop()

df = pd.read_csv("partes.csv")

st.success("✔️ Ficheiro partes.csv carregado com sucesso!")

# ---------------------------------------------------------
# Filtros
# ---------------------------------------------------------
st.subheader("🔍 Filtros")

col1, col2, col3 = st.columns(3)

with col1:
    semanas = ["Todos"] + sorted(df["Semana"].unique().tolist())
    filtro_semana = st.selectbox("Semana:", semanas)

with col2:
    secoes = ["Todos"] + sorted(df["Secção"].unique().tolist())
    filtro_secao = st.selectbox("Secção:", secoes)

with col3:
    responsaveis = ["Todos"] + sorted(df["Responsável"].unique().tolist())
    filtro_resp = st.selectbox("Responsável:", responsaveis)

df_filtrado = df.copy()

if filtro_semana != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Semana"] == filtro_semana]

if filtro_secao != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Secção"] == filtro_secao]

if filtro_resp != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Responsável"] == filtro_resp]

st.dataframe(df_filtrado, use_container_width=True)

# ---------------------------------------------------------
# Exportações
# ---------------------------------------------------------
st.subheader("📤 Exportar")

colA, colB, colC, colD = st.columns(4)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# CSV
with colA:
    csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV", csv_bytes, file_name=f"partes_{timestamp}.csv", mime="text/csv")

    with open(f"{EXPORT_DIR}/partes_{timestamp}.csv", "wb") as f:
        f.write(csv_bytes)

# PDF normal
with colB:
    pdf_bytes = gerar_pdf(df_filtrado)
    st.download_button("📄 PDF", pdf_bytes, file_name=f"partes_{timestamp}.pdf", mime="application/pdf")

    with open(f"{EXPORT_DIR}/partes_{timestamp}.pdf", "wb") as f:
        f.write(pdf_bytes)

# PDF limpo
with colC:
    pdf_limpo = gerar_pdf_limpo(df_filtrado)
    st.download_button("🖨️ PDF Limpo", pdf_limpo, file_name=f"partes_limpo_{timestamp}.pdf", mime="application/pdf")

    with open(f"{EXPORT_DIR}/partes_limpo_{timestamp}.pdf", "wb") as f:
        f.write(pdf_limpo)

# Excel
with colD:
    excel_buffer = io.BytesIO()
    df_filtrado.to_excel(excel_buffer, index=False)
    st.download_button("📊 Excel", excel_buffer.getvalue(), file_name=f"partes_{timestamp}.xlsx")

    with open(f"{EXPORT_DIR}/partes_{timestamp}.xlsx", "wb") as f:
        f.write(excel_buffer.getvalue())

# ---------------------------------------------------------
# Preview do PDF
# ---------------------------------------------------------
st.subheader("👀 Pré-visualização do PDF")

st.pdf(pdf_bytes)

# ---------------------------------------------------------
# Histórico
# ---------------------------------------------------------
st.subheader("📚 Histórico de Exportações")

ficheiros = sorted(os.listdir(EXPORT_DIR), reverse=True)

for f in ficheiros:
    caminho = f"{EXPORT_DIR}/{f}"
    with open(caminho, "rb") as file:
        st.download_button(f"⬇️ {f}", file.read(), file_name=f)

