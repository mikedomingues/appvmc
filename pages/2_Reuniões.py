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

    # Normalização de nomes da secção
    df["Secção"] = df["Secção"].replace({
        "Empenhe-se no Ministério": "Empenha-se no Ministério",
        "Empanha-se no Ministério": "Empenha-se no Ministério",
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

# Gerar semanas consecutivas
semanas = [(primeira_semana + timedelta(weeks=i)).strftime("%d %b") for i in range(num_semanas)]

nomes_df = load_nomes()
partes_cfg = load_partes()

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

    # Empenha-se no Ministério (flexível)
    st.subheader("Empenha-se no Ministério")
    ministerio_partes = partes_cfg[partes_cfg["Secção"] == "Empenha-se no Ministério"]

    num_ministerio = st.number_input(f"Número de partes ({semana})", min_value=1, max_value=4, value=3, key=f"num_ministerio_{semana}")
    for i in range(num_ministerio):
        parte_escolhida = st.selectbox(
            f"Parte {i+1} ({semana})",
            ministerio_partes["Parte"].unique(),
            key=f"{semana}_ministerio_parte_{i}"
        )
        row = ministerio_partes[ministerio_partes["Parte"] == parte_escolhida].iloc[0]
        tempo = st.number_input(
            f"Tempo para {parte_escolhida} ({semana})",
            min_value=int(row["TempoMin"]),
            max_value=int(row["TempoMax"]),
            value=int(row["TempoMin"]),
            key=f"{semana}_ministerio_tempo_{i}"
        )

       if parte_escolhida == "Discurso":
    tempo = 5  # tempo fixo
    resp = st.selectbox(f"{parte_escolhida} - Responsável ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_resp_{i}")
    dados.append({
        "Semana": semana,
        "Secção": "Empenha-se no Ministério",
        "Ordem": f"Parte {i+1}",
        "Parte": f"{parte_escolhida} ({tempo} min)",
        "Responsável": resp
    })

    })

            })
        else:
            resp1 = st.selectbox(f"{parte_escolhida} - Designado 1 ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_1_{i}")
            resp2 = st.selectbox(f"{parte_escolhida} - Designado 2 ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_2_{i}")
            dados.append({
                "Semana": semana,
                "Secção": "Empenha-se no Ministério",
                "Ordem": f"Parte {i+1}",
                "Parte": f"{parte_escolhida} ({tempo} min)",
                "Responsável": f"{resp1} / {resp2}"
            })

    # Viver como Cristãos (flexível)
    st.subheader("Viver como Cristãos")
    viver_partes = partes_cfg[partes_cfg["Secção"] == "Viver como Cristãos"]

    num_viver = st.number_input(f"Número de partes ({semana})", min_value=1, max_value=4, value=2, key=f"num_viver_{semana}")
    for i in range(num_viver):
        parte_escolhida = st.selectbox(
            f"Parte {i+1} ({semana})",
            viver_partes["Parte"].unique(),
            key=f"{semana}_viver_parte_{i}"
        )
        row = viver_partes[viver_partes["Parte"] == parte_escolhida].iloc[0]
        tempo = st.number_input(
            f"Tempo para {parte_escolhida} ({semana})",
            min_value=int(row["TempoMin"]),
            max_value=int(row["TempoMax"]),
            value=int(row["TempoMin"]),
            key=f"{semana}_viver_tempo_{i}"
        )
        resp = st.selectbox(f"{parte_escolhida} - Responsável ({semana})", nomes_visiveis, key=f"{semana}_{parte_escolhida}_resp_{i}")

        dados.append({
            "Semana": semana,
            "Secção": "Viver como Cristãos",
            "Ordem": f"Parte {i+1}",
            "Parte": f"{parte_escolhida} ({tempo} min)",
            "Responsável": resp
        })

    # Final da Reunião
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
