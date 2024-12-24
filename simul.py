import pandas as pd
import streamlit as st
import plotly.express as px

# Ruta del archivo CSV limpio
FILE_PATH = "cleaned_coti.csv"

# Función para cargar y procesar los datos
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Renombrar columnas clave para facilitar su manejo
    df_copia.rename(columns={
        "Monto": "MONTO",
        "Cliente": "CLIENTE",
        "Estatus": "ESTATUS",
        "Fecha_Envio": "FECHA ENVIO",
        "Duracion_Dias": "DIAS",
        "Concepto": "CONCEPTO"
    }, inplace=True)

    # Simular datos faltantes usando los ejemplos proporcionados
    df_copia["AREA"] = df_copia.get("AREA", "General")
    df_copia["CLASIFICACION"] = df_copia.get("CLASIFICACION", "No clasificado")
    df_copia["VENDEDOR"] = df_copia.get("VENDEDOR", "Desconocido")
    df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Agregar ejemplos simulados para columnas faltantes o inconsistentes
ejemplos_simulados = {
    "VENDEDOR": [
        "Ramiro Rodriguez", "Guillermo Damico", "Juan Alvarado", "Eduardo Manzanares", "Juan Jose Sanchez",
        "Antonio Cabrera", "Juan Carlos Hdz", "Luis Carlos Holt", "Daniel Montero", "Carlos Villanueva",
        "Tere", "Judith Echavarria", "Octavio Farias", "Eduardo Teran", "Sebastian Padilla"
    ] * 3,
    "CLASIFICACION": ["AA", "A", "A", "AA", "A", "A", "AA", "A", "AA", "AA"] * 5,
    "AREA": ["Electromecanica", "Construccion", "HVAC", "Construccion", "Electromecanica"] * 9
}
for col, valores in ejemplos_simulados.items():
    if col not in cotizaciones.columns:
        cotizaciones[col] = valores[:len(cotizaciones)]

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard aborda las siguientes problemáticas clave:

1. **Formato unificado para presupuestos y ventas**: Consolida ambos aspectos para automatizar el análisis.
2. **Seguimiento del flujo de cotización**: Monitorea estados, tiempos y responsables en tiempo real.
3. **Integración con Evidence**: Facilita la exportación de datos aprobados para integración.
""")

# Copia para simulación y edición
cotizaciones_simuladas = cotizaciones.copy()

# Crear semáforo para los estados
cotizaciones_simuladas["Semaforo"] = cotizaciones_simuladas["ESTATUS"].apply(
    lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
)

# Sección: Estado general de cotizaciones
st.subheader("Estado General de Cotizaciones")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Esta tabla consolida toda la información relevante para facilitar el análisis dinámico.
""")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]

# Filtros dinámicos
filtros = {}
if st.checkbox("Filtrar por Área"):
    filtros['AREA'] = st.multiselect("Selecciona Área(s):", options=cotizaciones_simuladas['AREA'].unique())
if st.checkbox("Filtrar por Clasificación"):
    filtros['CLASIFICACION'] = st.multiselect("Selecciona Clasificación(es):", options=cotizaciones_simuladas['CLASIFICACION'].unique())
if st.checkbox("Filtrar por Vendedor"):
    filtros['VENDEDOR'] = st.multiselect("Selecciona Vendedor(es):", options=cotizaciones_simuladas['VENDEDOR'].unique())

# Aplicar filtros
cotizaciones_filtradas = cotizaciones_simuladas.copy()
for col, values in filtros.items():
    if values:
        cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas[col].isin(values)]

# Mostrar tabla filtrada
st.dataframe(cotizaciones_filtradas[columnas_mostrar], use_container_width=True)

# Métricas generales
st.subheader("Métricas Generales")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Resuma las métricas clave sobre cotizaciones, presupuestos y ventas.
""")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones_filtradas))
col2.metric("Monto Total", f"${cotizaciones_filtradas['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones_filtradas['DIAS'].mean():.2f}")

# Gráfico de proyección mensual
st.subheader("Proyección de Ventas Mensual")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Proyecta el monto mensual acumulado basado en las cotizaciones actuales.
""")
proyeccion_mensual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:7])["MONTO"].sum().reset_index()
proyeccion_mensual.columns = ["Mes", "Monto"]
fig_proyeccion_mensual = px.line(
    proyeccion_mensual,
    x="Mes",
    y="Monto",
    title="Proyección Mensual de Ventas",
    markers=True
)
st.plotly_chart(fig_proyeccion_mensual)

# Sección: Edición dinámica
st.subheader("Edición Dinámica de Información")
st.markdown("""
**Punto 2: Seguimiento del flujo de cotización**  
Edite información clave de cualquier cotización en tiempo real.
""")
cliente_seleccionado = st.selectbox("Selecciona un cliente:", cotizaciones_simuladas["CLIENTE"].unique())
columna_editar = st.selectbox("Selecciona la columna a editar:", ["MONTO", "ESTATUS", "DIAS", "CONCEPTO"])
nuevo_valor = st.text_input("Ingresa el nuevo valor:")
if st.button("Aplicar Cambios"):
    try:
        if columna_editar in ["MONTO", "DIAS"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones_simuladas.loc[cotizaciones_simuladas["CLIENTE"] == cliente_seleccionado, columna_editar] = nuevo_valor
        st.success("¡Los cambios han sido aplicados exitosamente!")
    except ValueError:
        st.error("El valor ingresado no es válido para la columna seleccionada.")
