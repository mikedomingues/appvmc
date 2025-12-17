import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from fpdf import FPDF

DB_FILE = "nomes.csv"

def load_nomes():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Garantir colunas esperadas
        for col in ["Nome", "Visível"]:
            if col not in df.columns:
                df[col] = "" if col == "Nome" else True
        return df
    else:
        return pd.DataFrame(columns=["Nome", "Visível"])

def to_latin1(text):
    return str(text).encode("latin-1", "replace").decode("latin-1")

def export_pdf(df):
    # Landscape para mais espaço horizontal
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)  # sem quebras automáticas
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(270, 12, to_latin1("Designações da Reunião Vida e Ministério Cristãos"), ln=True, align="C")

    semanas_ordenadas = list(df["Semana"].unique())
    for semana in semanas_ordenadas:
        grupo_semana = df[df["Semana"] == semana]

        pdf.ln(6)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(270, 8, to_latin1(f"SEMANA - {semana}"), ln=True, align="L", fill=True)

        ordem_secoes = [
            "Início da Reunião",
            "Tesouros da Palavra de Deus",
            "Empenha-se no Ministério",
            "Viver como Cristãos",
            "Final da Reunião",
        ]

        for secao in ordem_secoes:
            grupo_secao = grupo_semana[grupo_semana["Secção"] == secao]
            if grupo_secao.empty:
                continue

            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(270, 6, to_latin1(secao), ln=True, align="L", fill=True)

            # Cabeçalho da tabela
            pdf.set_font("Arial", "B", 8)
            pdf.cell(120, 6, "Parte", 1)
            pdf.cell(150, 6, "Responsável", 1)
            pdf.ln()

            # Linhas
            pdf.set_font("Arial", "", 8)
            for _, row in grupo_secao.iterrows():
                parte = to_latin1(row["Parte"])
                responsavel = to_latin1(row["Responsável"])
                pdf.cell(120, 6, parte, 1)
                pdf.cell(150, 6, responsavel, 1)
                pdf.ln()

    return pdf.output(dest="S").encode("latin-1")
)

    # Agrupar por semana (ordem pela lista original, se possível)
    semanas_ordenadas = list(df["Semana"].unique())
    for semana in semanas_ordenadas:
        grupo_semana = df[df["Semana"] == semana]

        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(200, 200, 200)  # fundo cinza
        pdf.cell(190, 10, to_latin1(f"SEMANA - {semana}"), ln=True, align="L", fill=True)

        # Ordem de secções para consistência visual
        ordem_secoes = [
            "Início da Reunião",
            "Tesouros da Palavra de Deus",
            "Empenha-se no Ministério",
            "Viver como Cristãos",
            "Final da Reunião",
        ]

        for secao in ordem_secoes:
            grupo_secao = grupo_semana[grupo_semana["Secção"] == secao]
            if grupo_secao.empty:
                continue

            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(190, 8, to_latin1(secao), ln=True, align="L", fill=True)

            # Cabeçalho da tabela
            pdf.set_font("Arial", "B", 10)
            pdf.cell(90, 8, to_latin1("Parte"), 1)  # 90
            pdf.cell(100, 8, to_latin1("Responsável"), 1)  # 100
            pdf.ln()

            # Linhas
            pdf.set_font("Arial", "", 10)
            for _, row in grupo_secao.iterrows():
                parte = to_latin1(row["Parte"])
                responsavel = to_latin1(row["Responsável"])
                pdf.cell(90, 8, parte, 1)
                pdf.cell(100, 8, responsavel, 1)
                pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# --- Interface ---
st.title("📅 Gestão de Reuniões")

st.subheader("Definir semanas do mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

# Gerar semanas consecutivas
semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()
nomes_visiveis = [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist()

# Estrutura dinâmica
dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # Início da Reunião
    st.subheader("Início da Reunião")

    presidente = st.selectbox(
        f"Presidente ({semana})",
        nomes_visiveis,
        key=f"presidente_{semana}",
    )
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Presidente", "Responsável": presidente})

    oracao_inicial = st.selectbox(
        f"Oração Inicial ({semana})",
        nomes_visiveis,
        key=f"oracao_inicial_{semana}",
    )
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Oração Inicial", "Responsável": oracao_inicial})

    # Tesouros da Palavra de Deus
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(
            f"{parte} ({semana})",
            nomes_visiveis,
            key=f"{semana}_{parte}",
        )
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Parte": parte, "Responsável": responsavel})

    # Empenha-se no Ministério (pares)
    st.subheader("Empenha-se no Ministério")
    num_partes_min = st.number_input(
        f"Número de partes (3-4) - {semana}",
        min_value=3, max_value=4, value=3,
        key=f"ministerio_{semana}",
    )
    for i in range(num_partes_min):
        nome_parte = st.text_input(
            f"Nome da parte {i+1} ({semana})",
            f"Parte {i+1}",
            key=f"ministerio_nome_{semana}_{i}",
        )
        resp1 = st.selectbox(
            f"{nome_parte} - Designado 1 ({semana})",
            nomes_visiveis,
            key=f"ministerio_resp1_{semana}_{i}",
        )
        resp2 = st.selectbox(
            f"{nome_parte} - Designado 2 ({semana})",
            nomes_visiveis,
            key=f"ministerio_resp2_{semana}_{i}",
        )
        dados.append({
            "Semana": semana,
            "Secção": "Empenha-se no Ministério",
            "Parte": nome_parte,
            "Responsável": f"{resp1} / {resp2}",
        })

    # Viver como Cristãos (dinâmica)
    st.subheader("Viver como Cristãos")
    num_partes_viver = st.number_input(
        f"Número de partes adicionais (0-2) - {semana}",
        min_value=0, max_value=2, value=1,
        key=f"viver_{semana}",
    )
    for i in range(num_partes_viver):
        nome_parte = st.text_input(
            f"Nome da parte {i+1} ({semana})",
            f"Parte {i+1}",
            key=f"viver_nome_{semana}_{i}",
        )
        resp = st.selectbox(
            f"{nome_parte} ({semana})",
            nomes_visiveis,
            key=f"viver_resp_{semana}_{i}",
        )
        dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": nome_parte, "Responsável": resp})

    # Estudo Bíblico de Congregação (Responsável + Leitor)
    st.subheader("Estudo Bíblico de Congregação")
    responsavel_estudo = st.selectbox(
        f"Responsável ({semana})",
        nomes_visiveis,
        key=f"estudo_resp_{semana}",
    )
    leitor_estudo = st.selectbox(
        f"Leitor ({semana})",
        nomes_visiveis,
        key=f"estudo_leitor_{semana}",
    )
    dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": "Estudo Bíblico de Congregação", "Responsável": responsavel_estudo})
    dados.append({"Semana": semana, "Secção": "Viver como Cristãos", "Parte": "Leitor do Estudo Bíblico", "Responsável": leitor_estudo})

    # Final da Reunião
    st.subheader("Final da Reunião")
    num_partes_final = st.number_input(
        f"Número de partes finais (2-3) - {semana}",
        min_value=2, max_value=3, value=2,
        key=f"final_{semana}",
    )
    for i in range(num_partes_final - 1):
        nome_parte = st.text_input(
            f"Nome da parte final {i+1} ({semana})",
            f"Parte Final {i+1}",
            key=f"final_nome_{semana}_{i}",
        )
        resp = st.selectbox(
            f"{nome_parte} ({semana})",
            nomes_visiveis,
            key=f"final_resp_{semana}_{i}",
        )
        dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": nome_parte, "Responsável": resp})

    # Estudo Bíblico de Congregação (Final) — mantém visibilidade
    resp_final_estudo = st.selectbox(
        f"Estudo Bíblico de Congregação (Final) ({semana})",
        nomes_visiveis,
        key=f"final_estudo_{semana}",
    )
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Estudo Bíblico de Congregação", "Responsável": resp_final_estudo})

    # Oração Final — última parte da semana
    oracao_final = st.selectbox(
        f"Oração Final ({semana})",
        nomes_visiveis,
        key=f"oracao_final_{semana}",
    )
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Oração Final", "Responsável": oracao_final})

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
st.download_button("📄 Exportar PDF (mês inteiro)", data=pdf_bytes, file_name="partes.pdf", mime="application/pdf")
