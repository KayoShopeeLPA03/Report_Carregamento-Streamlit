import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

    
    st.markdown(f"""
        <h2 style='text-align: center;'>⏱️ Report de Carregamento - LPA-03</h2>
        <p style='text-align: center; font-size: 18px;'>📅 Carregamento referente ao dia: <b>{data_carregamento}</b></p>
    """, unsafe_allow_html=True)

    
    indicadores = [
        ("🧾 Total de Rotas", total_rotas, "#303031"),
        ("🌙 Rotas PM", rotas_pm, "#000080"),
        ("✅ Carregadas", rotas_carregadas, "#36B258"),
        ("❌ Não Carregadas", rotas_nao_carregadas, "#ee2d2d")
    ]

    for titulo, valor, cor in indicadores:
        st.markdown(
            f"""
            <div style="background-color:{cor};padding:20px;border-radius:10px;text-align:center;margin-bottom:15px;">
                <h3 style="color:white;font-size:20px;">{titulo}</h3>
                <h2 style="color:white;font-size:32px;">{valor}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    
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
                font=dict(size=28, color="black"),
                showarrow=False
            )]
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")