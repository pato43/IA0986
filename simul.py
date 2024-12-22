import streamlit as st
from streamlit_timeline import st_timeline
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión de Cotizaciones", layout="wide")

# Títulos y subtítulos principales
st.title("Dashboard de Gestión de Cotizaciones")
st.markdown("""
    Este dashboard está diseñado para **optimizar la gestión de cotizaciones**, automatizar procesos y brindar una visión clara del desempeño del equipo.
""")

# Definición de estilos personalizados
def custom_css():
    st.markdown(
        """
        <style>
        .stButton > button { 
            background-color: #2ECC71;
            color: white;
            border-radius: 10px;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #27AE60;
        }
        .critical { background-color: #E74C3C; color: white; padding: 8px; border-radius: 5px; text-align: center; }
        .warning { background-color: #F1C40F; color: black; padding: 8px; border-radius: 5px; text-align: center; }
        .success { background-color: #2ECC71; color: white; padding: 8px; border-radius: 5px; text-align: center; }
        </style>
        """,
        unsafe_allow_html=True,
    )

custom_css()

# Sidebar para control de accesos y filtros
st.sidebar.title("Panel de Configuración")
role = st.sidebar.selectbox("Seleccione su rol:", ["Coordinador", "Vendedor", "Supervisor"])

if role == "Vendedor":
    user_name = st.sidebar.text_input("Nombre del vendedor:", "Sebastián")
else:
    user_name = "Administrador"

st.sidebar.markdown(f"### Bienvenido, {user_name}")

# Filtros por estado de las cotizaciones
st.sidebar.header("Filtros")
status_filter = st.sidebar.multiselect(
    "Seleccionar estado:", ["Pendiente", "En proceso", "Enviado", "Aprobado", "Rechazado"], ["Pendiente"]
)

# Simulación de datos
@st.cache_data
def load_data():
    data = {
        "ID": [1, 2, 3, 4, 5],
        "Cliente": ["Cliente A", "Cliente B", "Cliente C", "Cliente D", "Cliente E"],
        "Estado": ["Pendiente", "En proceso", "Enviado", "Aprobado", "Rechazado"],
        "Fecha Creación": [
            datetime.now() - timedelta(days=i * 5) for i in range(5)
        ],
        "Fecha Límite": [
            datetime.now() + timedelta(days=(5 - i) * 2) for i in range(5)
        ],
        "Vendedor": ["Sebastián", "Ramiro", "Antonia", "Sebastián", "Antonia"],
        "Monto": [5000, 10000, 7500, 8000, 12000],
    }
    return pd.DataFrame(data)

data = load_data()

# Filtrar datos por estado seleccionado
data_filtered = data[data["Estado"].isin(status_filter)]

# Visualización de métricas clave
st.header("Indicadores Clave")

col1, col2, col3 = st.columns(3)

with col1:
    total_cotizaciones = len(data)
    st.metric("Total Cotizaciones", total_cotizaciones)

with col2:
    cotizaciones_enviadas = len(data[data["Estado"] == "Enviado"])
    st.metric("Cotizaciones Enviadas", cotizaciones_enviadas)

with col3:
    tasa_exito = (
        len(data[data["Estado"] == "Aprobado"]) / total_cotizaciones * 100
        if total_cotizaciones > 0
        else 0
    )
    st.metric("Tasa de Éxito (%)", f"{tasa_exito:.2f}")

# Sección de Cotizaciones
st.header("Gestión de Cotizaciones")

# Tabla interactiva
st.subheader("Cotizaciones Actuales")

def highlight_status(row):
    if row["Estado"] == "Pendiente":
        return ["background-color: #FAD7A0"] * len(row)
    elif row["Estado"] == "En proceso":
        return ["background-color: #F9E79F"] * len(row)
    elif row["Estado"] == "Aprobado":
        return ["background-color: #A9DFBF"] * len(row)
    elif row["Estado"] == "Rechazado":
        return ["background-color: #E6B0AA"] * len(row)
    return [""] * len(row)

data_display = data_filtered.style.apply(highlight_status, axis=1)
st.write(data_display, unsafe_allow_html=True)

# Botones de Acción
st.subheader("Acciones Rápidas")
col1, col2 = st.columns(2)

with col1:
    if st.button("Agregar Nueva Cotización"):
        st.success("Función para agregar cotizaciones próximamente.")

with col2:
    if st.button("Actualizar Estados"):
        st.info("Función para actualizar estados próximamente.")

# Gráficos de Desempeño
st.header("Gráficos de Desempeño")

data_grouped = data.groupby("Vendedor").agg(
    Total_Cotizaciones=("ID", "count"),
    Monto_Total=("Monto", "sum"),
).reset_index()

fig = px.bar(
    data_grouped,
    x="Vendedor",
    y="Monto_Total",
    color="Vendedor",
    title="Monto Total por Vendedor",
    labels={"Monto_Total": "Monto Total ($)"},
    template="plotly_white",
)
st.plotly_chart(fig, use_container_width=True)

# Fin de la Parte 1
# Continuación del código
# -------------------------------------------------------------------------------

# Timeline interactivo para seguimiento de cotizaciones
st.markdown("### Timeline de Cotizaciones")

# Generar datos ficticios para el timeline
cotizaciones_timeline = [
    {
        "id": 1,
        "content": "Cotización 1 Enviada",
        "start": "2024-12-01",
        "end": "2024-12-05",
        "className": "green",
    },
    {
        "id": 2,
        "content": "Cotización 2 Pendiente",
        "start": "2024-12-03",
        "end": "2024-12-07",
        "className": "yellow",
    },
    {
        "id": 3,
        "content": "Cotización 3 Rechazada",
        "start": "2024-12-08",
        "end": "2024-12-10",
        "className": "red",
    },
]

# Visualizar el timeline
st_timeline(
    items=cotizaciones_timeline,
    groups=[],
    options={
        "editable": False,
        "stack": True,
        "start": "2024-12-01",
        "end": "2024-12-15",
    },
)

# Simulación y análisis avanzado
st.markdown("### Simulaciones de Cotizaciones")

# Inputs interactivos para simulación
col1, col2 = st.columns(2)
with col1:
    sim_cotizaciones = st.slider(
        "Cantidad de cotizaciones a simular", min_value=10, max_value=100, value=50
    )
with col2:
    probabilidad_exito = st.slider(
        "Probabilidad de éxito (%)", min_value=0, max_value=100, value=50
    )

# Generar simulación de datos
np.random.seed(42)
resultados_simulacion = np.random.choice(
    ["Éxito", "Fracaso"], size=sim_cotizaciones, p=[probabilidad_exito / 100, 1 - probabilidad_exito / 100]
)

# Contar resultados
resultados_contados = pd.DataFrame(
    {"Resultado": ["Éxito", "Fracaso"], "Cantidad": [
        np.sum(resultados_simulacion == "Éxito"),
        np.sum(resultados_simulacion == "Fracaso"),
    ]}
)

# Gráfica de simulación
st.markdown("#### Resultados de la Simulación")
fig_simulacion = px.bar(
    resultados_contados,
    x="Resultado",
    y="Cantidad",
    color="Resultado",
    title="Resultados de la Simulación",
    color_discrete_map={"Éxito": "green", "Fracaso": "red"},
)
st.plotly_chart(fig_simulacion)

# Sección de optimización
st.markdown("### Optimización y Análisis de Desempeño")

# Inputs dinámicos
col1, col2, col3 = st.columns(3)
with col1:
    margen_utilidad = st.number_input(
        "Margen de utilidad esperado (%)", min_value=0.0, max_value=100.0, value=20.0
    )
with col2:
    costos_fijos = st.number_input("Costos fijos ($)", min_value=0.0, value=5000.0)
with col3:
    costos_variables = st.number_input("Costos variables por unidad ($)", min_value=0.0, value=100.0)

# Calcular optimización
ventas_optimales = (costos_fijos / (margen_utilidad / 100)) + costos_variables
st.markdown(f"#### Ventas óptimas para alcanzar el margen deseado: ${ventas_optimales:,.2f}")

# Visualización del rendimiento
datos_rendimiento = pd.DataFrame({
    "Concepto": ["Costos Fijos", "Costos Variables", "Ventas Optimales"],
    "Monto": [costos_fijos, costos_variables, ventas_optimales],
})
fig_rendimiento = px.pie(
    datos_rendimiento,
    names="Concepto",
    values="Monto",
    title="Distribución de Costos y Ventas",
    color_discrete_sequence=["blue", "orange", "green"],
)
st.plotly_chart(fig_rendimiento)

# Feedback y métricas adicionales
st.markdown("### Retroalimentación en Tiempo Real")

# Sección para capturar comentarios
comentario = st.text_area(
    "Escribe tus comentarios sobre el desempeño del equipo o el análisis presentado:"
)
if st.button("Enviar Comentario"):
    st.success("¡Comentario enviado exitosamente!")

# Cierre del dashboard
st.markdown(
    "---\n**Nota**: Este dashboard es un prototipo y está sujeto a mejoras según las necesidades del cliente."
)

# Fin del código
# -------------------------------------------------------------------------------
