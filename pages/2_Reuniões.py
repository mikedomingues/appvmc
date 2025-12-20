import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from fpdf import FPDF

DB_FILE = "nomes.csv"
PARTES_FILE = "partes_reuniao.csv"

# -------------------------
# Leitura de dados
# -------------------------
def load_nomes():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Nome" not in df.columns:
            df["Nome"] = ""
        if "Visível" not in df.columns:
            df["Visível"] = True
        df["Visível"] = df["Visível"].astype(str).str.lower().isin(["true", "1", "sim", "yes"])
        return df
    return pd.DataFrame(columns=["Nome", "Visível"])

def load_partes():
    if not os.path.exists(PARTES_FILE):
        st.warning("Faltou o ficheiro partes_reuniao.csv.")
        return pd.DataFrame(columns=["Secção", "Parte", "TempoMin", "TempoMax"])

    df = pd.read_csv(PARTES_FILE)
    df["Secção"] = df["Secção"].astype(str).str.strip().replace({
        "Empenhe-se no Ministério": "Empenha-se no Ministério",
        "Empenha-se no Ministério ": "Empenha-se no Ministério",
        "Viver como Cristaos": "Viver como Cristãos",
        "Viver como Cristãos ": "Viver como Cristãos",
    })
    df["TempoMin"] = pd.to_numeric(df.get("TempoMin", 0), errors="coerce").fillna(0).astype(int)
    df["TempoMax"] = pd.to_numeric(df.get("TempoMax", 0), errors="coerce").fillna(0).astype(int)
    return df

def nomes_visiveis_list(nomes_df):
    return [""] + nomes_df[nomes_df["Visível"]]["Nome"].tolist()

# -------------------------
# Exportação PDF
# -------------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Designações da Reunião", ln=True, align="C")
    pdf.ln(5)

    col_widths = [30, 45, 35, 70, 30]
    headers = ["Semana", "Secção", "Ordem", "Parte", "Responsável"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row.get("Semana", ""))[:30], border=1)
        pdf.cell(col_widths[1], 8, str(row.get("Secção", ""))[:40], border=1)
        pdf.cell(col_widths[2], 8, str(row.get("Ordem", ""))[:30], border=1)
        pdf.cell(col_widths[3], 8, str(row.get("Parte", ""))[:65], border=1)
        pdf.cell(col_widths[4], 8, str(row.get("Responsável", ""))[:28], border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# -------------------------
# App
# -------------------------
st.title("📅 Gestão de Reuniões")

st.subheader("Definir semanas do mês")
primeira_semana = st.date_input("Escolhe a primeira semana do mês")
num_semanas = st.radio("Número de semanas:", [4, 5], index=0)

semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()
partes_cfg = load_partes()
nomes_visiveis = nomes_visiveis_list(nomes_df)

dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # Início da Reunião
    st.subheader("Início da Reunião")
    presidente = st.selectbox(f"Presidente ({semana})", nomes_visiveis, key=f"presidente_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Ordem": "Abertura", "Parte": "Presidente", "Responsável": presidente})

    oracao_inicial = st.selectbox(f"Oração Inicial ({semana})", nomes_visiveis, key=f"oracao_inicial_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Ordem": "Abertura", "Parte": "Oração Inicial", "Responsável": oracao_inicial})

    # Tesouros da Palavra de Deus
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(f"{parte} ({semana})", nomes_visiveis, key=f"{semana}_{parte}")
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Ordem": "Sequência", "Parte": parte, "Responsável": responsavel})

    # Empenha-se no Ministério
    st.subheader("Empenha-se no Ministério")
    ministerio_cfg = partes_cfg[partes_cfg["Secção"] == "Empenha-se no Ministério"].copy()

    # Se existir Discurso no CSV, força 5/5 por consistência
    if "Discurso" in ministerio_cfg["Parte"].unique():
        ministerio_cfg.loc[ministerio_cfg["Parte"] == "Discurso", ["TempoMin", "TempoMax"]] = [5, 5]

    num_ministerio = st.number_input(f"Número de partes ({semana})", min_value=1, max_value=4, value=3, key=f"num_ministerio_{semana}")

    for i in range(num_ministerio):
        parte_escolhida = st.selectbox(
            f"Parte {i+1} ({semana})",
            ministerio_cfg["Parte"].unique(),
            key=f"{semana}_ministerio_parte_{i}"
        )

        rows = ministerio_cfg[ministerio_cfg["Parte"] == parte_escolhida]
        if rows.empty:
            st.warning(f"A parte '{parte_escolhida}' não está configurada no CSV para o Ministério.")
            continue
        row = rows.iloc[0]

        if parte_escolhida == "Discurso":
            resp = st.selectbox(f"{parte_escolhida} - Responsável ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_resp_{i}")
            dados.append({
                "Semana": semana,
                "Secção": "Empenha-se no Ministério",
                "Ordem": f"Parte {i+1}",
                "Parte": "Discurso (5 min)",
                "Responsável": resp
            })
        else:
            tempo = st.number_input(
                f"Tempo para {parte_escolhida} ({semana})",
                min_value=int(row["TempoMin"]),
                max_value=int(row["TempoMax"]),
                value=int(row["TempoMin"]),
                key=f"{semana}_ministerio_tempo_{i}"
            )
            resp1 = st.selectbox(f"{parte_escolhida} - Designado 1 ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_1_{i}")
            resp2 = st.selectbox(f"{parte_escolhida} - Designado 2 ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_2_{i}")
            dados.append({
                "Semana": semana,
                "Secção": "Empenha-se no Ministério",
                "Ordem": f"Parte {i+1}",
                "Parte": f"{parte_escolhida} ({tempo} min)",
                "Responsável": f"{resp1} / {resp2}"
            })

# -------------------------
# Viver como Cristãos
# -------------------------
st.subheader("Viver como Cristãos")

# Quantas partes variáveis o utilizador quer?
num_partes_vc = st.number_input(
    f"Número de partes variáveis ({semana})",
    min_value=1,
    max_value=3,
    value=1,
    step=1,
    key=f"{semana}_num_vc"
)

# Criar as partes variáveis dinamicamente
for i in range(num_partes_vc):
    tempo = st.number_input(
        f"Tempo da Parte variável {i+1} ({semana})",
        min_value=5,
        max_value=15,
        value=5,
        key=f"{semana}_viver_tempo_{i}"
    )

    resp = st.selectbox(
        f"Parte variável {i+1} - Designado ({semana})",
        nomes_visiveis,
        key=f"{semana}_viver_resp_{i}"
    )

    dados.append({
        "Semana": semana,
        "Secção": "Viver como Cristãos",
        "Ordem": f"Parte variável {i+1}",
        "Parte": f"Parte variável {i+1} ({tempo} min)",
        "Responsável": resp
    })

# -------------------------
# Parte fixa 1 — Estudo Bíblico
# -------------------------
resp_estudo = st.selectbox(
    f"Estudo Bíblico de Congregação ({semana})",
    nomes_visiveis,
    key=f"{semana}_estudo_biblico"
)
dados.append({
    "Semana": semana,
    "Secção": "Viver como Cristãos",
    "Ordem": "Parte fixa 1",
    "Parte": "Estudo Bíblico de Congregação (30 min)",
    "Responsável": resp_estudo
})

# -------------------------
# Parte fixa 2 — Leitor
# -------------------------
resp_leitor = st.selectbox(
    f"Leitor do Estudo Bíblico ({semana})",
    nomes_visiveis,
    key=f"{semana}_leitor_estudo"
)
dados.append({
    "Semana": semana,
    "Secção": "Viver como Cristãos",
    "Ordem": "Parte fixa 2",
    "Parte": "Leitor do Estudo Bíblico",
    "Responsável": resp_leitor
})


    # Final da Reunião
    st.subheader("Final da Reunião")
    oracao_final = st.selectbox(f"Oração Final ({semana})", nomes_visiveis, key=f"oracao_final_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Ordem": "Encerramento", "Parte": "Oração Final", "Responsável": oracao_final})

# -------------------------
# Exportação (CSV e PDF)
# -------------------------
partes_df_final = pd.DataFrame(dados)

st.subheader("Exportação")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Guardar designações em CSV"):
        partes_df_final.to_csv("partes.csv", index=False)
        st.success("Designações guardadas em partes.csv")

with col2:
    st.download_button(
        "📥 Exportar CSV",
        data=partes_df_final.to_csv(index=False),
        file_name="partes.csv",
        mime="text/csv",
    )

with col3:
    pdf_bytes = export_pdf(partes_df_final)
    st.download_button(
        "📄 Exportar PDF",
        data=pdf_bytes,
        file_name="partes.pdf",
        mime="application/pdf",
    )
