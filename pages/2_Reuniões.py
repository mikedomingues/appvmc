import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from fpdf import FPDF

DB_FILE = "nomes.csv"

def load_nomes():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

def to_latin1(text):
    return str(text).encode("latin-1", "replace").decode("latin-1")

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Reunião Vida e Ministério Cristãos", ln=True, align="C")

    # Agrupar por secção
    for secao, grupo in df.groupby("Secção"):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, to_latin1(secao), ln=True, align="L")

        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 8, "Semana", 1)
        pdf.cell(80, 8, "Parte", 1)
        pdf.cell(70, 8, "Responsável", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        for _, row in grupo.iterrows():
            pdf.cell(40, 8, to_latin1(row["Semana"]), 1)
            pdf.cell(80, 8, to_latin1(row["Parte"]), 1)
            pdf.cell(70, 8, to_latin1(row["Responsável"]), 1)
            pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# --- Interface ---
st.title("📅 Gestão de Reuniões")

st.subheader("Definir Semanas do Mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

# Gerar semanas consecutivas
semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()

# Estrutura dinâmica
dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # Presidente da reunião
    st.subheader("Presidente da Reunião")
    presidente = st.selectbox(f"Presidente ({semana})",
                              [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                              key=f"presidente_{semana}")
    dados.append({"Semana": semana, "Secção": "Presidente da Reunião", "Parte": "Presidente", "Responsável": presidente})

    # Secção Tesouros da Palavra de Deus (fixa)
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(f"{parte} ({semana})",
                                   [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                                   key=f"{semana}_{parte}")
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Parte": parte, "Responsável": responsavel})

    # Secção Empenha-se no Ministério (pares)
    st.subheader("Empenha-se no Ministério")
    num_partes_min = st.number_input(f"Número de partes (3-4) - {semana}", min_value=3, max_value=4, value=3, key=f"ministerio_{semana}")
    for i in range(num_partes_min):
        nome_parte = st.text_input(f"Nome da parte {i+1} ({semana})", f"Parte {i+1}", key=f"ministerio_nome_{semana}_{i}")
        resp1 = st.selectbox(f"{nome_parte} - Designado 1 ({semana})",
                             [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                             key=f"ministerio_resp1_{semana}_{i}")
        resp2 = st.selectbox(f"{nome_parte} - Designado 2 ({semana})",
                             [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                             key=f"ministerio_resp2_{semana}_{i}")
        dados.append({"Semana": semana, "Secção": "Empenha-se no Ministério", "Parte": nome_parte, "Responsável": f"{resp1} / {resp2}"})

    # Secção Viver como Cristãos (dinâmica + fixa)
    st.subheader("Viver como Cristãos")
    num_partes_viver = st.number_input(f"Número de partes adicionais (0-2) - {semana}", min_value=0, max_value=2, value=1, key=f"viver_{semana}")
    for i in range(num_partes_viver):
        nome_parte = st.text_input(f"Nome da parte {i+1} ({semana})", f"Parte {i+1}", key=f"viver_nome_{semana}_{i}")
        resp = st.selectbox(f"{nome_parte} ({semana})",
                            [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                            key=f"viver_resp_{semana}_{i}")
        dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": nome_parte, "Responsável": resp})

    # Parte fixa: Estudo Bíblico de Congregação
    resp = st.selectbox(f"Estudo Bíblico de Congregação ({semana})",
                        [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                        key=f"estudo_{semana}")
    dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": "Estudo Bíblico de Congregação", "Responsável": resp})

    # Secção Final da Reunião
    st.subheader("Final da Reunião")
    num_partes_final = st.number_input(f"Número de partes finais (2-3) - {semana}", min_value=2, max_value=3, value=2, key=f"final_{semana}")
    for i in range(num_partes_final-1):
        nome_parte = st.text_input(f"Nome da parte final {i+1} ({semana})", f"Parte Final {i+1}", key=f"final_nome_{semana}_{i}")
        resp = st.selectbox(f"{nome_parte} ({semana})",
                            [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                            key=f"final_resp_{semana}_{i}")
        dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": nome_parte, "Responsável": resp})

    # Última parte fixa: Estudo Bíblico de Congregação
    resp = st.selectbox(f"Estudo Bíblico de Congregação (Final) ({semana})",
                        [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist(),
                        key=f"final_estudo_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Estudo Bíblico de Congregação", "Responsável": resp})

# Criar DataFrame final
partes_df = pd.DataFrame(dados)

# Guardar CSV
if st.button("💾 Guardar Designações"):
    partes_df.to_csv("partes.csv", index=False)
    st.success("Designações guardadas com sucesso!")

# Exportar CSV
st.download_button("📥 Exportar CSV", data=partes_df.to_csv(index=False), file_name="partes.csv", mime="text/csv")

# Exportar PDF
pdf_bytes = export_pdf(partes_df)
st.download_button("📄 Exportar PDF", data=pdf_bytes, file_name="partes.pdf", mime="application/pdf")
