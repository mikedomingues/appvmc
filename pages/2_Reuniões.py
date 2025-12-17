import streamlit as st
import pandas as pd
import os
from datetime import timedelta

DB_FILE = "nomes.csv"
PARTES_FILE = "partes_reuniao.csv"

# -------------------------
# Utilitários
# -------------------------
def load_nomes():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if "Nome" not in df.columns:
            df["Nome"] = ""
        if "Visível" not in df.columns:
            df["Visível"] = True
        return df
    return pd.DataFrame(columns=["Nome", "Visível"])

def load_partes():
    if not os.path.exists(PARTES_FILE):
        st.warning("Faltou o ficheiro partes_reuniao.csv.")
        return pd.DataFrame(columns=["Secção", "Parte", "TempoMin", "TempoMax"])

    df = pd.read_csv(PARTES_FILE)

    # Normalização de nomes da secção
    df["Secção"] = df["Secção"].replace({
        "Empenhe-se no Ministério": "Empenha-se no Ministério",
        "Empenha-se no Ministério ": "Empenha-se no Ministério",
        "Viver como Cristaos": "Viver como Cristãos",
        "Viver como Cristãos": "Viver como Cristãos",
    })

    # Garantir tipos numéricos
    df["TempoMin"] = pd.to_numeric(df.get("TempoMin", 0), errors="coerce").fillna(0).astype(int)
    df["TempoMax"] = pd.to_numeric(df.get("TempoMax", 0), errors="coerce").fillna(0).astype(int)

    return df

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
nomes_visiveis = [""] + nomes_df[nomes_df["Visível"].astype(str).str.lower() == "true"]["Nome"].tolist()

dados = []

for idx, semana in enumerate(semanas, start=1):
    st.header(f"📅 Semana {idx} - {semana}")

    # -------------------------
    # Início da Reunião
    # -------------------------
    st.subheader("Início da Reunião")
    presidente = st.selectbox(f"Presidente ({semana})", nomes_visiveis, key=f"presidente_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Presidente", "Responsável": presidente})

    oracao_inicial = st.selectbox(f"Oração Inicial ({semana})", nomes_visiveis, key=f"oracao_inicial_{semana}")
    dados.append({"Semana": semana, "Secção": "Início da Reunião", "Parte": "Oração Inicial", "Responsável": oracao_inicial})

    # -------------------------
    # Tesouros da Palavra de Deus
    # -------------------------
    st.subheader("Tesouros da Palavra de Deus")
    for parte in ["Tesouros da Palavra de Deus", "Pérolas Espirituais", "Leitura da Bíblia"]:
        responsavel = st.selectbox(f"{parte} ({semana})", nomes_visiveis, key=f"{semana}_{parte}")
        dados.append({"Semana": semana, "Secção": "Tesouros da Palavra de Deus", "Parte": parte, "Responsável": responsavel})

    # -------------------------
    # Empenha-se no Ministério
    # -------------------------
    st.subheader("Empenha-se no Ministério")
    ministerio_partes = partes_cfg[partes_cfg["Secção"] == "Empenha-se no Ministério"]
    num_ministerio = st.number_input(f"Número de partes ({semana})", min_value=1, max_value=4, value=3, key=f"num_ministerio_{semana}")

    for i in range(num_ministerio):
        parte_escolhida = st.selectbox(
            f"Parte {i+1} ({semana})",
            ministerio_partes["Parte"].unique(),
            key=f"{semana}_ministerio_parte_{i}"
        )

        # Validação defensiva
        rows = ministerio_partes[ministerio_partes["Parte"] == parte_escolhida]
        if rows.empty:
            st.warning(f"A parte '{parte_escolhida}' não está configurada no CSV para o Ministério.")
            continue
        row = rows.iloc[0]

        if parte_escolhida == "Discurso":
            tempo = 5  # fixo
            resp = st.selectbox(
                f"{parte_escolhida} - Responsável ({semana})",
                nomes_visiveis,
                key=f"{semana}_{parte_escolhida}_resp_{i}"
            )
            dados.append({
                "Semana": semana,
                "Secção": "Empenha-se no Ministério",
                "Ordem": f"Parte {i+1}",
                "Parte": f"{parte_escolhida} ({tempo} min)",
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
    viver_cfg = partes_cfg[partes_cfg["Secção"] == "Viver como Cristãos"].copy()

    # Partes especiais (sem responsável)
    partes_especiais = ["Atualização Corpo Governante", "Realizações da Organização"]
    mostrar_especiais = st.checkbox(f"Ativar partes especiais ({semana})", key=f"{semana}_mostrar_especiais")

    # Lista de partes disponíveis
    todas_partes = viver_cfg["Parte"].unique().tolist()
    partes_normais = [p for p in todas_partes if p not in partes_especiais and p != "Estudo Bíblico de Congregação"]
    opcoes = partes_normais + (partes_especiais if mostrar_especiais else [])

    # Parte 1
    parte1 = st.selectbox(f"Parte 1 ({semana})", ["Nenhuma"] + opcoes, key=f"{semana}_viver_parte1")
    tempo1 = None
    if parte1 != "Nenhuma":
        row1 = viver_cfg[viver_cfg["Parte"] == parte1].iloc[0]
        tempo1 = st.number_input(
            f"Tempo para {parte1} ({semana})",
            min_value=int(row1["TempoMin"]),
            max_value=int(row1["TempoMax"]),
            value=int(row1["TempoMin"]),
            key=f"{semana}_viver_tempo1"
        )
        if parte1 in partes_especiais:
            responsavel1 = ""
        else:
            responsavel1 = st.selectbox(f"{parte1} - Responsável ({semana})", nomes_visiveis, key=f"{semana}_viver_resp1")
        dados.append({
            "Semana": semana,
            "Secção": "Viver como Cristãos",
            "Ordem": "Parte variável 1",
            "Parte": f"{parte1} ({tempo1} min)",
            "Responsável": responsavel1
        })

    # Parte 2 (só aparece se tempo1 < 15)
    if tempo1 is not None and tempo1 < 15:
        parte2 = st.selectbox(f"Parte 2 ({semana})", ["Nenhuma"] + opcoes, key=f"{semana}_viver_parte2")
        if parte2 != "Nenhuma":
            row2 = viver_cfg[viver_cfg["Parte"] == parte2].iloc[0]
            tempo2 = st.number_input(
                f"Tempo para {parte2} ({semana})",
                min_value=int(row2["TempoMin"]),
                max_value=int(row2["TempoMax"]),
                value=int(row2["TempoMin"]),
                key=f"{semana}_viver_tempo2"
            )
            if parte2 in partes_especiais:
                responsavel2 = ""
            else:
                responsavel2 = st.selectbox(f"{parte2} - Responsável ({semana})", nomes_visiveis, key=f"{semana}_viver_resp2")
            dados.append({
                "Semana": semana,
                "Secção": "Viver como Cristãos",
                "Ordem": "Parte variável 2",
                "Parte": f"{parte2} ({tempo2} min)",
                "Responsável": responsavel2
            })

    # Parte fixa 1: Estudo Bíblico
    resp_estudo = st.selectbox(f"Estudo Bíblico de Congregação ({semana})", nomes_visiveis, key=f"{semana}_estudo_biblico")
    dados.append({
        "Semana": semana,
        "Secção": "Viver como Cristãos",
        "Ordem": "Parte fixa 1",
        "Parte": "Estudo Bíblico de Congregação (30 min)",
        "Responsável": resp_estudo
    })

    # Parte fixa 2: Leitor
    resp_leitor = st.selectbox(f"Leitor do Estudo Bíblico ({semana})", nomes_visiveis, key=f"{semana}_leitor_estudo")
    dados.append({
        "Semana": semana,
        "Secção": "Viver como Cristãos",
        "Ordem": "Parte fixa 2",
        "Parte": "Leitor do Estudo Bíblico",
        "Responsável": resp_leitor
    })


    # -------------------------
    # Final da Reunião
    # -------------------------
    st.subheader("Final da Reunião")
    oracao_final = st.selectbox(f"Oração Final ({semana})", nomes_visiveis, key=f"oracao_final_{semana}")
    dados.append({"Semana": semana, "Secção": "Final da Reunião", "Parte": "Oração Final", "Responsável": oracao_final})

# -------------------------
# Exportação
# -------------------------
partes_df_final = pd.DataFrame(dados)

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
