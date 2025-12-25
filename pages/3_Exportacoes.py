import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io

EXPORT_DIR = "pages/exportacoes"
os.makedirs(EXPORT_DIR, exist_ok=True)

# -------------------------
# Classe PDF para lista simples
# -------------------------
class PDFLista(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSans.ttf", uni=True)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=9)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


# -------------------------
# Classe PDF para Modelo A (mensal)
# -------------------------
class PDFModeloMensal(FPDF):
    def __init__(self, titulo="Reunião Vida e Ministério Cristãos"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = titulo
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSans.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 8, self.titulo, ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=9)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def secao_imagem(self, imagem_path):
        if os.path.exists(imagem_path):
            x = 10
            w = 190
            y = self.get_y()
            self.image(imagem_path, x=x, y=y, w=w)
            self.ln(15)
        else:
            self.ln(5)


# -------------------------
# Funções de exportação
# -------------------------
def gerar_pdf_lista(df):
    pdf = PDFLista()
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "Designações da Reunião", ln=True, align="C")
    pdf.ln(4)

    # Já não usamos "Ordem"
    col_widths = [30, 60, 70, 30]
    headers = ["Semana", "Secção", "Parte", "Responsável"]

    pdf.set_font("DejaVu", "B", 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    pdf.set_font("DejaVu", "", 9)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row.get("Semana", "")), border=1)
        pdf.cell(col_widths[1], 8, str(row.get("Secção", ""))[:30], border=1)
        pdf.cell(col_widths[2], 8, str(row.get("Parte", ""))[:60], border=1)
        pdf.cell(col_widths[3], 8, str(row.get("Responsável", ""))[:25], border=1)
        pdf.ln()

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def gerar_pdf_mensal(df, titulo="Reunião Vida e Ministério Cristãos"):
    pdf = PDFModeloMensal(titulo=titulo)
    pdf.add_page()

    # 1) Semanas únicas
    if "Semana" not in df.columns:
        semanas = []
    else:
        semanas = sorted(df["Semana"].dropna().unique().tolist())

    # 2) Mapa (semana, parte) -> responsável
    mapa = {}
    for _, row in df.iterrows():
        sem = str(row.get("Semana", "")).strip()
        parte = str(row.get("Parte", "")).strip()
        resp = str(row.get("Responsável", "")).strip()
        if sem and parte:
            mapa[(sem, parte)] = resp

    # 3) Linhas fixas do modelo
    linhas = [
        ("Início da Reunião", "Presidente"),
        ("Início da Reunião", "Oração Inicial"),
        ("Tesouros da Palavra de Deus", "Tesouros da Palavra de Deus"),
        ("Tesouros da Palavra de Deus", "Pérolas Espirituais"),
        ("Tesouros da Palavra de Deus", "Leitura da Bíblia"),
        ("Empenha-se no Ministério", "Iniciar conversas (1 min) — 1"),
        ("Empenha-se no Ministério", "Iniciar conversas (1 min) — 2"),
        ("Empenha-se no Ministério", "Iniciar conversas (1 min) — 3"),
        ("Viver como Cristãos", "Parte variável 1 (5 min)"),
        ("Viver como Cristãos", "Estudo Bíblico de Congregação (30 min)"),
        ("Viver como Cristãos", "Leitor do Estudo Bíblico"),
        ("Final da Reunião", "Oração Final"),
    ]

    # 4) Imagem de secção (podes depois adicionar mais por secção)
    pdf.secao_imagem("assets/tesouros.png")

    # 5) Tabela: colunas = semanas, linhas = partes
    pdf.set_font("DejaVu", "B", 10)
    col_desc_w = 70
    col_sem_w = (190 - col_desc_w) / max(len(semanas), 1)

    pdf.cell(col_desc_w, 8, "Parte", border=1, align="L")
    for sem in semanas:
        pdf.cell(col_sem_w, 8, sem, border=1, align="C")
    pdf.ln()

    for secao, parte_label in linhas:
        pdf.set_font("DejaVu", "B", 9)
        pdf.cell(col_desc_w, 7, f"{secao} — {parte_label}", border=1, align="L")

        pdf.set_font("DejaVu", "", 9)
        for sem in semanas:
            resp = ""
            for (s, p), r in mapa.items():
                if s == sem and parte_label.split(" — ")[0].split("(")[0].strip() in p:
                    resp = r
                    break
            pdf.cell(col_sem_w, 7, resp, border=1, align="C")
        pdf.ln()

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


# -------------------------
# Página principal Streamlit
# -------------------------
st.title("📦 Exportações e Histórico")

if not os.path.exists("partes.csv"):
    st.warning("⚠️ Ainda não existe o ficheiro partes.csv. Gera primeiro na página das reuniões.")
    st.stop()

df = pd.read_csv("partes.csv")
st.success("✔️ Ficheiro partes.csv carregado com sucesso!")

# -------------------------
# Filtros
# -------------------------
st.subheader("🔍 Filtros")

col1, col2, col3 = st.columns(3)

with col1:
    semanas = ["Todos"] + sorted(df["Semana"].dropna().unique().tolist()) if "Semana" in df.columns else ["Todos"]
    filtro_semana = st.selectbox("Semana:", semanas)

with col2:
    secoes = ["Todos"] + sorted(df["Secção"].dropna().unique().tolist()) if "Secção" in df.columns else ["Todos"]
    filtro_secao = st.selectbox("Secção:", secoes)

with col3:
    if "Responsável" in df.columns:
        responsaveis = ["Todos"] + sorted(df["Responsável"].dropna().unique().tolist())
    else:
        responsaveis = ["Todos"]
    filtro_resp = st.selectbox("Responsável:", responsaveis)

df_filtrado = df.copy()

if filtro_semana != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Semana"] == filtro_semana]

if filtro_secao != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Secção"] == filtro_secao]

if filtro_resp != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Responsável"] == filtro_resp]

st.dataframe(df_filtrado, use_container_width=True)

# -------------------------
# Exportações
# -------------------------
st.subheader("📤 Exportar")

colA, colB, colC, colD = st.columns(4)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# CSV
with colA:
    csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV", csv_bytes, file_name=f"partes_{timestamp}.csv", mime="text/csv")
    with open(f"{EXPORT_DIR}/partes_{timestamp}.csv", "wb") as f:
        f.write(csv_bytes)

# PDF lista
with colB:
    pdf_bytes = gerar_pdf_lista(df_filtrado)
    st.download_button("📄 PDF Lista", pdf_bytes, file_name=f"partes_{timestamp}.pdf", mime="application/pdf")
    with open(f"{EXPORT_DIR}/partes_{timestamp}.pdf", "wb") as f:
        f.write(pdf_bytes)

# PDF mensal (Modelo A)
with colC:
    titulo_mensal = st.text_input("Título PDF Mensal", "Reunião Vida e Ministério Cristãos")
    pdf_mensal_bytes = gerar_pdf_mensal(df, titulo=titulo_mensal)
    st.download_button("🗓️ PDF Mensal (Modelo A)", pdf_mensal_bytes, file_name=f"modelo_mensal_{timestamp}.pdf", mime="application/pdf")
    with open(f"{EXPORT_DIR}/modelo_mensal_{timestamp}.pdf", "wb") as f:
        f.write(pdf_mensal_bytes)

# Excel
with colD:
    excel_buffer = io.BytesIO()
    df_filtrado.to_excel(excel_buffer, index=False)
    st.download_button("📊 Excel", excel_buffer.getvalue(), file_name=f"partes_{timestamp}.xlsx")
    with open(f"{EXPORT_DIR}/partes_{timestamp}.xlsx", "wb") as f:
        f.write(excel_buffer.getvalue())

# -------------------------
# Histórico
# -------------------------
st.subheader("📚 Histórico de Exportações")

ficheiros = sorted(os.listdir(EXPORT_DIR), reverse=True)

for f in ficheiros:
    caminho = f"{EXPORT_DIR}/{f}"
    with open(caminho, "rb") as file:
        st.download_button(f"⬇️ {f}", file.read(), file_name=f)
