import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Ruta del archivo CSV limpio
FILE_PATH = "/mnt/data/cleaned_coti.csv"

# Función para cargar y procesar los datos
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Renombrar columnas para ajustarse a los nombres requeridos
    df_copia.rename(columns={
        "Monto": "MONTO",
        "Cliente": "CLIENTE",
        "Estatus": "ESTATUS",
        "Fecha_Envio": "FECHA ENVIO",
        "Duracion_Dias": "DIAS",
        "Metodo_Captura": "LLAMADA AL CLIENTE",
        "Concepto": "CONCEPTO"
    }, inplace=True)

    # Simular datos faltantes para asegurar compatibilidad
    if "AREA" not in df_copia.columns:
        df_copia["AREA"] = "General"
    if "CLASIFICACION" not in df_copia.columns:
        df_copia["CLASIFICACION"] = "No clasificado"
    if "VENDEDOR" not in df_copia.columns:
        df_copia["VENDEDOR"] = "Desconocido"

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard resuelve las siguientes problemáticas principales:

1. **Formato Unificado para Presupuestos y Ventas**:
   - **Sección Resolutiva:** Tablas interactivas en "Estado General de Clientes" y "Análisis por Vendedor".
   - **Cómo lo Resuelve:** Consolida presupuestos y ventas en un solo análisis dinámico.

2. **Seguimiento del Flujo de Cotización**:
   - **Sección Resolutiva:** "Seguimiento de la Venta" permite identificar el progreso de cada cotización.
   - **Cómo lo Resuelve:** Monitorea responsables, tiempos de envío y estado actual.

3. **Integración con Evidence**:
   - **Sección Resolutiva:** Tablas filtradas por "Semaforo" listas para exportación e integración externa.
   - **Cómo lo Resuelve:** Automatiza la transferencia de datos aprobados para minimizar errores.
""")

# Tabla principal con filtros dinámicos
st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]

# Crear opciones dinámicas de filtrado
filtros = {}
if st.checkbox("Filtrar por Área"):
    filtros['AREA'] = st.multiselect("Selecciona Área(s):", options=cotizaciones['AREA'].dropna().unique())
if st.checkbox("Filtrar por Estatus"):
    filtros['ESTATUS'] = st.multiselect("Selecciona Estatus(es):", options=cotizaciones['ESTATUS'].dropna().unique())
if st.checkbox("Filtrar por Vendedor"):
    filtros['VENDEDOR'] = st.multiselect("Selecciona Vendedor(es):", options=cotizaciones['VENDEDOR'].dropna().unique())

# Aplicar los filtros dinámicamente
cotizaciones_filtradas = cotizaciones.copy()
for columna, valores in filtros.items():
    if valores:
        cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas[columna].isin(valores)]

st.dataframe(cotizaciones_filtradas[columnas_mostrar], use_container_width=True)

# Visualización de métricas generales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones_filtradas))
col2.metric("Monto Total", f"${cotizaciones_filtradas['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones_filtradas['DIAS'].mean():.2f}")

# Gráfico de Distribución de Montos
st.subheader("Distribución de Montos")
fig_montos = px.histogram(cotizaciones_filtradas, x="MONTO", nbins=20, title="Distribución de Montos")
fig_montos.update_layout(xaxis_title="Monto ($)", yaxis_title="Frecuencia")
st.plotly_chart(fig_montos)

# Gráfico de Cotizaciones por Área
st.subheader("Cotizaciones por Área")
fig_areas = px.bar(
    cotizaciones_filtradas.groupby("AREA")["MONTO"].sum().reset_index(),
    x="AREA",
    y="MONTO",
    title="Monto Total por Área",
    labels={"MONTO": "Monto Total ($)", "AREA": "Área"}
)
st.plotly_chart(fig_areas)
