
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Previsão de Óbitos por Diabetes em SP",
    page_icon="🩺",
    layout="wide"
)


# ============================================================
# CAMINHOS
# ============================================================

PASTA = os.path.dirname(
    os.path.abspath(__file__)
)

ARQUIVO_SERIE = os.path.join(
    PASTA,
    "dashboard_serie_anual.csv"
)

ARQUIVO_PERFIL = os.path.join(
    PASTA,
    "dashboard_perfil_historico.csv"
)

ARQUIVO_HIST_MUN = os.path.join(
    PASTA,
    "dashboard_municipios_historico.csv"
)

ARQUIVO_PROJ_MUN = os.path.join(
    PASTA,
    "dashboard_projecoes_municipais.csv"
)

ARQUIVO_METRICAS = os.path.join(
    PASTA,
    "dashboard_metricas_modelos.csv"
)


# ============================================================
# CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_dados():

    serie = pd.read_csv(
        ARQUIVO_SERIE,
        sep=";"
    )

    perfil = pd.read_csv(
        ARQUIVO_PERFIL,
        sep=";"
    )

    historico_municipal = pd.read_csv(
        ARQUIVO_HIST_MUN,
        sep=";",
        dtype={
            "CODMUNRES": str
        }
    )

    projecoes_municipais = pd.read_csv(
        ARQUIVO_PROJ_MUN,
        sep=";",
        dtype={
            "CODMUNRES": str
        }
    )

    metricas = pd.read_csv(
        ARQUIVO_METRICAS,
        sep=";"
    )

    return (
        serie,
        perfil,
        historico_municipal,
        projecoes_municipais,
        metricas
    )


(
    serie,
    perfil,
    historico_municipal,
    projecoes_municipais,
    metricas
) = carregar_dados()

# ============================================================
# NOMES DOS MUNICÍPIOS - IBGE
# ============================================================

@st.cache_data
def carregar_municipios_ibge():

    url = (
        "https://servicodados.ibge.gov.br/api/v1/"
        "localidades/estados/SP/municipios"
    )

    try:

        dados = pd.read_json(url)

        mapa = {}

        for _, linha in dados.iterrows():

            codigo_7 = str(linha["id"])

            # Nossa base usa os 6 primeiros dígitos
            codigo_6 = codigo_7[:6]

            mapa[codigo_6] = linha["nome"]

        return mapa

    except Exception:

        return {}


mapa_municipios = carregar_municipios_ibge()

# ============================================================
# PADRONIZAÇÃO
# ============================================================

serie["ANO"] = pd.to_numeric(
    serie["ANO"],
    errors="coerce"
)

serie["OBITOS"] = pd.to_numeric(
    serie["OBITOS"],
    errors="coerce"
)

perfil["ANO"] = pd.to_numeric(
    perfil["ANO"],
    errors="coerce"
)

perfil["OBITOS"] = pd.to_numeric(
    perfil["OBITOS"],
    errors="coerce"
)

historico_municipal["ANO"] = pd.to_numeric(
    historico_municipal["ANO"],
    errors="coerce"
)

historico_municipal["OBITOS"] = pd.to_numeric(
    historico_municipal["OBITOS"],
    errors="coerce"
)

projecoes_municipais["ANO"] = pd.to_numeric(
    projecoes_municipais["ANO"],
    errors="coerce"
)

projecoes_municipais[
    "OBITOS_PREVISTOS"
] = pd.to_numeric(
    projecoes_municipais[
        "OBITOS_PREVISTOS"
    ],
    errors="coerce"
)

historico_municipal["CODMUNRES"] = (
    historico_municipal[
        "CODMUNRES"
    ]
    .astype(str)
    .str.zfill(6)
)

projecoes_municipais["CODMUNRES"] = (
    projecoes_municipais[
        "CODMUNRES"
    ]
    .astype(str)
    .str.zfill(6)
)


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🩺 Previsão de Óbitos por Diabetes Mellitus "
    "no Estado de São Paulo"
)

st.caption(
    "Dados do SIM/DATASUS — CID-10 E10 a E14"
)

st.info(
    "Os dados de 2000 a 2024 correspondem ao histórico "
    "utilizado no estudo. O ano de 2025 é apresentado "
    "separadamente como dado preliminar e não foi utilizado "
    "no treinamento final. Os valores de 2026 a 2030 "
    "correspondem às projeções do modelo selecionado."
)


# ============================================================
# ABAS
# ============================================================

aba1, aba2, aba3, aba4 = st.tabs(
    [
        "📈 Visão Geral",
        "👥 Perfil Histórico",
        "🏙️ Municípios",
        "🤖 Modelos"
    ]
)


# ============================================================
# ABA 1 - VISÃO GERAL
# ============================================================

with aba1:

    st.subheader(
        "Evolução dos óbitos e projeções"
    )

    historico = serie[
        serie["TIPO"]
        == "Histórico definitivo"
    ].copy()

    preliminar = serie[
        serie["TIPO"]
        == "2025 - dado preliminar"
    ].copy()

    projecao = serie[
        serie["TIPO"]
        == "Projeção do modelo"
    ].copy()


    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    total_2024 = historico.loc[
        historico["ANO"] == 2024,
        "OBITOS"
    ].iloc[0]

    total_2025 = preliminar[
        "OBITOS"
    ].iloc[0]

    total_2030 = projecao.loc[
        projecao["ANO"] == 2030,
        "OBITOS"
    ].iloc[0]


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Óbitos em 2024",
        f"{total_2024:,.0f}".replace(
            ",",
            "."
        )
    )

    col2.metric(
        "Prévia de 2025",
        f"{total_2025:,.0f}".replace(
            ",",
            "."
        )
    )

    col3.metric(
        "Projeção para 2030",
        f"{total_2030:,.0f}".replace(
            ",",
            "."
        )
    )


    # --------------------------------------------------------
    # GRÁFICO PRINCIPAL
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=historico["ANO"],
            y=historico["OBITOS"],
            mode="lines+markers",
            name="Histórico 2000–2024"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=preliminar["ANO"],
            y=preliminar["OBITOS"],
            mode="markers",
            marker={
                "size": 12
            },
            name="2025 — dado preliminar"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=projecao["ANO"],
            y=projecao["OBITOS"],
            mode="lines+markers",
            line={
                "dash": "dash"
            },
            name="Projeção 2026–2030"
        )
    )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Número de óbitos",
        hovermode="x unified",
        legend_title="Tipo de dado"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

    st.subheader(
        "Série histórica e projeções"
    )

    ano_inicio, ano_fim = st.slider(
        "Selecione o período",
        min_value=2000,
        max_value=2030,
        value=(
            2000,
            2030
        ),
        key="slider_serie"
    )

    tabela_serie = serie[
        serie["ANO"].between(
            ano_inicio,
            ano_fim
        )
    ].copy()

    tabela_serie["OBITOS"] = (
        tabela_serie["OBITOS"]
        .round(0)
        .astype(int)
    )

    tabela_serie = tabela_serie.rename(
        columns={
            "ANO":
                "Ano",

            "OBITOS":
                "Óbitos",

            "TIPO":
                "Tipo"
        }
    )

    st.dataframe(
        tabela_serie,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ABA 2 - PERFIL HISTÓRICO
# ============================================================

with aba2:

    st.subheader(
        "Perfil dos óbitos registrados entre 2000 e 2024"
    )

    intervalo_perfil = st.slider(
        "Período histórico",
        min_value=2000,
        max_value=2024,
        value=(
            2000,
            2024
        ),
        key="slider_perfil"
    )

    perfil_filtrado = perfil[
        perfil["ANO"].between(
            intervalo_perfil[0],
            intervalo_perfil[1]
        )
    ].copy()


    # --------------------------------------------------------
    # FAIXA ETÁRIA
    # --------------------------------------------------------

    faixa = (
        perfil_filtrado
        .groupby(
            "FAIXA_ETARIA",
            dropna=False
        )["OBITOS"]
        .sum()
        .reset_index()
        .sort_values(
            "OBITOS",
            ascending=False
        )
    )

    fig_faixa = px.bar(
        faixa,
        x="FAIXA_ETARIA",
        y="OBITOS",
        labels={
            "FAIXA_ETARIA":
                "Faixa etária",

            "OBITOS":
                "Óbitos"
        },
        title="Óbitos por faixa etária"
    )

    st.plotly_chart(
        fig_faixa,
        use_container_width=True
    )


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # SEXO
    # --------------------------------------------------------

    sexo = (
        perfil_filtrado
        .groupby(
            "SEXO_DESC",
            dropna=False
        )["OBITOS"]
        .sum()
        .reset_index()
    )

    fig_sexo = px.bar(
        sexo,
        x="SEXO_DESC",
        y="OBITOS",
        labels={
            "SEXO_DESC":
                "Sexo",

            "OBITOS":
                "Óbitos"
        },
        title="Óbitos por sexo"
    )

    col1.plotly_chart(
        fig_sexo,
        use_container_width=True
    )


    # --------------------------------------------------------
    # RAÇA/COR
    # --------------------------------------------------------

    raca = (
        perfil_filtrado
        .groupby(
            "RACACOR_DESC",
            dropna=False
        )["OBITOS"]
        .sum()
        .reset_index()
    )

    fig_raca = px.bar(
        raca,
        x="RACACOR_DESC",
        y="OBITOS",
        labels={
            "RACACOR_DESC":
                "Raça/cor",

            "OBITOS":
                "Óbitos"
        },
        title="Óbitos por raça/cor"
    )

    col2.plotly_chart(
        fig_raca,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ESCOLARIDADE
    # --------------------------------------------------------

    escolaridade = (
        perfil_filtrado
        .groupby(
            "ESCOLARIDADE_DESC",
            dropna=False
        )["OBITOS"]
        .sum()
        .reset_index()
        .sort_values(
            "OBITOS",
            ascending=False
        )
    )

    fig_esc = px.bar(
        escolaridade,
        x="ESCOLARIDADE_DESC",
        y="OBITOS",
        labels={
            "ESCOLARIDADE_DESC":
                "Escolaridade",

            "OBITOS":
                "Óbitos"
        },
        title="Óbitos por escolaridade"
    )

    st.plotly_chart(
        fig_esc,
        use_container_width=True
    )


    # --------------------------------------------------------
    # CID
    # --------------------------------------------------------

    cid = (
        perfil_filtrado
        .groupby(
            "GRUPO_CID",
            dropna=False
        )["OBITOS"]
        .sum()
        .reset_index()
    )

    fig_cid = px.bar(
        cid,
        x="GRUPO_CID",
        y="OBITOS",
        labels={
            "GRUPO_CID":
                "Grupo CID-10",

            "OBITOS":
                "Óbitos"
        },
        title="Óbitos por grupo CID-10"
    )

    st.plotly_chart(
        fig_cid,
        use_container_width=True
    )


# ============================================================
# ABA 3 - MUNICÍPIOS
# ============================================================

with aba3:

    st.subheader(
        "Análise por município"
    )

    lista_codigos = sorted(
        historico_municipal[
            "CODMUNRES"
        ].unique()
    )


    # --------------------------------------------------------
    # Nome do município + código
    # --------------------------------------------------------

    opcoes_municipios = {}

    for codigo in lista_codigos:

        nome = mapa_municipios.get(
            codigo,
            "Município"
        )

        texto = f"{nome} — {codigo}"

        opcoes_municipios[
            texto
        ] = codigo


    lista_exibicao = sorted(
        opcoes_municipios.keys()
    )


    municipio_exibicao = st.selectbox(
        "Selecione o município",
        lista_exibicao
    )


    municipio = (
        opcoes_municipios[
            municipio_exibicao
        ]
    )


    nome_municipio = (
        mapa_municipios.get(
            municipio,
            "Município não identificado"
        )
    )


    st.caption(
        f"Município selecionado: "
        f"**{nome_municipio} — {municipio}**"
    )


    # --------------------------------------------------------
    # HISTÓRICO E PROJEÇÕES DO MUNICÍPIO
    # --------------------------------------------------------

    hist_municipio = historico_municipal[
        historico_municipal[
            "CODMUNRES"
        ] == municipio
    ].copy()

    proj_municipio = projecoes_municipais[
        projecoes_municipais[
            "CODMUNRES"
        ] == municipio
    ].copy()


    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    fig_municipio = go.Figure()

    fig_municipio.add_trace(
        go.Scatter(
            x=hist_municipio["ANO"],
            y=hist_municipio["OBITOS"],
            mode="lines+markers",
            name="Histórico",
            hovertemplate=(
                "Ano: %{x}<br>"
                "Óbitos históricos: %{y:.0f}"
                "<extra></extra>"
            )
        )
    )

    fig_municipio.add_trace(
        go.Scatter(
            x=proj_municipio["ANO"],
            y=proj_municipio[
                "OBITOS_PREVISTOS"
            ],
            mode="lines+markers",
            line={
                "dash": "dash"
            },
            name="Projeção",
            hovertemplate=(
                "Ano: %{x}<br>"
                "Óbitos previstos: %{y:.0f}"
                "<extra></extra>"
            )
        )
    )

    fig_municipio.update_layout(
        title=(
            f"Histórico e projeção — "
            f"{nome_municipio}"
        ),
        xaxis_title="Ano",
        yaxis_title="Óbitos",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_municipio,
        use_container_width=True
    )


    # --------------------------------------------------------
    # PROJEÇÕES MUNICIPAIS
    # --------------------------------------------------------

    st.subheader(
        "Projeções municipais"
    )

    ano_projecao = st.selectbox(
        "Ano da projeção",
        [
            2026,
            2027,
            2028,
            2029,
            2030
        ]
    )


    ranking_municipal = (
        projecoes_municipais[
            projecoes_municipais[
                "ANO"
            ] == ano_projecao
        ]
        .sort_values(
            "OBITOS_PREVISTOS",
            ascending=False
        )
        .copy()
    )


    # --------------------------------------------------------
    # Adicionar nome do município
    # --------------------------------------------------------

    ranking_municipal[
        "MUNICIPIO"
    ] = (
        ranking_municipal[
            "CODMUNRES"
        ]
        .map(
            mapa_municipios
        )
        .fillna(
            "Município não identificado"
        )
    )


    # --------------------------------------------------------
    # Arredondar somente a exibição
    # --------------------------------------------------------

    ranking_municipal[
        "OBITOS_PREVISTOS"
    ] = (
        ranking_municipal[
            "OBITOS_PREVISTOS"
        ]
        .round(0)
        .astype(int)
    )


    ranking_municipal = (
        ranking_municipal[
            [
                "ANO",
                "MUNICIPIO",
                "CODMUNRES",
                "OBITOS_PREVISTOS"
            ]
        ]
        .rename(
            columns={
                "ANO":
                    "Ano",

                "MUNICIPIO":
                    "Município",

                "CODMUNRES":
                    "Código do município",

                "OBITOS_PREVISTOS":
                    "Óbitos previstos"
            }
        )
    )


    st.dataframe(
        ranking_municipal,
        use_container_width=True,
        hide_index=True
    )


    st.caption(
        "Os valores municipais previstos são exibidos "
        "arredondados para o número inteiro mais próximo. "
        "Os valores originais produzidos pelo modelo "
        "permanecem preservados na base de dados."
    )

# ============================================================
# ABA 4 - MODELOS
# ============================================================

with aba4:

    st.subheader(
        "Comparação dos modelos"
    )

    st.markdown(
        """
        Foram comparados dois modelos de regressão:

        - **Regressão Linear Temporal**
        - **Random Forest Regressor ajustado**

        A avaliação foi realizada em um teste temporal
        correspondente ao período de **2021 a 2024**.
        """
    )


    metricas_exibir = metricas.copy()

    metricas_exibir[
        "MAE"
    ] = metricas_exibir[
        "MAE"
    ].round(3)

    metricas_exibir[
        "RMSE"
    ] = metricas_exibir[
        "RMSE"
    ].round(3)

    metricas_exibir[
        "R2"
    ] = metricas_exibir[
        "R2"
    ].round(4)

    metricas_exibir = metricas_exibir.rename(
        columns={
            "MODELO":
                "Modelo",

            "R2":
                "R²"
        }
    )

    st.dataframe(
        metricas_exibir,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # GRÁFICO DE R²
    # --------------------------------------------------------

    fig_r2 = px.bar(
        metricas,
        x="MODELO",
        y="R2",
        labels={
            "MODELO":
                "Modelo",

            "R2":
                "R²"
        },
        title="R² no teste temporal 2021–2024",
        text_auto=".4f"
    )

    st.plotly_chart(
        fig_r2,
        use_container_width=True
    )


    # --------------------------------------------------------
    # GRÁFICO DE ERROS
    # --------------------------------------------------------

    erros = metricas.melt(
        id_vars=[
            "MODELO"
        ],
        value_vars=[
            "MAE",
            "RMSE"
        ],
        var_name="Métrica",
        value_name="Valor"
    )

    fig_erros = px.bar(
        erros,
        x="MODELO",
        y="Valor",
        color="Métrica",
        barmode="group",
        labels={
            "MODELO":
                "Modelo"
        },
        title="MAE e RMSE no teste temporal"
    )

    st.plotly_chart(
        fig_erros,
        use_container_width=True
    )


    melhor_modelo = (
        metricas
        .sort_values(
            "RMSE"
        )
        .iloc[0]
    )


    st.success(
        "Modelo selecionado para as projeções: "
        f"{melhor_modelo['MODELO']}."
    )

    st.markdown(
        """
        **Interpretação das métricas**

        **MAE:** erro absoluto médio das previsões.

        **RMSE:** penaliza mais intensamente erros de maior
        magnitude.

        **R²:** indica a proporção da variabilidade dos dados
        explicada pelo modelo. Valores mais próximos de 1
        indicam maior capacidade explicativa no conjunto
        avaliado.
        """
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Trabalho acadêmico desenvolvido com dados públicos "
    "do Sistema de Informações sobre Mortalidade (SIM/DATASUS). "
    "As projeções representam estimativas produzidas pelo "
    "modelo e não valores observados."
)
