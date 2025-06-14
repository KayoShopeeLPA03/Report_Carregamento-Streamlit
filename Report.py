import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Report Carregamento - LPA-03", 
    page_icon="⏱️",
    layout="wide"
)

st.markdown("---")
st.caption("**Desenvolvido por Kayo Soares - LPA 03**")

if st.button("🔄 Atualizar dados"):
    st.rerun()

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

    data_carregamento = df["Data Exp."].iloc[0] if "Data Exp." in df.columns else datetime.today().strftime('%d/%m/%Y')

    total_rotas = df["Gaiola"].nunique()
    rotas_pm = df[df["OpsClock"] == "PM 12:00"]["Gaiola"].nunique()
    rotas_carregadas = df[df["OK?"] == "OK"]["Gaiola"].nunique()
    rotas_nao_carregadas = df[df["OK?"] == "-"]["Gaiola"].nunique()

    total_processadas = rotas_carregadas + rotas_nao_carregadas
    percentual_carregado = (rotas_carregadas / total_processadas) * 100 if total_processadas > 0 else 0

    
    total_rotas_am = df[df["OpsClock"] <= "09:00"]["Gaiola"].nunique()
    rotas_am_carregadas = df[(df["OpsClock"] <= "09:00") & (df["OK?"] == "OK")]["Gaiola"].nunique()

    meta_opsclock = total_rotas_am * 0.98
    rotas_faltantes = max(0, int(round(meta_opsclock - rotas_am_carregadas)))
    percentual_realizado = (rotas_am_carregadas / total_rotas_am) * 100 if total_rotas_am > 0 else 0
    atingiu_meta = rotas_am_carregadas >= meta_opsclock

    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    hora_atualizacao = datetime.now().strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div style="background-color:#444;padding:10px;border-radius:8px;text-align:center;margin-bottom:15px;">
            <h5 style="color:white;margin:0;">⏰ Última atualização: <span style="color:#00c6ff;">{hora_atualizacao}</span></h5>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
        <h2 style='text-align: center;'>⏱️ Report de Carregamento - LPA-03</h2>
        <p style='text-align: center; font-size: 16px;'>📅 Carregamento referente ao dia: <b>{data_carregamento}</b></p>
    """, unsafe_allow_html=True)

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
            <div style="background-color:#000080;padding:12px 10px;border-radius:10px;text-align:center;margin-bottom:10px;">
                <h5 style="color:white;margin-bottom:6px;">🌙 Rotas PM</h5>
                <h3 style="color:white;margin:0;">{rotas_pm}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

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

    col5, col6 = st.columns(2)
with col5:
    st.markdown(
        f"**⏰ Meta 98% até 9h:** {rotas_am_carregadas} / {total_rotas_am} — **{percentual_realizado:.0f}%**"
    )
with col6:
    st.markdown(
        f"**📉 Rotas faltantes para atingir a meta:** {rotas_faltantes}"
    )

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
