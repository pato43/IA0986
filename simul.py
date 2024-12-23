import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Title and Sidebar Configuration
st.set_page_config(page_title="Dashboard de Cotizaciones", layout="wide")
st.sidebar.title("Configuración del Dashboard")
st.sidebar.markdown("Selecciona las opciones para filtrar los datos:")

# Load Data from GitHub Repository
GITHUB_URL = "<https://github.com/pato43/IA0986/raw/refs/heads/main/tablas%20ordenadas%20.csv>"
st.sidebar.markdown(f"[Fuente de datos en GitHub]({GITHUB_URL})")

@st.cache_data
def load_data():
    """Carga los datos desde un repositorio de GitHub."""
    data = pd.read_excel(GITHUB_URL)
    data.columns = data.columns.str.strip()  # Remove leading/trailing spaces
    return data

data = load_data()

# Columns Overview
columns_overview = {
    "AREA": "Categoría o tipo de proyecto.",
    "CLIENTE": "Cliente asociado al proyecto.",
    "CONCEPTO": "Descripción del trabajo o proyecto.",
    "CLASIFICACION": "Nivel del proyecto (A, AA, AAA).",
    "VENDEDOR": "Persona responsable de la cotización.",
    "FECHA INICIO": "Fecha de inicio del proyecto.",
    "DIAS": "Duración del proyecto (estimada o real).",
    "FECHA ENVIO": "Fecha en que se envía el proyecto.",
    "MONTO": "Monto de la cotización en pesos.",
    "ESTATUS": "Estado actual del proyecto (pendiente, completado).",
    "AVANCE%": "Progreso del proyecto en porcentaje.",
    "Pronostico con metodo de suavizacion exponencial": "Estimación de ventas basada en datos históricos.",
    "Cotizado del mes": "Monto cotizado durante un mes específico.",
    "PRONOSTICO X AREA": "Estimaciones basadas en áreas específicas.",
    "N° de cotizaciones realizadas": "Total de cotizaciones generadas."
}

# Display Data Overview
st.markdown("## Vista General de los Datos")
with st.expander("Detalles de columnas"):
    for col, desc in columns_overview.items():
        st.markdown(f"**{col}**: {desc}")

# Sidebar Filters
selected_area = st.sidebar.multiselect(
    "Selecciona el área:",
    options=data["AREA"].unique(),
    default=data["AREA"].unique()
)

selected_vendedor = st.sidebar.multiselect(
    "Selecciona el vendedor:",
    options=data["VENDEDOR"].unique(),
    default=data["VENDEDOR"].unique()
)

selected_client = st.sidebar.multiselect(
    "Selecciona el cliente:",
    options=data["CLIENTE"].unique(),
    default=data["CLIENTE"].unique()
)

# Filter Data Based on Selections
filtered_data = data[
    (data["AREA"].isin(selected_area)) &
    (data["VENDEDOR"].isin(selected_vendedor)) &
    (data["CLIENTE"].isin(selected_client))
]

# Display Filtered Data
st.markdown("### Datos Filtrados")
st.dataframe(filtered_data)

# Section 1: Cotizaciones y Montos por Área
st.markdown("## Cotizaciones y Montos por Área")
area_summary = (
    filtered_data.groupby("AREA")["MONTO"].sum().reset_index().sort_values(by="MONTO", ascending=False)
)

fig_area = px.bar(
    area_summary,
    x="AREA",
    y="MONTO",
    title="Monto Total Cotizado por Área",
    labels={"MONTO": "Monto (MXN)", "AREA": "Área"},
    text_auto=True,
    color="MONTO",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_area, use_container_width=True)

# Section 2: Pronóstico de Ventas (Suavización Exponencial)
st.markdown("## Pronóstico de Ventas Mensual (Suavización Exponencial)")

# Extract Pronóstico Data
forecast_data = filtered_data[["FECHA INICIO", "Pronostico con metodo de suavizacion exponencial"]]
forecast_data["FECHA INICIO"] = pd.to_datetime(forecast_data["FECHA INICIO"], errors="coerce")
forecast_data = forecast_data.dropna(subset=["FECHA INICIO", "Pronostico con metodo de suavizacion exponencial"])
forecast_data = forecast_data.groupby(forecast_data["FECHA INICIO"].dt.to_period("M")).sum().reset_index()
forecast_data["FECHA INICIO"] = forecast_data["FECHA INICIO"].dt.to_timestamp()

fig_forecast = px.line(
    forecast_data,
    x="FECHA INICIO",
    y="Pronostico con metodo de suavizacion exponencial",
    title="Pronóstico de Ventas Mensual",
    labels={"FECHA INICIO": "Fecha", "Pronostico con metodo de suavizacion exponencial": "Monto Pronosticado (MXN)"},
    markers=True
)

st.plotly_chart(fig_forecast, use_container_width=True)

# Section 3: Avance de Proyectos y Control de Colores
st.markdown("## Avance de Proyectos y Control de Colores")

# Define Colors Based on Progress
def assign_status_color(avance):
    if avance < 50:
        return "Rojo"
    elif avance < 100:
        return "Amarillo"
    else:
        return "Verde"

filtered_data["Estatus Color"] = filtered_data["AVANCE%"].apply(assign_status_color)

color_summary = (
    filtered_data.groupby("Estatus Color")["CONCEPTO"].count().reset_index()
)
color_summary.columns = ["Estatus", "Proyectos"]

fig_colors = px.pie(
    color_summary,
    values="Proyectos",
    names="Estatus",
    title="Distribución de Proyectos por Estatus de Color",
    color="Estatus",
    color_discrete_map={"Rojo": "red", "Amarillo": "yellow", "Verde": "green"}
)

st.plotly_chart(fig_colors, use_container_width=True)

# Additional Notes
st.sidebar.info("Puedes ajustar los filtros para explorar diferentes segmentos de datos.")
# Section 4: Análisis de Cotizaciones por Vendedor
st.markdown("## Análisis de Cotizaciones por Vendedor")

vendedor_summary = (
    filtered_data.groupby("VENDEDOR")["MONTO"].sum().reset_index().sort_values(by="MONTO", ascending=False)
)

fig_vendedor = px.bar(
    vendedor_summary,
    x="VENDEDOR",
    y="MONTO",
    title="Monto Total Cotizado por Vendedor",
    labels={"MONTO": "Monto (MXN)", "VENDEDOR": "Vendedor"},
    text_auto=True,
    color="MONTO",
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig_vendedor, use_container_width=True)

# Section 5: Distribución de Duración de Proyectos
st.markdown("## Distribución de Duración de Proyectos")

fig_duracion = px.histogram(
    filtered_data,
    x="DIAS",
    nbins=20,
    title="Distribución de la Duración de Proyectos",
    labels={"DIAS": "Duración (días)"},
    color_discrete_sequence=["teal"]
)

st.plotly_chart(fig_duracion, use_container_width=True)

# Section 6: Pronóstico Anual con Suavización Exponencial
st.markdown("## Pronóstico Anual con Suavización Exponencial")

annual_forecast_data = filtered_data[["FECHA INICIO", "Pronostico con metodo de suavizacion exponencial"]]
annual_forecast_data["FECHA INICIO"] = pd.to_datetime(annual_forecast_data["FECHA INICIO"], errors="coerce")
annual_forecast_data = annual_forecast_data.dropna(subset=["FECHA INICIO", "Pronostico con metodo de suavizacion exponencial"])
annual_forecast_data = annual_forecast_data.groupby(annual_forecast_data["FECHA INICIO"].dt.year).sum().reset_index()
annual_forecast_data.columns = ["Año", "Monto Pronosticado"]

fig_annual_forecast = px.bar(
    annual_forecast_data,
    x="Año",
    y="Monto Pronosticado",
    title="Pronóstico Anual de Ventas",
    labels={"Año": "Año", "Monto Pronosticado": "Monto Pronosticado (MXN)"},
    text_auto=True,
    color="Monto Pronosticado",
    color_continuous_scale="Plasma"
)

st.plotly_chart(fig_annual_forecast, use_container_width=True)

# Section 7: Comparación de Clasificaciones
st.markdown("## Comparación de Clasificaciones")

clasificacion_summary = (
    filtered_data.groupby("CLASIFICACION")["MONTO"].sum().reset_index().sort_values(by="MONTO", ascending=False)
)

fig_clasificacion = px.pie(
    clasificacion_summary,
    values="MONTO",
    names="CLASIFICACION",
    title="Distribución de Montos por Clasificación",
    color="CLASIFICACION",
    color_discrete_sequence=px.colors.qualitative.Set2
)

st.plotly_chart(fig_clasificacion, use_container_width=True)

# Section 8: Control de Progreso por Cliente
st.markdown("## Control de Progreso por Cliente")

client_progress = filtered_data.groupby("CLIENTE")["AVANCE%"].mean().reset_index()
client_progress = client_progress.sort_values(by="AVANCE%", ascending=False)

fig_client_progress = px.bar(
    client_progress,
    x="CLIENTE",
    y="AVANCE%",
    title="Progreso Promedio por Cliente",
    labels={"AVANCE%": "Avance (%)", "CLIENTE": "Cliente"},
    text_auto=True,
    color="AVANCE%",
    color_continuous_scale="Sunsetdark"
)

st.plotly_chart(fig_client_progress, use_container_width=True)

# Section 9: Métricas Clave
st.markdown("## Métricas Clave")

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Monto Total Cotizado", f"${filtered_data['MONTO'].sum():,.2f}")
metric_col2.metric("Proyectos Activos", f"{len(filtered_data)}")
metric_col3.metric("Avance Promedio", f"{filtered_data['AVANCE%'].mean():.2f}%")

# Section 10: Exportar Datos
st.markdown("## Exportar Datos")

@st.cache_data
def convert_df(df):
    """Convierte un DataFrame a CSV para su descarga."""
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df(filtered_data)
st.download_button(
    label="Descargar datos filtrados como CSV",
    data=csv_data,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)

st.success("Dashboard actualizado y operativo.")
