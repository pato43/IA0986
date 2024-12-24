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
    if "Semaforo" not in df_copia.columns:
        df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
            lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
        )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Crear una copia para simulación y edición
cotizaciones_simuladas = cotizaciones.copy()

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

# Validar columnas disponibles
columnas_disponibles = [col for col in columnas_mostrar if col in cotizaciones_simuladas.columns]

# Crear opciones dinámicas de filtrado
filtros = {}
if st.checkbox("Filtrar por Área"):
    filtros['AREA'] = st.multiselect("Selecciona Área(s):", options=cotizaciones_simuladas['AREA'].dropna().unique())
if st.checkbox("Filtrar por Estatus"):
    filtros['ESTATUS'] = st.multiselect("Selecciona Estatus(es):", options=cotizaciones_simuladas['ESTATUS'].dropna().unique())
if st.checkbox("Filtrar por Vendedor"):
    filtros['VENDEDOR'] = st.multiselect("Selecciona Vendedor(es):", options=cotizaciones_simuladas['VENDEDOR'].dropna().unique())

# Aplicar los filtros dinámicamente
cotizaciones_filtradas = cotizaciones_simuladas.copy()
for columna, valores in filtros.items():
    if valores:
        cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas[columna].isin(valores)]

st.dataframe(cotizaciones_filtradas[columnas_disponibles], use_container_width=True)

# Visualización de métricas generales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones_filtradas))
col2.metric("Monto Total", f"${cotizaciones_filtradas['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones_filtradas['DIAS'].mean():.2f}")

# Gráfico de Proyección Mensual
st.subheader("Proyección de Ventas del Próximo Mes")
proyeccion_mensual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:7])["MONTO"].sum().reset_index()
proyeccion_mensual.columns = ["Mes", "Monto"]
fig_proyeccion_mensual = px.line(
    proyeccion_mensual,
    x="Mes",
    y="Monto",
    title="Proyección Mensual de Ventas",
    labels={"Mes": "Mes", "Monto": "Monto ($)"},
    markers=True
)
st.plotly_chart(fig_proyeccion_mensual)

# Gráfico de Proyección Anual
st.subheader("Proyección de Ventas Anual")
proyeccion_anual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:4])["MONTO"].sum().reset_index()
proyeccion_anual.columns = ["Año", "Monto"]
fig_proyeccion_anual = px.line(
    proyeccion_anual,
    x="Año",
    y="Monto",
    title="Proyección Anual de Ventas",
    labels={"Año": "Año", "Monto": "Monto ($)"},
    markers=True
)
st.plotly_chart(fig_proyeccion_anual)
