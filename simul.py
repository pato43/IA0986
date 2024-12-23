import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Sistema de Gestión de Cotizaciones",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Path fijo al archivo CSV
RUTA_CSV = "ruta/a/tu/archivo/coti.csv"

# Función para cargar el archivo CSV
@st.cache_data
def cargar_datos(ruta_archivo):
    """
    Carga un archivo CSV que contiene las cotizaciones previas.
    Args:
        ruta_archivo (str): Ruta del archivo CSV.
    Returns:
        pd.DataFrame: DataFrame con las cotizaciones.
    """
    try:
        data = pd.read_csv(ruta_archivo)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para registrar una nueva cotización
def registrar_cotizacion(data, nueva_cotizacion):
    """
    Agrega una nueva cotización al DataFrame existente.
    Args:
        data (pd.DataFrame): DataFrame con las cotizaciones actuales.
        nueva_cotizacion (dict): Diccionario con los datos de la nueva cotización.
    Returns:
        pd.DataFrame: DataFrame actualizado con la nueva cotización.
    """
    return data.append(nueva_cotizacion, ignore_index=True)

# Cargar datos iniciales desde el backend
cotizaciones = cargar_datos(RUTA_CSV)

if cotizaciones is not None:
    # Título del dashboard
    st.title("Sistema de Gestión y Automatización de Cotizaciones")

    # Vista general del archivo cargado
    st.subheader("Cotizaciones Actuales")
    st.dataframe(cotizaciones, use_container_width=True)

    # Registro de nueva cotización
    st.subheader("Registrar Nueva Cotización")
    with st.form(key="form_cotizacion"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.selectbox("Área", cotizaciones["Area"].unique(), help="Selecciona el área de la cotización.")
            cliente = st.text_input("Cliente", help="Nombre del cliente.")
            concepto = st.text_input("Concepto", help="Descripción del producto o servicio.")
            monto = st.number_input("Monto", min_value=0.0, help="Monto total de la cotización.")
        with col2:
            clasificacion = st.selectbox("Clasificación", ["A", "AA", "AAA"], help="Clasificación del cliente.")
            vendedor = st.text_input("Vendedor", help="Nombre del vendedor a cargo.")
            fecha_inicio = st.date_input("Fecha de inicio", datetime.today(), help="Fecha de inicio del proyecto.")
            duracion = st.number_input("Duración (días)", min_value=1, help="Duración del proyecto en días.")

        # Botón para guardar la nueva cotización
        submit_button = st.form_submit_button(label="Guardar Cotización")
    
    # Si se presiona el botón de guardar
    if submit_button:
        nueva_cotizacion = {
            "Area": area,
            "Cliente": cliente,
            "Concepto": concepto,
            "Monto": monto,
            "Clasificacion": clasificacion,
            "Vendedor": vendedor,
            "Fecha_Inicio": fecha_inicio.strftime("%Y-%m-%d"),
            "Duracion_Dias": duracion,
            "Estatus": "Pendiente",
            "Avance_Porcentaje": 0
        }
        cotizaciones = registrar_cotizacion(cotizaciones, nueva_cotizacion)
        st.success("¡Nueva cotización registrada exitosamente!")
        
        # Mostrar tabla actualizada
        st.subheader("Cotizaciones Actualizadas")
        st.dataframe(cotizaciones, use_container_width=True)

        # Botón para descargar la tabla actualizada
        st.download_button(
            label="Descargar Cotizaciones Actualizadas",
            data=cotizaciones.to_csv(index=False).encode('utf-8'),
            file_name="cotizaciones_actualizadas.csv",
            mime="text/csv"
        )
else:
    st.error("No se pudo cargar el archivo de cotizaciones. Verifica el path del archivo CSV.")
# Función para actualizar el estado y avance de una cotización
def actualizar_cotizacion(data, indice, avance, estatus):
    """
    Actualiza el avance y el estado de una cotización específica en el DataFrame.
    Args:
        data (pd.DataFrame): DataFrame con las cotizaciones actuales.
        indice (int): Índice de la cotización a actualizar.
        avance (float): Porcentaje de avance.
        estatus (str): Nuevo estatus de la cotización.
    Returns:
        pd.DataFrame: DataFrame actualizado.
    """
    data.at[indice, "Avance_Porcentaje"] = avance
    data.at[indice, "Estatus"] = estatus
    return data

# Mostrar filtros en la barra lateral
st.sidebar.header("Filtros de Cotizaciones")
area_seleccionada = st.sidebar.multiselect("Filtrar por Área", cotizaciones["Area"].unique())
cliente_seleccionado = st.sidebar.text_input("Buscar por Cliente")
vendedor_seleccionado = st.sidebar.text_input("Buscar por Vendedor")
estatus_seleccionado = st.sidebar.multiselect("Filtrar por Estatus", cotizaciones["Estatus"].unique())

# Aplicar filtros al DataFrame
cotizaciones_filtradas = cotizaciones.copy()

if area_seleccionada:
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["Area"].isin(area_seleccionada)]
if cliente_seleccionado:
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["Cliente"].str.contains(cliente_seleccionado, case=False, na=False)]
if vendedor_seleccionado:
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["Vendedor"].str.contains(vendedor_seleccionado, case=False, na=False)]
if estatus_seleccionado:
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["Estatus"].isin(estatus_seleccionado)]

# Mostrar las cotizaciones filtradas
st.subheader("Cotizaciones Filtradas")
st.dataframe(cotizaciones_filtradas, use_container_width=True)

# Resumen general de cotizaciones
st.subheader("Resumen General de Cotizaciones")
col1, col2, col3 = st.columns(3)

with col1:
    total_cotizaciones = len(cotizaciones_filtradas)
    st.metric("Total de Cotizaciones", total_cotizaciones)

with col2:
    monto_total = cotizaciones_filtradas["Monto"].sum()
    st.metric("Monto Total ($)", f"${monto_total:,.2f}")

with col3:
    avance_promedio = cotizaciones_filtradas["Avance_Porcentaje"].mean()
    st.metric("Avance Promedio (%)", f"{avance_promedio:.2f}%" if not pd.isnull(avance_promedio) else "N/A")

# Actualización de cotizaciones existentes
st.subheader("Actualizar Cotización")
with st.form(key="form_actualizar_cotizacion"):
    # Seleccionar cotización a actualizar
    indice_seleccionado = st.selectbox(
        "Selecciona una cotización para actualizar",
        cotizaciones_filtradas.index,
        format_func=lambda x: f"{cotizaciones_filtradas.at[x, 'Cliente']} - {cotizaciones_filtradas.at[x, 'Concepto']}"
    )

    # Campos para actualizar
    nuevo_avance = st.slider("Porcentaje de Avance", 0, 100, int(cotizaciones_filtradas.at[indice_seleccionado, "Avance_Porcentaje"]))
    nuevo_estatus = st.selectbox(
        "Nuevo Estatus",
        ["Pendiente", "En Progreso", "Completado"],
        index=["Pendiente", "En Progreso", "Completado"].index(cotizaciones_filtradas.at[indice_seleccionado, "Estatus"])
    )

    # Botón para guardar cambios
    submit_actualizar = st.form_submit_button(label="Actualizar Cotización")

if submit_actualizar:
    cotizaciones = actualizar_cotizacion(cotizaciones, indice_seleccionado, nuevo_avance, nuevo_estatus)
    st.success("¡Cotización actualizada exitosamente!")

    # Mostrar tabla actualizada
    st.subheader("Cotizaciones Actualizadas")
    st.dataframe(cotizaciones, use_container_width=True)

    # Botón para descargar la tabla actualizada
    st.download_button(
        label="Descargar Cotizaciones Actualizadas",
        data=cotizaciones.to_csv(index=False).encode('utf-8'),
        file_name="cotizaciones_actualizadas.csv",
        mime="text/csv"
    )
