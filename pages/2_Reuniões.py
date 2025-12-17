import streamlit as st
import pandas as pd
import os
from datetime import timedelta

DB_FILE = "nomes.csv"
PARTES_FILE = "partes_reuniao.csv"

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

def load_partes():
    """Carrega partes e tempos do CSV."""
    if os.path.exists(PARTES_FILE):
        df = pd.read_csv(PARTES_FILE)
        # Normalizar nome da secção para evitar typos
        df["Secção"] = df["Secção"].replace({
            "Empanha-se no Ministério": "Empenha-se no Ministério",
            "Empenhe-se no Ministério": "Empenha-se no Ministério",
        })
        return df
    else:
        return pd.DataFrame(columns=["Secção", "Parte", "TempoMin", "TempoMax"])

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
partes_df = load_partes()

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

    comentarios = st.text_input(f"Comentários introdutórios (1 min) ({semana})", key=f"comentarios_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Comentários introdutórios 1 min", "Responsável": comentarios})

    # Tesouros da Palavra de Deus
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(f"{parte} ({semana})", nomes_visiveis, key=f"{semana}_{parte}")
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Parte": parte, "Responsável": responsavel})

    # Empenha-se no Ministério (dinâmico via CSV)
    st.subheader("Empenha-se no Ministério")
    ministerio_partes = partes_df[partes_df["Secção"] == "Empenha-se no Ministério"]

    for _, row in ministerio_partes.iterrows():
        tempo = st.number_input(
            f"{row['Parte']} - Tempo ({semana})",
            min_value=int(row["TempoMin"]),
            max_value=int(row["TempoMax"]),
            value=int(row["TempoMin"]),
            key=f"{semana}_{row['Parte']}_tempo"
        )
        resp1 = st.selectbox(f"{row['Parte']} - Designado 1 ({semana})", nomes_visiveis, key=f"{semana}_{row['Parte']}_1")
        resp2 = st.selectbox(f"{row['Parte']} - Designado 2 ({semana})", nomes_visiveis, key=f"{semana}_{row['Parte']}_2")

        dados.append({
            "Semana": semana,
            "Secção": "Empenha-se no Ministério",
            "Parte": f"{row['Parte']} ({tempo} min)",
            "Responsável": f"{resp1} / {resp2}"
        })

    # Viver como Cristãos (dinâmico via CSV)
    st.subheader("Viver como Cristãos")
    viver_partes = partes_df[partes_df["Secção"] == "Viver como Cristãos"]

    for _, row in viver_partes.iterrows():
        tempo = st.number_input(
            f"{row['Parte']} - Tempo ({semana})",
            min_value=int(row["TempoMin"]),
            max_value=int(row["TempoMax"]),
            value=int(row["TempoMin"]),
            key=f"{semana}_{row['Parte']}_tempo"
        )
        resp = st.selectbox(f"{row['Parte']} ({semana})", nomes_visiveis, key=f"{semana}_{row['Parte']}_resp")

        dados.append({
            "Semana": semana,
            "Secção": "Viver como Cristãos",
            "Parte": f"{row['Parte']} ({tempo} min)",
            "Responsável": resp
        })

    # Final da Reunião
    st.subheader("Final da Reunião")
    comentarios_finais = st.text_input(f"Comentários finais (3 min) ({semana})", key=f"comentarios_finais_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Comentários finais 3 min", "Responsável": comentarios_finais})

    oracao_final = st.selectbox(f"Oração Final ({semana})", nomes_visiveis, key=f"oracao_final_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Oração Final", "Responsável": oracao_final})

# Criar DataFrame final
partes_df_final = pd.DataFrame(dados)

# -------------------------
# Ações finais
# -------------------------
col1, col2 = st.columns(2)

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
