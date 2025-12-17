import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from fpdf import FPDF

DB_FILE = "nomes.csv"

# -------------------------
# Utilitários de dados
# -------------------------
def load_nomes():
    """Carrega nomes do CSV, garantindo colunas esperadas."""
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Nome" not in df.columns:
            df["Nome"] = ""
        if "Visível" not in df.columns:
            df["Visível"] = True
        return df
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

def to_latin1(text):
    """Converte texto para latin-1 com substituição segura."""
    return str(text).encode("latin-1", "replace").decode("latin-1")

# -------------------------
# Exportação PDF (paisagem, fonte compacta, uma só página)
# -------------------------
def export_pdf(df):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(270, 8, to_latin1("Designações da Reunião Vida e Ministério Cristãos"), ln=True, align="C")

    semanas_ordenadas = list(pd.unique(df["Semana"]))
    ordem_secoes = [
        "Início da Reunião",
        "Tesouros da Palavra de Deus",
        "Empenha-se no Ministério",
        "Viver como Cristãos",
        "Final da Reunião",
    ]

    for semana in semanas_ordenadas:
        grupo_semana = df[df["Semana"] == semana]

        pdf.ln(3)
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(270, 6, to_latin1(f"SEMANA - {semana}"), ln=True, align="L", fill=True)

        for secao in ordem_secoes:
            grupo_secao = grupo_semana[grupo_semana["Secção"] == secao]
            if grupo_secao.empty:
                continue

            # 🔹 Início da Reunião → mostrar direto
            if secao == "Início da Reunião":
                presidente = grupo_secao[grupo_secao["Parte"] == "Presidente"]["Responsável"].values[0]
                oracao = grupo_secao[grupo_secao["Parte"] == "Oração Inicial"]["Responsável"].values[0]
                pdf.set_font("Arial", "", 8)
                pdf.cell(270, 5, to_latin1(f"Presidente: {presidente}"), ln=True)
                pdf.cell(270, 5, to_latin1(f"Oração Inicial: {oracao}"), ln=True)
                continue

            # 🔹 Final da Reunião → mostrar apenas Oração Final
            if secao == "Final da Reunião":
                oracao_final = grupo_secao[grupo_secao["Parte"] == "Oração Final"]["Responsável"].values[0]
                pdf.set_font("Arial", "", 8)
                pdf.cell(270, 5, to_latin1(f"Oração Final: {oracao_final}"), ln=True)
                continue

            # 🔹 Secções normais com tabela
            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(270, 5, to_latin1(secao), ln=True, align="L", fill=True)

            pdf.set_font("Arial", "B", 7)
            pdf.cell(120, 5, "Parte", 1)
            pdf.cell(150, 5, "Responsável", 1)
            pdf.ln()

            pdf.set_font("Arial", "", 7)
            for _, row in grupo_secao.iterrows():
                parte = row["Parte"]
                if parte in ["Presidente", "Oração Inicial", "Oração Final"]:
                    continue  # já tratados acima
                responsavel = row["Responsável"]
                pdf.cell(120, 5, to_latin1(parte), 1)
                pdf.cell(150, 5, to_latin1(responsavel), 1)
                pdf.ln()

    return pdf.output(dest="S").encode("latin-1")


# -------------------------
# Interface
# -------------------------
st.title("📅 Gestão de Reuniões")

st.subheader("Definir semanas do mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

# Gerar semanas consecutivas (etiquetas curtas)
semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()
# Lista de nomes visíveis + entrada vazia para permitir não preencher
nomes_visiveis = [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist()

dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # Início da Reunião
    st.subheader("Início da Reunião")
    presidente = st.selectbox(f"Presidente ({semana})", nomes_visiveis, key=f"presidente_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Presidente", "Responsável": presidente})

    oracao_inicial = st.selectbox(f"Oração Inicial ({semana})", nomes_visiveis, key=f"oracao_inicial_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Oração Inicial", "Responsável": oracao_inicial})

    # Tesouros da Palavra de Deus
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(f"{parte} ({semana})", nomes_visiveis, key=f"{semana}_{parte}")
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Parte": parte, "Responsável": responsavel})

    # Empenha-se no Ministério (pares)
    st.subheader("Empenha-se no Ministério")
    num_partes_min = st.number_input(f"Número de partes (3-4) - {semana}", min_value=3, max_value=4, value=3, key=f"ministerio_{semana}")
    for i in range(num_partes_min):
        nome_parte = st.text_input(f"Nome da parte {i+1} ({semana})", f"Parte {i+1}", key=f"ministerio_nome_{semana}_{i}")
        resp1 = st.selectbox(f"{nome_parte} - Designado 1 ({semana})", nomes_visiveis, key=f"ministerio_resp1_{semana}_{i}")
        resp2 = st.selectbox(f"{nome_parte} - Designado 2 ({semana})", nomes_visiveis, key=f"ministerio_resp2_{semana}_{i}")
        dados.append({
            "Semana": semana,
            "Secção": "Empenha-se no Ministério",
            "Parte": nome_parte,
            "Responsável": f"{resp1} / {resp2}",
        })

    # Viver como Cristãos (dinâmica)
    st.subheader("Viver como Cristãos")
    num_partes_viver = st.number_input(f"Número de partes adicionais (0-2) - {semana}", min_value=0, max_value=2, value=1, key=f"viver_{semana}")
    for i in range(num_partes_viver):
        nome_parte = st.text_input(f"Nome da parte {i+1} ({semana})", f"Parte {i+1}", key=f"viver_nome_{semana}_{i}")
        resp = st.selectbox(f"{nome_parte} ({semana})", nomes_visiveis, key=f"viver_resp_{semana}_{i}")
        dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": nome_parte, "Responsável": resp})

    # Estudo Bíblico de Congregação (Responsável + Leitor)
    st.subheader("Estudo Bíblico de Congregação")
    responsavel_estudo = st.selectbox(f"Responsável ({semana})", nomes_visiveis, key=f"estudo_resp_{semana}")
    leitor_estudo = st.selectbox(f"Leitor ({semana})", nomes_visiveis, key=f"estudo_leitor_{semana}")
    dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": "Estudo Bíblico de Congregação", "Responsável": responsavel_estudo})
    dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": "Leitor do Estudo Bíblico", "Responsável": leitor_estudo})

    # Final da Reunião
    st.subheader("Final da Reunião")
    num_partes_final = st.number_input(f"Número de partes finais (2-3) - {semana}", min_value=2, max_value=3, value=2, key=f"final_{semana}")
    for i in range(num_partes_final - 1):
        nome_parte = st.text_input(f"Nome da parte final {i+1} ({semana})", f"Parte Final {i+1}", key=f"final_nome_{semana}_{i}")
        resp = st.selectbox(f"{nome_parte} ({semana})", nomes_visiveis, key=f"final_resp_{semana}_{i}")
        dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": nome_parte, "Responsável": resp})

    # Estudo Bíblico de Congregação (Final)
    resp_final_estudo = st.selectbox(f"Estudo Bíblico de Congregação (Final) ({semana})", nomes_visiveis, key=f"final_estudo_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Estudo Bíblico de Congregação", "Responsável": resp_final_estudo})

    # Oração Final — última parte da semana
    oracao_final = st.selectbox(f"Oração Final ({semana})", nomes_visiveis, key=f"oracao_final_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Oração Final", "Responsável": oracao_final})

# Criar DataFrame final
partes_df = pd.DataFrame(dados)

# -------------------------
# Ações finais
# -------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Guardar designações em CSV"):
        partes_df.to_csv("partes.csv", index=False)
        st.success("Designações guardadas em partes.csv")

with col2:
    st.download_button(
        "📥 Exportar CSV",
        data=partes_df.to_csv(index=False),
        file_name="partes.csv",
        mime="text/csv",
    )

with col3:
    pdf_bytes = export_pdf(partes_df)
    st.download_button(
        "📄 Exportar PDF (mês numa só página)",
        data=pdf_bytes,
        file_name="partes.pdf",
        mime="application/pdf",
    )
