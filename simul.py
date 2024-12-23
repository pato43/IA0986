import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Carga de datos desde un archivo alojado en GitHub
@st.cache_data
def load_data():
    url = "https://github.com/pato43/IA0986/blob/main/tablas%20ordenadas%20.xlsx"
    data = pd.read_excel(url)
    return data

data = load_data()

# Layout general del dashboard
st.set_page_config(page_title="Dashboard de Cotizaciones", layout="wide")
st.title("Dashboard de Cotizaciones y Pronósticos")

# Sidebar
st.sidebar.header("Opciones de Filtrado")

# Filtrado de datos
clientes = st.sidebar.multiselect(
    "Selecciona Cliente(s)", options=data["CLIENTE"].unique(), default=data["CLIENTE"].unique()
)
clasificaciones = st.sidebar.multiselect(
    "Selecciona Clasificación(es)", options=data["CLASIFICACION"].dropna().unique(), default=data["CLASIFICACION"].unique()
)

fecha_inicio = st.sidebar.date_input(
    "Fecha de inicio mínima", value=pd.to_datetime(data["FECHA INICIO"].min())
)

fecha_fin = st.sidebar.date_input(
    "Fecha de inicio máxima", value=pd.to_datetime(data["FECHA INICIO"].max())
)

filtered_data = data[
    (data["CLIENTE"].isin(clientes)) &
    (data["CLASIFICACION"].isin(clasificaciones)) &
    (pd.to_datetime(data["FECHA INICIO"]) >= pd.to_datetime(fecha_inicio)) &
    (pd.to_datetime(data["FECHA INICIO"]) <= pd.to_datetime(fecha_fin))
]

# Sección 1: Resumen general
st.markdown("## Resumen General")

col1, col2, col3 = st.columns(3)
col1.metric("Monto Total Cotizado", f"${filtered_data['MONTO'].sum():,.2f}")
col2.metric("Proyectos Totales", len(filtered_data))
col3.metric("Duración Promedio (días)", f"{filtered_data['DIAS'].mean():.1f}")

# Sección 2: Pronóstico Mensual
st.markdown("## Pronóstico Mensual")

pronostico_mensual = (
    filtered_data.groupby(filtered_data["FECHA INICIO"].dt.to_period("M")).sum()["MONTO"].reset_index()
)
pronostico_mensual["FECHA INICIO"] = pronostico_mensual["FECHA INICIO"].dt.to_timestamp()

fig_pronostico_mensual = px.line(
    pronostico_mensual,
    x="FECHA INICIO",
    y="MONTO",
    title="Pronóstico Mensual con Suavización Exponencial",
    labels={"MONTO": "Monto (MXN)", "FECHA INICIO": "Fecha"},
    markers=True
)

st.plotly_chart(fig_pronostico_mensual, use_container_width=True)

# Sección 3: Análisis por Clasificación
st.markdown("## Análisis por Clasificación")

clasificacion_data = (
    filtered_data.groupby("CLASIFICACION")["MONTO"].sum().reset_index()
    .sort_values(by="MONTO", ascending=False)
)

fig_clasificacion = px.bar(
    clasificacion_data,
    x="CLASIFICACION",
    y="MONTO",
    title="Montos Totales por Clasificación",
    labels={"MONTO": "Monto (MXN)", "CLASIFICACION": "Clasificación"},
    color="CLASIFICACION",
    text_auto=True
)

st.plotly_chart(fig_clasificacion, use_container_width=True)

# Sección 4: Control de colores para estados
st.markdown("## Control de Estados por Progreso")

estado_colores = filtered_data.copy()

estado_colores["Estado"] = np.where(
    estado_colores["ESTATUS"] == "Completado", "Verde", np.where(
        estado_colores["ESTATUS"] == "En Proceso", "Amarillo", "Rojo"
    )
)

fig_estado_colores = px.histogram(
    estado_colores,
    x="Estado",
    title="Distribución de Estados por Color",
    color="Estado",
    color_discrete_map={"Verde": "green", "Amarillo": "yellow", "Rojo": "red"}
)

st.plotly_chart(fig_estado_colores, use_container_width=True)
# Sección 5: Pronóstico Anual
st.markdown("## Pronóstico Anual con Suavización Exponencial")

def suavizacion_exponencial(data, alpha):
    pronostico = [data[0]]
    for n in range(1, len(data)):
        pronostico.append(alpha * data[n] + (1 - alpha) * pronostico[n-1])
    return pronostico

ventas_anuales = (
    filtered_data.groupby(filtered_data["FECHA INICIO"].dt.year).sum()["MONTO"].reset_index()
)
ventas_anuales.rename(columns={"FECHA INICIO": "AÑO", "MONTO": "VENTAS"}, inplace=True)

alpha = st.sidebar.slider("Nivel de Suavización (α)", min_value=0.01, max_value=1.0, value=0.5, step=0.01)
ventas_anuales["PRONOSTICO"] = suavizacion_exponencial(ventas_anuales["VENTAS"].tolist(), alpha)

fig_pronostico_anual = px.line(
    ventas_anuales,
    x="AÑO",
    y=["VENTAS", "PRONOSTICO"],
    title="Pronóstico Anual con Suavización Exponencial",
    labels={"value": "Monto (MXN)", "variable": "Serie"},
    markers=True
)

st.plotly_chart(fig_pronostico_anual, use_container_width=True)

# Sección 6: Distribución por Vendedor
st.markdown("## Análisis por Vendedor")

vendedor_data = (
    filtered_data.groupby("VENDEDOR")["MONTO"].sum().reset_index()
    .sort_values(by="MONTO", ascending=False)
)

fig_vendedor = px.bar(
    vendedor_data,
    x="VENDEDOR",
    y="MONTO",
    title="Montos Totales por Vendedor",
    labels={"MONTO": "Monto (MXN)", "VENDEDOR": "Vendedor"},
    color="MONTO",
    text_auto=True
)

st.plotly_chart(fig_vendedor, use_container_width=True)

# Sección 7: Comentarios y Observaciones
st.markdown("## Comentarios y Observaciones")

comentarios = filtered_data[["CLIENTE", "CONCEPTO", "ESTATUS", "COMENTARIOS"]].copy()
comentarios = comentarios.dropna(subset=["COMENTARIOS"])

st.dataframe(comentarios, use_container_width=True)

# Exportación de Datos Filtrados
st.markdown("## Exportar Datos Filtrados")

def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

data_csv = convertir_csv(filtered_data)
st.download_button(
    label="Descargar Datos Filtrados",
    data=data_csv,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)

# Pie de Página
st.markdown("---")
st.markdown(
    "**Desarrollado por [Tu Nombre o Empresa](https://github.com/usuario/repositorio)** | © 2024"
)
