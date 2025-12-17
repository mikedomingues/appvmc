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
    """Carrega partes e tempos do CSV com validação e normalização."""
    if not os.path.exists(PARTES_FILE):
        st.warning("Faltou o ficheiro partes_reuniao.csv. Cria-o na raiz do projeto.")
        return pd.DataFrame(columns=["Secção", "Parte", "TempoMin", "TempoMax"])

    df = pd.read_csv(PARTES_FILE)

    # Validação mínima de colunas
    required_cols = {"Secção", "Parte", "TempoMin", "TempoMax"}
    if not required_cols.issubset(set(df.columns)):
        st.error(f"O CSV {PARTES_FILE} não tem as colunas corretas. Esperado: {', '.join(required_cols)}.")
        return pd.DataFrame(columns=["Secção", "Parte", "TempoMin", "TempoMax"])

    # Normalização de nomes da secção (corrigir typos comuns)
    df["Secção"] = df["Secção"].replace({
        "Empanha-se no Ministério": "Empenha-se no Ministério",
        "Empenhe-se no Ministério": "Empenha-se no Ministério",
        "Empenha-se no ministério": "Empenha-se no Ministério",
        "Empenha-se no Ministério ": "Empenha-se no Ministério",
    })

    # Garantir tipos numéricos
    df["TempoMin"] = pd.to_numeric(df["TempoMin"], errors="coerce").fillna(0).astype(int)
    df["TempoMax"] = pd.to_numeric(df["TempoMax"], errors="coerce").fillna(0).astype(int)

    return df

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
partes_cfg = load_partes()

# Lista de nomes visíveis + entrada vazia para permitir não preencher
nomes_visiveis = [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist()

# Feedback se não há partes
if partes_cfg.empty:
    st.warning("Não há partes configuradas. Verifica o ficheiro partes_reuniao.csv.")
    st.stop()

dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # Início da Reunião (sem comentários iniciais)
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

    # Empenha-se no Ministério (dinâmico via CSV)
    st.subheader("Empenha-se no Ministério")
    ministerio_partes = partes_cfg[partes_cfg["Secção"] == "Empenha-se no Ministério"]

    if ministerio_partes.empty:
        st.info("Nenhuma parte configurada para 'Empenha-se no Ministério' no CSV.")
    else:
        for _, row in ministerio_partes.iterrows():
            parte_nome = str(row["Parte"])
            tempo_min = int(row["TempoMin"])
            tempo_max = int(row["TempoMax"])
            default = tempo_min if tempo_min <= tempo_max else tempo_max

            tempo = st.number_input(
                f"{parte_nome} - Tempo ({semana})",
                min_value=tempo_min,
                max_value=tempo_max,
                value=default,
                key=f"{semana}_{parte_nome}_tempo"
            )
            # Duas designações (par) para estas partes
            resp1 = st.selectbox(f"{parte_nome} - Designado 1 ({semana})", nomes_visiveis, key=f"{semana}_{parte_nome}_1")
            resp2 = st.selectbox(f"{parte_nome} - Designado 2 ({semana})", nomes_visiveis, key=f"{semana}_{parte_nome}_2")

            dados.append({
                "Semana": semana,
                "Secção": "Empenha-se no Ministério",
                "Parte": f"{parte_nome} ({tempo} min)",
                "Responsável": f"{resp1} / {resp2}"
            })

    # Viver como Cristãos (dinâmico via CSV)
    st.subheader("Viver como Cristãos")
    viver_partes = partes_cfg[partes_cfg["Secção"] == "Viver como Cristãos"]

    if viver_partes.empty:
        st.info("Nenhuma parte configurada para 'Viver como Cristãos' no CSV.")
    else:
        for _, row in viver_partes.iterrows():
            parte_nome = str(row["Parte"])
            tempo_min = int(row["TempoMin"])
            tempo_max = int(row["TempoMax"])
            default = tempo_min if tempo_min <= tempo_max else tempo_max

            tempo = st.number_input(
                f"{parte_nome} - Tempo ({semana})",
                min_value=tempo_min,
                max_value=tempo_max,
                value=default,
                key=f"{semana}_{parte_nome}_tempo"
            )
            resp = st.selectbox(f"{parte_nome} ({semana})", nomes_visiveis, key=f"{semana}_{parte_nome}_resp")

            dados.append({
                "Semana": semana,
                "Secção": "Viver como Cristãos",
                "Parte": f"{parte_nome} ({tempo} min)",
                "Responsável": resp
            })

    # Final da Reunião (sem comentários finais)
    st.subheader("Final da Reunião")
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
