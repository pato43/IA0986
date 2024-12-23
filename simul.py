import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("Dashboard de Cotizaciones")

# Cargar y procesar datos
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    # Copiar el dataframe y simular datos faltantes
    df_copia = df.copy()

    # Limpieza y simulación de datos faltantes
    df_copia["Monto"] = pd.to_numeric(df_copia["Monto"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(100000)
    df_copia["Avance_Porcentaje"] = pd.to_numeric(df_copia["Avance_Porcentaje"], errors="coerce").fillna(50)
    df_copia["2020"] = pd.to_numeric(df_copia["2020"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(2000000)
    df_copia["2021"] = pd.to_numeric(df_copia["2021"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(3000000)
    df_copia["Estatus"] = df_copia["Estatus"].fillna("Desconocido")

    # Agregar semáforo
    df_copia["Semaforo"] = df_copia["Avance_Porcentaje"].apply(lambda x: "🟢 Aprobada" if x >= 75 else ("🟡 Pendiente" if x >= 50 else "🔴 Rechazada"))
    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Layout inicial con pestañas
menu = st.tabs(["Resumen General", "Tablas Detalladas", "Edición de Datos"])

# Pestaña: Resumen General
with menu[0]:
    st.header("Resumen General de Cotizaciones")

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cotizaciones", len(cotizaciones))
    col2.metric("Monto Total", f"${cotizaciones['Monto'].sum():,.2f}")
    col3.metric("Promedio de Avance", f"{cotizaciones['Avance_Porcentaje'].mean():.2f}%")

    # Gráfico de barras de ventas por año
    st.subheader("Monto Anual de Ventas")
    ventas_anuales = cotizaciones[["2020", "2021"]].sum().reset_index()
    ventas_anuales.columns = ["Año", "Monto"]

    fig_ventas = px.bar(
        ventas_anuales,
        x="Año",
        y="Monto",
        text="Monto",
        title="Monto Total de Ventas por Año",
        labels={"Monto": "Monto Total", "Año": "Año"},
        color="Año",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_ventas.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_ventas.update_layout(xaxis_title="Año", yaxis_title="Monto Total")
    st.plotly_chart(fig_ventas)

# Pestaña: Tablas Detalladas
with menu[1]:
    st.header("Tablas Detalladas")

    # Resumen por cliente
    st.subheader("Resumen por Cliente")
    tabla_cliente = cotizaciones.groupby("Cliente").agg(
        Total_Monto=("Monto", "sum"),
        Total_Cotizaciones=("Cliente", "count"),
        Promedio_Avance=("Avance_Porcentaje", "mean")
    ).reset_index()
    st.dataframe(tabla_cliente, use_container_width=True)

    # Resumen por área
    st.subheader("Resumen por Área")
    tabla_area = cotizaciones.groupby("Area").agg(
        Total_Monto=("Monto", "sum"),
        Total_Cotizaciones=("Area", "count"),
        Promedio_Avance=("Avance_Porcentaje", "mean")
    ).reset_index()
    st.dataframe(tabla_area, use_container_width=True)

# Pestaña: Edición de Datos
with menu[2]:
    st.header("Edición de Datos")

    # Selección de filtros
    cliente_filtrado = st.selectbox("Selecciona un cliente para filtrar:", ["Todos"] + cotizaciones["Cliente"].unique().tolist())
    area_filtrada = st.selectbox("Selecciona un área para filtrar:", ["Todos"] + cotizaciones["Area"].unique().tolist())

    datos_filtrados = cotizaciones.copy()
    if cliente_filtrado != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Cliente"] == cliente_filtrado]
    if area_filtrada != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Area"] == area_filtrada]

    st.dataframe(datos_filtrados, use_container_width=True)

    # Edición interactiva
    columna_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Avance_Porcentaje"])
    nuevo_valor = st.text_input("Nuevo valor para la columna seleccionada")
    if st.button("Aplicar Cambios"):
        datos_filtrados[columna_editar] = nuevo_valor
        st.success("Cambios aplicados correctamente.")
