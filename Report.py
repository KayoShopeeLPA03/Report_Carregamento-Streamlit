import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# Configuração da página
st.set_page_config(
    page_title="Report Carregamento - LPA-03", 
    page_icon="⏱️",
    layout="wide"
)

# Estilo customizado do botão
st.markdown("""
    <style>
        div.stButton > button:first-child {
            background-color: #1f77b4;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 12px;
            padding: 10px 20px;
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #105d90;
            transform: scale(1.02);
        }
    </style>
""", unsafe_allow_html=True)

# Botão de atualização
if st.button("🔄 Atualizar dados"):
    st.rerun()

# Seletor: Geral / AM / PM
tipo_carregamento = st.radio(
    "Escolha o tipo de carregamento:",
    options=["Geral", "Carregamento AM", "Carregamento PM"],
    horizontal=True
)

st.markdown("---")
st.caption("**Desenvolvido por Kayo Soares - LPA 03**")

# Autenticação com Google Sheets
file_name = "teste-motoristas-4f5250c96818.json"
Scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

try:
    credencial = ServiceAccountCredentials.from_json_keyfile_name(
        filename=file_name,
        scopes=Scopes
    )
    gc = gspread.authorize(credencial)

    planilha = gc.open("PROGRAMAÇÃO FROTA - Belem - LPA-02")
    aba = planilha.worksheet("Programação")

    dados = aba.get_all_values()[2:]
    df = pd.DataFrame(dados[1:], columns=dados[0])

    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    data_carregamento = df["Data Exp."].iloc[0] if "Data Exp." in df.columns and not df["Data Exp."].isnull().all() else datetime.today().strftime('%d/%m/%Y')

    # Filtro de carregamento
    if tipo_carregamento == "Carregamento AM":
        df_filtrado = df[df["OpsClock"] == "CARREG. AM"]
    elif tipo_carregamento == "Carregamento PM":
        df_filtrado = df[df["OpsClock"] == "CARREG. PM"]
    else:
        df_filtrado = df.copy()

    # KPIs
    total_rotas = df_filtrado["Gaiola"].nunique()
    rotas_carregadas = df_filtrado[df_filtrado["OK?"] == "OK"]["Gaiola"].nunique()
    rotas_nao_carregadas = df_filtrado[df_filtrado["OK?"] == "-"]["Gaiola"].nunique()

    # 📦 Total de peças expedidas apenas das rotas carregadas
    if "Qtd Pct" in df_filtrado.columns:
        df_filtrado["Qtd Pct"] = pd.to_numeric(df_filtrado["Qtd Pct"], errors="coerce").fillna(0)
        total_pecas = int(df_filtrado[df_filtrado["OK?"] == "OK"]["Qtd Pct"].sum())
    else:
        total_pecas = 0

    total_processadas = rotas_carregadas + rotas_nao_carregadas
    percentual_carregado = (rotas_carregadas / total_processadas) * 100 if total_processadas > 0 else 0

    meta_95_qtd = round(total_rotas * 0.95)
    percentual_realizado_total = (rotas_carregadas / total_rotas) * 100 if total_rotas > 0 else 0
    percentual_progresso_meta = (rotas_carregadas / meta_95_qtd) * 100 if meta_95_qtd > 0 else 0
    percentual_progresso_meta = min(percentual_progresso_meta, 100)
    rotas_faltando_para_meta = max(0, meta_95_qtd - rotas_carregadas)

    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    hora_atualizacao = datetime.now(fuso_brasil).strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div style="background-color:#444;padding:10px;border-radius:8px;text-align:center;margin-bottom:15px;">
            <h5 style="color:white;margin:0;">⏰ Última atualização: <span style="color:#00c6ff;">{hora_atualizacao}</span></h5>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Título
    st.markdown(f"""
        <h2 style='text-align: center;'>⏱️ Report de Carregamento - LPA-03</h2>
        <p style='text-align: center; font-size: 16px;'>🗓️ Carregamento referente ao dia: <b>{data_carregamento}</b> — <b>{tipo_carregamento}</b></p>
    """, unsafe_allow_html=True)

    # KPIs superiores
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="background-color:#303031;padding:12px 10px;border-radius:10px;text-align:center;margin-bottom:10px;">
                <h5 style="color:white;margin-bottom:6px;">🧾 Total de Rotas</h5>
                <h3 style="color:white;margin:0;">{total_rotas}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color:#296898;padding:12px 10px;border-radius:10px;text-align:center;margin-bottom:10px;">
                <h5 style="color:white;margin-bottom:6px;">📦 Pacotes Expedidos</h5>
                <h3 style="color:white;margin:0;">{total_pecas:,}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Carregadas e Não Carregadas
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            f"""
            <div style="background-color:#36B258;padding:12px 10px;border-radius:10px;text-align:center;margin-bottom:10px;">
                <h5 style="color:white;margin-bottom:6px;">✅ Carregadas</h5>
                <h3 style="color:white;margin:0;">{rotas_carregadas}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div style="background-color:#ee2d2d;padding:12px 10px;border-radius:10px;text-align:center;margin-bottom:10px;">
                <h5 style="color:white;margin-bottom:6px;">❌ Não Carregadas</h5>
                <h3 style="color:white;margin:0;">{rotas_nao_carregadas}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Barras de progresso
    col5, col6 = st.columns(2)

    with col5:
        st.markdown(
            f"<b>⏱️ Progresso geral (rotas carregadas vs. total):</b> {rotas_carregadas} / {total_rotas} — <b>{percentual_realizado_total:.2f}%</b>",
            unsafe_allow_html=True
        )
        st.markdown(f"""
            <div style="background-color: #1e1e1e; border-radius: 12px; height: 26px; width: 100%; border: 1px solid #333;">
                <div style="
                    background-color: #36B258;
                    width: {percentual_realizado_total:.2f}%;
                    height: 100%;
                    border-radius: 12px;
                    text-align: center;
                    line-height: 26px;
                    color: white;
                    font-weight: 600;
                    font-size: 15px;
                ">{percentual_realizado_total:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(
            f"<b>📉 Progresso até atingir a meta de 95% ({meta_95_qtd} rotas):</b> {percentual_progresso_meta:.2f}%<br><b>🚚 Rotas faltando:</b> {rotas_faltando_para_meta}",
            unsafe_allow_html=True
        )
        st.markdown(f"""
            <div style="background-color: #1e1e1e; border-radius: 12px; height: 26px; width: 100%; border: 1px solid #333;">
                <div style="
                    background-color: #ee2d2d;
                    width: {percentual_progresso_meta:.2f}%;
                    height: 100%;
                    border-radius: 12px;
                    text-align: center;
                    line-height: 26px;
                    color: white;
                    font-weight: 600;
                    font-size: 15px;
                ">{percentual_progresso_meta:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico pizza
    with st.expander("📈 Ver gráfico de status de carregamento"):
        fig = go.Figure(data=[go.Pie(
            labels=["Carregadas", "Não Carregadas"],
            values=[rotas_carregadas, rotas_nao_carregadas],
            hole=0.4,
            marker=dict(colors=["#28a745", "#dc3545"]),
            textinfo="label+percent",
            insidetextorientation="radial",
            textfont=dict(size=16)
        )])

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=14)
            ),
            margin=dict(t=20, b=80, l=0, r=0),
            annotations=[dict(
                text=f"{percentual_carregado:.1f}%",
                x=0.5, y=0.5,
                font=dict(size=24, color="white"),
                showarrow=False
            )]
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

