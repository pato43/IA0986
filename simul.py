import pandas as pd
import streamlit as st

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dashboard de Cotizaciones", layout="wide")

# Ruta del archivo CSV limpio
csv_path = "path/to/coti_limpio.csv"

# Cargar datos
@st.cache_data
def cargar_datos(path):
    """
    Carga el archivo CSV y lo convierte en un DataFrame.
    Args:
        path (str): Ruta al archivo CSV.
    Returns:
        pd.DataFrame: DataFrame cargado.
    """
    return pd.read_csv(path)

cotizaciones = cargar_datos(csv_path)

# Convertir columnas clave a tipos adecuados
cotizaciones["Monto"] = pd.to_numeric(cotizaciones["Monto"], errors="coerce")
cotizaciones["Avance_Porcentaje"] = pd.to_numeric(cotizaciones["Avance_Porcentaje"], errors="coerce")

# Encabezado del dashboard
st.title("Dashboard de Cotizaciones")
st.markdown("Visualización y gestión de cotizaciones con estados automatizados y notas personalizadas.")

# Agregar sistema de colores para el estado de las cotizaciones
def asignar_color(avance):
    """
    Asigna un color según el avance de la cotización.
    Args:
        avance (float): Porcentaje de avance de la cotización.
    Returns:
        str: Nombre del color.
    """
    if avance >= 75:
        return "🟢 Verde"
    elif 50 <= avance < 75:
        return "🟡 Amarillo"
    else:
        return "🔴 Rojo"

cotizaciones["Color_Estado"] = cotizaciones["Avance_Porcentaje"].apply(asignar_color)

# Visualización de datos principales
st.subheader("Tabla de Cotizaciones con Estado")
st.write("Visualiza las cotizaciones con un sistema de colores basado en su avance.")
st.dataframe(
    cotizaciones[["Cliente", "Concepto", "Monto", "Avance_Porcentaje", "Estatus", "Color_Estado"]],
    use_container_width=True
)

# Notas adicionales
st.subheader("Agregar Notas a Cotizaciones")
with st.form(key="form_notas"):
    seleccion_cliente = st.selectbox(
        "Selecciona un cliente",
        cotizaciones["Cliente"].unique()
    )
    nota = st.text_area("Escribe una nota para este cliente")
    submit_nota = st.form_submit_button("Agregar Nota")

    if submit_nota:
        st.success(f"Nota agregada para el cliente: {seleccion_cliente}")
        st.markdown(f"**Nota:** {nota}")

# Visualización adicional: Resumen de tablas esenciales
st.subheader("Resumen General")
col1, col2, col3 = st.columns(3)

with col1:
    total_cotizaciones = len(cotizaciones)
    st.metric("Total de Cotizaciones", total_cotizaciones)

with col2:
    monto_total = cotizaciones["Monto"].sum()
    st.metric("Monto Total", f"${monto_total:,.2f}")

with col3:
    avance_promedio = cotizaciones["Avance_Porcentaje"].mean()
    st.metric("Avance Promedio", f"{avance_promedio:.2f}%")

# Sección para visualización específica
st.subheader("Cotizaciones por Estado")
st.markdown("Visualización de cotizaciones agrupadas según su estado de avance.")
estado_seleccionado = st.radio(
    "Selecciona un estado para visualizar:",
    ["🟢 Verde", "🟡 Amarillo", "🔴 Rojo"]
)
cotizaciones_filtradas = cotizaciones[cotizaciones["Color_Estado"] == estado_seleccionado]
st.dataframe(cotizaciones_filtradas, use_container_width=True)

# Final: Mostrar tabla completa con notas adicionales
st.subheader("Tabla Completa de Cotizaciones")
st.write("Incluye todos los campos del archivo CSV procesado.")
st.dataframe(cotizaciones, use_container_width=True)
# Extensión del Dashboard de Cotizaciones

# Exportar cotizaciones filtradas
st.subheader("Exportar Datos Filtrados")
st.write("Descarga las cotizaciones seleccionadas en un archivo CSV.")

# Seleccionar las columnas a incluir
columnas_seleccionadas = st.multiselect(
    "Selecciona las columnas a exportar:",
    options=cotizaciones.columns.tolist(),
    default=cotizaciones.columns.tolist()
)

# Botón para descargar CSV
if not cotizaciones_filtradas.empty:
    cotizaciones_exportar = cotizaciones_filtradas[columnas_seleccionadas]
    st.download_button(
        label="Descargar CSV Filtrado",
        data=cotizaciones_exportar.to_csv(index=False).encode("utf-8"),
        file_name="cotizaciones_filtradas.csv",
        mime="text/csv"
    )
else:
    st.warning("No hay datos para exportar con los filtros seleccionados.")

# Sección de búsqueda avanzada
st.subheader("Búsqueda Avanzada")
st.write("Encuentra cotizaciones rápidamente utilizando varios criterios.")

# Búsqueda por cliente, concepto o estado
cliente_buscado = st.text_input("Buscar por Cliente", "")
concepto_buscado = st.text_input("Buscar por Concepto", "")
estado_buscado = st.radio(
    "Buscar por Estado",
    ["Todos", "🟢 Verde", "🟡 Amarillo", "🔴 Rojo"],
    index=0
)

# Filtrar datos según búsqueda
datos_filtrados = cotizaciones.copy()
if cliente_buscado:
    datos_filtrados = datos_filtrados[datos_filtrados["Cliente"].str.contains(cliente_buscado, case=False, na=False)]
if concepto_buscado:
    datos_filtrados = datos_filtrados[datos_filtrados["Concepto"].str.contains(concepto_buscado, case=False, na=False)]
if estado_buscado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Color_Estado"] == estado_buscado]

st.write("Resultados de la búsqueda:")
st.dataframe(datos_filtrados, use_container_width=True)

# Sección de edición de datos
st.subheader("Editar Cotizaciones")
st.write("Modifica el monto o el porcentaje de avance de las cotizaciones directamente desde aquí.")

# Selección de fila a editar
cotizacion_editar = st.selectbox(
    "Selecciona una cotización para editar:",
    options=cotizaciones["Cliente"] + " - " + cotizaciones["Concepto"]
)

# Formulario para editar cotización
fila_editar = cotizaciones.loc[
    cotizaciones["Cliente"] + " - " + cotizaciones["Concepto"] == cotizacion_editar
]
with st.form(key="form_editar"):
    nuevo_monto = st.number_input("Monto", value=fila_editar["Monto"].values[0])
    nuevo_avance = st.number_input("Avance (%)", value=fila_editar["Avance_Porcentaje"].values[0])
    submit_edicion = st.form_submit_button("Guardar Cambios")

    if submit_edicion:
        index = fila_editar.index[0]
        cotizaciones.at[index, "Monto"] = nuevo_monto
        cotizaciones.at[index, "Avance_Porcentaje"] = nuevo_avance
        cotizaciones["Color_Estado"] = cotizaciones["Avance_Porcentaje"].apply(asignar_color)
        st.success("Cotización actualizada correctamente.")
        st.experimental_rerun()

# Tablas dinámicas
st.subheader("Análisis de Cotizaciones")
st.write("Visualiza métricas agrupadas por cliente y estado.")

# Agrupación por cliente
tabla_cliente = cotizaciones.groupby("Cliente").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Cliente", "count")
).reset_index()

st.markdown("### Agrupación por Cliente")
st.dataframe(tabla_cliente, use_container_width=True)

# Agrupación por estado
tabla_estado = cotizaciones.groupby("Color_Estado").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Color_Estado", "count")
).reset_index()

st.markdown("### Agrupación por Estado")
st.dataframe(tabla_estado, use_container_width=True)

# Visualización final
st.markdown("---")
st.write("Este dashboard está diseñado para automatizar la gestión de cotizaciones. Usa las herramientas disponibles para optimizar tus procesos.")
